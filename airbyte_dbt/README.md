# Airbyte + dbt Core Workspace

This directory isolates data-pipeline assets from the main application code.

## Current State

The first dbt merge flow is now implemented for the CNC agreement use case with these assumptions:

1. Airbyte Google Sheets ingestion is already configured.
2. The Google Sheet `AGREEMENT CNC` lands in `ab_raw.agreement_cnc`.
3. The current historical application film dataset is available in `raw.ric_films`.

Implemented models:

1. `stg_agreement_cnc`: normalization and typing of `ab_raw.agreement_cnc`.
2. `stg_raw_ric_films`: projection of the existing historical film table.
3. `int_agreement_cnc_latest_by_visa`: latest Agreement CNC record per `visa_number`.
4. `mart_cnc_films_for_scraping`: merged dataset used to drive downstream scraping decisions.

The final model keeps both source values and merged values, and exposes operational flags such as:

1. `is_new_film`
2. `has_cnc_payload_change`
3. `should_scrape_allocine`

## Start Here

From repository root, enter this workspace before running setup commands:

```bash
cd airbyte_dbt
```

## Structure

- `airbyte/`: Airbyte-related configuration/assets
- `dbt/`: dbt Core project

Within `dbt/models/`:

1. `staging/`: source normalization
2. `intermediate/`: latest-per-key consolidation
3. `marts/`: published merged dataset for orchestration and scraping

## Runbook

See [infra setup runbook](../docs/runbooks/infra-setup-dbt-core-airbyte-remote-postgres.md) for step-by-step setup and troubleshooting.

## Run the models

From `airbyte_dbt/`:

```bash
set -a
source .env
set +a

dbt build --profile ric --project-dir dbt --select +mart_cnc_films_for_scraping
```

This builds the staging, intermediate, and final merge model.
