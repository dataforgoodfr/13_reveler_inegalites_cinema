#!/usr/bin/env bash
set -euo pipefail

POOL_NAME="ingestion-pool"
FLOWS_FILE="/app/ingestion/prefect/flows.py"

delete_deployment_if_exists() {
  local deployment_name="$1"
  prefect deployment delete "$deployment_name" >/tmp/prefect-deployment-delete.log 2>&1 || true
}

prefect work-pool create "${POOL_NAME}" --type process --overwrite >/tmp/prefect-work-pool.log 2>&1 || {
  cat /tmp/prefect-work-pool.log
  exit 1
}

delete_deployment_if_exists "Synchroniser les sources/synchroniser-les-sources"
delete_deployment_if_exists "Preparer les donnees/preparer-les-donnees"
delete_deployment_if_exists "Recuperer les donnees Allocine/recuperer-les-donnees-allocine"
delete_deployment_if_exists "Finaliser les donnees/finaliser-les-donnees"

prefect deploy "${FLOWS_FILE}:main_ingestion_flow" \
  --name "lancer-ingestion-donnees" \
  --description "Execution manuelle du pipeline d'ingestion complet avec etapes optionnelles Airbyte et dbt final." \
  --pool "${POOL_NAME}" >/tmp/prefect-deploy-main.log 2>&1 || {
  cat /tmp/prefect-deploy-main.log
  exit 1
}

exec prefect worker start --pool "${POOL_NAME}" --type process
