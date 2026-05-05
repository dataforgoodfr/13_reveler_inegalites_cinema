Owner: Joel Teixeira

Last reviewed: 2026-04-30

Status: active

# Reproducible Infra Setup - Airbyte OSS + dbt Core with Remote Postgres

## 1. Purpose

This runbook standardizes how developers set up and run:

1. Airbyte OSS (self-hosted)
2. dbt Core
3. Remote PostgreSQL environments (`test` and `prod` on separate machines)

Goal: every developer gets the same setup, same commands, and same expected behavior.

This document is operational. It owns setup commands, environment variables, validation steps, and troubleshooting. Data contracts are documented in the specification; migration sequencing is documented in the architecture plan.

## 2. Standard Topology (for all developers)

Use this topology in all environments:

1. Airbyte OSS runs on developer machine (local, via `abctl`) for development/testing workflows.
2. dbt Core runs on developer machine (Python virtual environment).
3. PostgreSQL is remote or local:
   - `test` Postgres machine
   - `prod` Postgres machine
   - (optional) local Postgres for isolated testing, but not required.
4. Environment selection (`test` or `prod`) is done only by values set in `POSTGRES_*` variables.
5. Repository layout is standardized:
   - `ingestion/airbyte` for Airbyte assets
   - `ingestion/dbt` for dbt assets

### This is reproducible

Consistency is enforced by:

1. Fixed tool versions.
2. Single environment-variable contract.
3. Same schema and role naming convention across environments.
4. Same dbt profile structure.
5. Same Airbyte naming conventions for sources/connections.

## 3. Working Directory (mandatory first step)

By default, developers start in repository root. Before running setup commands in this runbook, move into the dedicated workspace:

```bash
cd ingestion
```

Unless explicitly stated otherwise, commands below assume current directory is `ingestion/`.

## 4. Prerequisites

Required on developer machine:

1. Docker + Docker Compose plugin
2. Python 3.10+
3. `curl`
4. remote access to shared `test` and/or `prod` Postgres database. 
   - Or local Postgres for isolated testing (optional).


## 5. Pre-install Verification

Run prerequisite checks before any installation:

```bash
docker compose version
python3 --version
```


## 6. Environment Variable Contract

Create a local file (not committed) called `.env`. Use `.env.example` as template:

```
cp .env.example .env
```

then fillup missing values.


Set `POSTGRES_*` values to the target environment (`test` or `prod`) before running commands.
Set `AIRBYTE_PORT` to an available local port. Keep `AIRBYTE_URL` aligned with `AIRBYTE_HOST` + `AIRBYTE_PORT`.

Load variables in shell when needed:

```bash
set -a
source .env
set +a
```

## 7. Remote Postgres Preparation (once per environment) [Verify if already done before running]

Run with DBA/admin account on Postgres (adapt database name if needed).

```sql
CREATE USER pipeline_user WITH PASSWORD '<replace>';

GRANT CONNECT ON DATABASE reveler_inegalites_cinema TO pipeline_user;
GRANT CREATE ON DATABASE reveler_inegalites_cinema TO pipeline_user;

CREATE SCHEMA IF NOT EXISTS ab_raw AUTHORIZATION pipeline_user;
CREATE SCHEMA IF NOT EXISTS marts AUTHORIZATION pipeline_user;

GRANT USAGE, CREATE ON SCHEMA ab_raw TO pipeline_user;
GRANT USAGE, CREATE ON SCHEMA marts TO pipeline_user;

-- Required by the partial CNC dbt flow, which reads historical films from raw.ric_films
GRANT USAGE ON SCHEMA raw TO pipeline_user;
GRANT SELECT ON TABLE raw.ric_films TO pipeline_user;
```

If SSL is mandatory, ensure root certificate/trust chain is distributed to developers and configured in client options.

For `prod`, keep canonical schemas (`ab_raw`, `marts`) and restrict write access to CI/CD or approved maintainers.

## 8. Airbyte OSS Setup (developer machine)

### Step 1 - Install `abctl`

Version policy: use the latest stable `abctl` approved by team at onboarding date.

```bash
curl -LsfS https://get.airbyte.com | bash
abctl version
```

### Step 2 - Install local Airbyte

```bash
abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT"
abctl local status
abctl local credentials
```

If no TLS is configured in local environment:

```bash
abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT" --insecure-cookies
```

### Step 3 - Access UI

Open `AIRBYTE_URL` and sign in with credentials from `abctl local credentials`.

## 9. Airbyte Connection Setup (reproducible steps)

Requires Google Sheets sources to be already created and shared with service account email.

### Step 0 - Configure GCP service account 

1. Create a new project in GCP or use existing one.
2. Allow Google Sheets API for the project.
3. Create a service account with "Viewer" role.
4. Create and download a JSON key for the service account.
5. Share sheets with service-account email in read access.

### Step 1 - Create sources

1. Create Google Sheets source `src_gsheet_agreement_cnc`
2. Create Google Sheets source `src_gsheet_modification_data`
3. Use service account authentication

### Step 2 - Create Postgres destination

Create destination `dst_pg` with:

1. Host: `${POSTGRES_HOST}`
2. Port: `${POSTGRES_PORT}`
3. Database: `${POSTGRES_DB}`
4. User/password: `${POSTGRES_USER}` / `${POSTGRES_PASSWORD}`
5. Default schema: `${AB_RAW_SCHEMA}`
6. SSL mode: `${POSTGRES_SSLMODE}` (set when required by your Postgres server)

### Step 3 - Create connections

1. `cnx_agreement_cnc_to_pg`
2. `cnx_modification_data_to_pg`

Recommended defaults:

1. Schedule: hourly (or nightly, align with business SLA)
2. Normalize names to SQL-compliant columns
3. Enable notifications on sync failure

### Step 4 - First sync validation

After first sync, confirm raw data in configured Postgres database:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = '<your_raw_schema>'
ORDER BY table_name;
```

## 10. dbt Core Setup (developer machine)

### Step 1 - Create isolated environment

Version policy: pin `dbt-core==1.11.7` and `dbt-postgres==1.10.0`.

```bash
python3 -m venv .venv-dbt
source .venv-dbt/bin/activate
python -m pip install --upgrade pip
python -m pip install "dbt-core==1.11.7" "dbt-postgres==1.10.0"
dbt --version
```

### Step 2 - Validate dbt project files (git versioned)

```bash
test -f dbt/dbt_project.yml
```

If this check fails, pull the branch/repository content that includes the dbt project before continuing.

### Step 3 - Configure `~/.dbt/profiles.yml`

```yaml
ric:
  target: default
  outputs:
    default:
      type: postgres
      host: "{{ env_var('POSTGRES_HOST') }}"
      port: "{{ env_var('POSTGRES_PORT') | int }}"
      user: "{{ env_var('POSTGRES_USER') }}"
      password: "{{ env_var('POSTGRES_PASSWORD') }}"
      dbname: "{{ env_var('POSTGRES_DB') }}"
      schema: "{{ env_var('DBT_SCHEMA', 'marts') }}"
      threads: "{{ env_var('DBT_THREADS', '4') | int }}"
      sslmode: "{{ env_var('POSTGRES_SSLMODE', 'disable') }}"
```

Use `POSTGRES_SSLMODE=require` only if your Postgres server supports/requires SSL.

### Step 4 - Validate connectivity

```bash
# Run from `ingestion/`
set -a
source .env
set +a

test -f dbt/dbt_project.yml
dbt debug --profile ric --project-dir dbt
```

If you are already inside `ingestion/dbt`, load env with `source ../.env` and run `dbt debug --profile ric`.

### Step 5 - Run transforms and tests

```bash
dbt deps --project-dir dbt
dbt build --profile ric --project-dir dbt
```

## 11. Daily Developer Workflow (same experience)

Every developer follows this order:

1. Set `POSTGRES_*` values in `.env` for the environment you want to target (`test` or `prod`).
2. Reload env vars (`set -a; source .env; set +a`).
3. Ensure Airbyte local is running (`abctl local status`).
4. Trigger or wait for Airbyte sync to the configured Postgres DB.
5. Run `dbt build --profile ric  --project-dir dbt`.
6. Validate marts consumed by backend/BI in the targeted environment.

## 12. Environment Switch (test <-> prod)

To switch environment, only update PostgreSQL connection values:

1. Edit `.env` and set `POSTGRES_*` to the target database (`test` or `prod`).
2. Reload environment variables (`set -a; source .env; set +a`).
3. Keep schemas and contracts identical across environments (`ab_raw`, `marts`).
4. Keep production writes restricted to approved maintainers/automation.

## 13. Reproducibility Checklist for Onboarding

A new developer setup is valid only if all checks pass:

1. `abctl version` matches team-approved version.
2. `dbt --version` shows `1.11.7` core + postgres adapter.
3. Airbyte can sync both Google Sheets sources to `${AB_RAW_SCHEMA}` in configured DB.
4. `dbt debug --profile ric  --project-dir dbt` succeeds.
5. `dbt build --profile ric  --project-dir dbt` succeeds.
6. At least one model is queryable in `${DBT_SCHEMA}` in configured DB.

## 14. Common Issues

1. Airbyte install fails with `error verifying port availability: port 8000 is already in use`:
   - Check candidate port availability: `ss -ltn "( sport = :8001 )"`.
   - Set a free port in `.env` (example: `AIRBYTE_PORT=8001`, `AIRBYTE_URL=http://localhost:8001`).
   - Re-run install: `abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT"`.
2. SSL handshake failure:
   - If error says `server does not support SSL, but SSL was required`, set `POSTGRES_SSLMODE=disable`.
   - If SSL is required by server, use `POSTGRES_SSLMODE=require` and verify certificate chain.
3. Permission denied on schema/table:
   - Re-run grants/default privileges from Section 7.
4. Airbyte connection green but no rows:
   - Verify spreadsheet sharing to service-account identity.

## 15. References

1. Airbyte OSS quickstart: https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart
2. Airbyte `abctl`: https://docs.airbyte.com/platform/deploying-airbyte/abctl
3. Airbyte destination Postgres: https://docs.airbyte.com/integrations/destinations/postgres
4. dbt Core install: https://docs.getdbt.com/docs/local/install-dbt
5. dbt profiles: https://docs.getdbt.com/docs/local/profiles.yml
6. dbt Postgres setup: https://docs.getdbt.com/docs/local/connect-data-platform/postgres-setup
