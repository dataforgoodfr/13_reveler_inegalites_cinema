# `ops` Schema For Pipeline Monitoring And Safe Triggering

## Metadata du document

**Responsable:** Data Team DataForGood

**Dernière révision:** 2026-05-26

**Statut:** actif

### Historique du document

| # | Date | Auteur | Observations |
| --- | --- | --- | --- |
| 1 | 2026-05-26 | Joel Teixeira | Alignement avec l'implémentation actuelle: poller porté par Prefect, suppression de `requested_extraction_date`, `request_id` généré par PostgreSQL. Clarification des statuts runtime, grants `dbt_user`/`prefect_user`/Metabase et requêtes dashboard |

## Summary

Use a new schema named `ops`.

Why `ops`:
- matches the repo’s short schema naming style: `raw`, `staging`, `intermediate`, `fnl`
- covers both monitoring and controlled operational actions
- cleaner than `admin`, `monitoring`, or `audit`

This schema contains:
- one dbt-built view for Allociné pipeline monitoring
- one request queue table written by a Metabase action button and consumed by a scheduled Prefect flow

The key adjustment: request consumption must be **claim-based and idempotent**, so one Metabase click cannot be executed multiple times by the poller flow.

## Key Changes

### Schema
- Create schema `ops`.
- Grant project-manager Metabase group read/write only as needed for the action model and dashboard.
- Keep standard Metabase users on `fnl` only.

### PostgreSQL: Schema and Table Creation

**1. Create the `ops` schema:**

```sql
CREATE SCHEMA IF NOT EXISTS ops;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

**2. Create the `ingestion_run_requests` table:**

```sql
CREATE TABLE IF NOT EXISTS ops.ingestion_run_requests (
  request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requested_at TIMESTAMP NOT NULL DEFAULT now(),
  requested_by_metabase_user TEXT NOT NULL,
  requested_by_metabase_group TEXT,
  request_source TEXT NOT NULL DEFAULT 'metabase',
  request_status TEXT NOT NULL DEFAULT 'pending',
  claimed_at TIMESTAMP,
  claimed_by TEXT,
  processed_at TIMESTAMP,
  triggered_flow_run_id TEXT,
  trigger_error TEXT,
  dedupe_key TEXT NOT NULL
);
```

**3. Add indexes:**

```sql
-- For efficient polling by status and time
CREATE INDEX IF NOT EXISTS idx_ingestion_run_requests_status_requested_at
  ON ops.ingestion_run_requests (request_status, requested_at ASC);

-- Unique dedupe key for active requests (partial index)
DROP INDEX IF EXISTS ops.idx_ingestion_run_requests_dedupe_key_active;

CREATE UNIQUE INDEX idx_ingestion_run_requests_dedupe_key_active
  ON ops.ingestion_run_requests (dedupe_key)
  WHERE request_status IN ('pending', 'processing');

ALTER TABLE ops.ingestion_run_requests
  ALTER COLUMN request_id SET DEFAULT gen_random_uuid();

ALTER TABLE ops.ingestion_run_requests
  DROP COLUMN IF EXISTS requested_extraction_date;
```

**4. (Reference) Monitoring view creation (dbt-managed):**

```sql
-- This view is built by dbt, but for reference:
CREATE OR REPLACE VIEW ops.v_allocine_pipeline_status AS
SELECT ... -- see dbt model for logic
;
```

### Monitoring view
- Create dbt model materialized as `view` in `ops`, recommended name: `ops.v_allocine_pipeline_status`.
- Build it from cleaned Allociné scrape data, preferably via [stg_allocine_data.sql](/root/explore/13_reveler_inegalites_cinema/ingestion/dbt/models/staging/stg_allocine_data.sql:1).
- Include fields needed by the dashboard:
  - `extracted_date`
  - `extracted_hour`
  - `extracted_ts`
  - `run_id`
  - `cnc_visa`
  - `source_record_id`
  - `scrapping_status`
  - `match_strategy`
  - `record_hash`
  - `error_message` if available
- Keep one row per scrape attempt so the hourly history chart remains correct.

### Request table
- Create table `ops.ingestion_run_requests`.
- Append-only for requests, but lifecycle fields are updated by the Prefect poller flow.
- Recommended columns:
  - `request_id` UUID primary key default `gen_random_uuid()`
  - `requested_at` timestamp not null default now()
  - `requested_by_metabase_user` text not null
  - `requested_by_metabase_group` text nullable
  - `request_source` text not null default `metabase`
  - `request_status` text not null default `pending`
  - `claimed_at` timestamp nullable
  - `claimed_by` text nullable
  - `processed_at` timestamp nullable
  - `triggered_flow_run_id` text nullable
  - `trigger_error` text nullable
  - `dedupe_key` text not null
- Add indexes:
  - `(request_status, requested_at asc)`
  - unique index on `dedupe_key` for active requests only

### Duplicate-prevention and safe execution
- Do not let the poller flow simply “read pending then trigger”.
- Use a **claim step in one SQL update**:
  - select one eligible `pending` row
  - atomically change it to `processing`
  - set `claimed_at` and `claimed_by`
  - return that row
- Only after a successful claim may the poller flow call Prefect.
- When the poller claims a row:
  - set `request_status = 'processing'`
  - set `claimed_at`
  - set `claimed_by`
- After Prefect creates the ingestion run:
  - set `triggered_flow_run_id`
- During the main ingestion flow:
  - keep `request_status = 'processing'`
- If the ingestion flow succeeds:
  - set `request_status = 'success'`
  - set `processed_at`
- If Prefect trigger or ingestion execution fails:
  - set `request_status = 'failed'`
  - set `processed_at`
  - set `trigger_error`
- The poller flow must ignore rows already in `processing`, `success`, or `failed`.

### Dedupe policy
- Prevent duplicate execution from repeated clicks by defining a deterministic `dedupe_key`.
- Recommended v1 key:
  - one active ingestion request per day
  - example: `metabase:YYYY-MM-DD`
- Enforce it with a partial unique index covering only active states:
  - `pending`
  - `processing`
- Result:
  - if a PM clicks multiple times before the first request finishes, only one active request exists
  - later clicks either fail cleanly or can be surfaced in Metabase as “already requested”
- Keep completed history by excluding `success` and `failed` rows from the unique constraint.

### Poller behavior
- A scheduled Prefect flow polls on interval.
- Each run:
  - atomically claim at most one row
  - trigger the main Prefect ingestion deployment once
  - persist terminal state
- In normal runtime, the poller flow should not require DDL privileges on the project database.
- Schema/table initialization can be handled once manually, or by an explicit admin-mode run only.
- If the poller flow crashes after claim but before creating the ingestion flow run:
  - introduce claim timeout handling
  - rows stuck in `processing` longer than threshold and without `triggered_flow_run_id` can be requeued by explicit maintenance logic, not automatically on every poll
- Recommended claim timeout field/logic:
  - `claimed_at`
  - requeue only if `claimed_at` older than configured threshold and no `triggered_flow_run_id`

### Metabase usage
- Dashboard cards read from `ops.v_allocine_pipeline_status`.
- Metabase action button inserts a request row with the precomputed `dedupe_key`.
- Restrict dashboard/model/collection access to PM group.
- Ensure `All Users` does not have broader access than PM-only operational content.

Recommended action-model insert query:

```sql
INSERT INTO ops.ingestion_run_requests (
  requested_by_metabase_user,
  requested_by_metabase_group,
  request_source,
  dedupe_key
)
SELECT
  {{email}},
  'C5050_Ops',
  'metabase',
  CONCAT('metabase:', CURRENT_DATE::TEXT)
WHERE NOT EXISTS (
  SELECT 1
  FROM ops.ingestion_run_requests
  WHERE dedupe_key = CONCAT('metabase:', CURRENT_DATE::TEXT)
    AND request_status IN ('pending', 'processing', 'triggered')
);
```

Notes:
- `request_id`, `requested_at` and `request_status` use database defaults.
- This `dedupe_key` implements the v1 rule: one active request per day.
- The query inserts one row only when no active request already exists for the same `dedupe_key`.
- `triggered` is kept in the guard only as a legacy active status during migration; new runs use `processing`.

## Dashboard Mapping

### Cards from `ops.v_allocine_pipeline_status`
- Donut:
  - distinct `cnc_visa` count by `scrapping_status`
  - filtered by `extracted_date`
- Hourly stacked bars:
  - distinct `cnc_visa` count
  - grouped by `extracted_hour` and `scrapping_status`
  - filtered by `extracted_date`
- Failure table:
  - rows where `scrapping_status != 'success'`
  - columns:
    - `extracted_ts`
    - `scrapping_status`
    - `error_message`

### Permissions

Use existing users when already created. Grants expected by implementation:

```sql
-- dbt builds ops.v_allocine_pipeline_status
GRANT USAGE, CREATE ON SCHEMA ops TO dbt_user;
GRANT SELECT ON ALL TABLES IN SCHEMA staging TO dbt_user;

-- Metabase reads dashboard and inserts trigger requests
GRANT USAGE ON SCHEMA ops TO metabase_user;
GRANT SELECT ON ops.v_allocine_pipeline_status TO metabase_user;
GRANT INSERT ON ops.ingestion_run_requests TO metabase_user;
GRANT SELECT ON ops.ingestion_run_requests TO metabase_user;

-- Prefect dispatcher and main flow claim/update lifecycle
GRANT USAGE ON SCHEMA ops TO prefect_user;
GRANT SELECT, UPDATE ON ops.ingestion_run_requests TO prefect_user;
```

Restrict default access:

```sql
REVOKE ALL ON SCHEMA ops FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA ops FROM PUBLIC;
```

### Filter behavior
- Primary dashboard filter: `extracted_date`
- Default: today
- Apply same filter to all cards

## Test Plan

- dbt model test:
  - schema builds into `ops`
  - expected columns exist
  - `extracted_date` and `extracted_hour` derive correctly
- Queue safety tests:
  - two workers polling concurrently can claim at most one same request
  - repeated button clicks with same active `dedupe_key` do not create multiple executable requests
  - poller never triggers Prefect for rows not successfully claimed
- Failure-path tests:
  - failed Prefect trigger updates row to `failed`
  - processing-but-untriggered stale row can be safely requeued only by timeout logic
- Permissions tests:
  - standard users cannot see `ops`
  - PM group can see dashboard and run action
  - `All Users` does not accidentally inherit access

## Assumptions

- `ops` is the approved schema name.
- Monitoring is Allociné-only for v1.
- History view should show all scrape attempts for the selected day.
- Queue semantics are single-trigger, no manual approval workflow.
- v1 allows only one active ingestion request at a time for the chosen dedupe scope.
