import argparse
import asyncio
import os
import socket
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import psycopg
from prefect import flow, get_run_logger
from prefect.client.orchestration import get_client
from psycopg.rows import dict_row

from ingestion.airbyte.client import ensure_workspace_id
from ingestion.airbyte.client import extract_job_id
from ingestion.airbyte.client import extract_job_status
from ingestion.airbyte.client import find_by_name
from ingestion.airbyte.client import find_running_job_for_connection
from ingestion.airbyte.client import get_access_token
from ingestion.airbyte.client import get_api_base_url
from ingestion.airbyte.client import get_job
from ingestion.airbyte.client import is_failed_job_status
from ingestion.airbyte.client import is_running_job_status
from ingestion.airbyte.client import is_success_job_status
from ingestion.airbyte.client import list_connections
from ingestion.airbyte.client import trigger_sync


REPO_ROOT = Path("/app")
DBT_PROJECT_DIR = REPO_ROOT / "ingestion" / "dbt"
ALLOCINE_CONFIG_PATH = (
    REPO_ROOT / "ingestion" / "scraping" / "allocine" / "config.json"
)
ALLOCINE_MAIN_PATH = REPO_ROOT / "ingestion" / "scraping" / "allocine" / "main.py"
DEFAULT_AIRBYTE_SYNC_TIMEOUT_SECONDS = int(
    os.getenv("AIRBYTE_SYNC_TIMEOUT_SECONDS", "3600")
)
DEFAULT_AIRBYTE_SYNC_POLL_SECONDS = int(
    os.getenv("AIRBYTE_SYNC_POLL_SECONDS", "10")
)
REQUEST_TABLE_NAME = "ops.ingestion_run_requests"
DEFAULT_MAIN_DEPLOYMENT_NAME = "Lancer l'ingestion complete/lancer-ingestion-donnees"
DEFAULT_REQUEST_FLOW_RUN_NAME_PREFIX = "metabase-ingestion"
CREATE_QUEUE_SQL = """
CREATE SCHEMA IF NOT EXISTS ops;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

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

CREATE INDEX IF NOT EXISTS idx_ingestion_run_requests_status_requested_at
  ON ops.ingestion_run_requests (request_status, requested_at ASC);

DROP INDEX IF EXISTS ops.idx_ingestion_run_requests_dedupe_key_active;

CREATE UNIQUE INDEX idx_ingestion_run_requests_dedupe_key_active
  ON ops.ingestion_run_requests (dedupe_key)
  WHERE request_status IN ('pending', 'processing');

ALTER TABLE ops.ingestion_run_requests
  ALTER COLUMN request_id SET DEFAULT gen_random_uuid();

ALTER TABLE ops.ingestion_run_requests
  DROP COLUMN IF EXISTS requested_extraction_date;
"""


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None) -> list[str]:
    if value is None:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class IngestionRequestSettings:
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    claim_timeout_seconds: int
    claimed_by: str
    main_deployment_name: str
    config_path: str
    flow_run_name_prefix: str
    auto_init_queue_schema: bool
    run_airbyte_sync_step: bool
    run_dbt_phase_2_step: bool
    airbyte_connection_names: list[str]

    @classmethod
    def from_env(cls) -> "IngestionRequestSettings":
        settings = cls(
            database_host=os.getenv("POSTGRES_HOST", ""),
            database_port=int(os.getenv("POSTGRES_PORT", "5432")),
            database_name=os.getenv("POSTGRES_DB", ""),
            database_user=os.getenv("INGESTION_REQUEST_POSTGRES_USER", "prefect_user"),
            database_password=os.getenv(
                "INGESTION_REQUEST_POSTGRES_PASSWORD",
                "",
            ),
            claim_timeout_seconds=int(
                os.getenv("INGESTION_REQUEST_CLAIM_TIMEOUT_SECONDS", "3600")
            ),
            claimed_by=os.getenv(
                "INGESTION_REQUEST_CLAIMED_BY",
                socket.gethostname() or "prefect-worker",
            ),
            main_deployment_name=os.getenv(
                "INGESTION_REQUEST_MAIN_DEPLOYMENT_NAME",
                DEFAULT_MAIN_DEPLOYMENT_NAME,
            ),
            config_path=os.getenv(
                "INGESTION_REQUEST_ALLOCINE_CONFIG_PATH",
                str(ALLOCINE_CONFIG_PATH),
            ),
            flow_run_name_prefix=os.getenv(
                "INGESTION_REQUEST_FLOW_RUN_NAME_PREFIX",
                DEFAULT_REQUEST_FLOW_RUN_NAME_PREFIX,
            ),
            auto_init_queue_schema=_parse_bool(
                os.getenv("INGESTION_REQUEST_AUTO_INIT_QUEUE_SCHEMA"),
                default=False,
            ),
            run_airbyte_sync_step=_parse_bool(
                os.getenv("INGESTION_REQUEST_RUN_AIRBYTE_SYNC_STEP"),
                default=False,
            ),
            run_dbt_phase_2_step=_parse_bool(
                os.getenv("INGESTION_REQUEST_RUN_DBT_PHASE_2_STEP"),
                default=False,
            ),
            airbyte_connection_names=_parse_csv(
                os.getenv("INGESTION_REQUEST_AIRBYTE_CONNECTION_NAMES")
            ),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        required = {
            "POSTGRES_HOST": self.database_host,
            "POSTGRES_DB": self.database_name,
            "INGESTION_REQUEST_POSTGRES_USER": self.database_user,
            "INGESTION_REQUEST_POSTGRES_PASSWORD": self.database_password,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required ingestion request environment variables: {', '.join(missing)}"
            )
        if self.run_airbyte_sync_step and not self.airbyte_connection_names:
            raise ValueError(
                "INGESTION_REQUEST_RUN_AIRBYTE_SYNC_STEP=true requires INGESTION_REQUEST_AIRBYTE_CONNECTION_NAMES."
            )


def _connect_request_db(
    settings: IngestionRequestSettings,
) -> psycopg.Connection[Any]:
    return psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
        row_factory=dict_row,
    )


def _ensure_request_queue(settings: IngestionRequestSettings) -> None:
    if not settings.auto_init_queue_schema:
        return
    with _connect_request_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_QUEUE_SQL)
        connection.commit()


def _claim_next_request(
    settings: IngestionRequestSettings,
) -> dict[str, Any] | None:
    claim_sql = f"""
    WITH candidate AS (
        SELECT request_id
        FROM {REQUEST_TABLE_NAME}
        WHERE request_status = 'pending'
        ORDER BY requested_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    UPDATE {REQUEST_TABLE_NAME} AS requests
    SET
        request_status = 'processing',
        claimed_at = now(),
        claimed_by = %(claimed_by)s
    FROM candidate
    WHERE requests.request_id = candidate.request_id
    RETURNING requests.*;
    """

    with _connect_request_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(claim_sql, {"claimed_by": settings.claimed_by})
            row = cursor.fetchone()
        connection.commit()
        return row


def _mark_request_processing(
    settings: IngestionRequestSettings,
    *,
    request_id: UUID,
    flow_run_id: str | None = None,
) -> None:
    sql = f"""
    UPDATE {REQUEST_TABLE_NAME}
    SET
        request_status = 'processing',
        claimed_at = COALESCE(claimed_at, now()),
        triggered_flow_run_id = COALESCE(%(flow_run_id)s, triggered_flow_run_id),
        trigger_error = NULL
    WHERE request_id = %(request_id)s;
    """

    with _connect_request_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                {
                    "request_id": str(request_id),
                    "flow_run_id": flow_run_id,
                },
            )
        connection.commit()


def _mark_request_failed(
    settings: IngestionRequestSettings,
    *,
    request_id: UUID,
    error_message: str,
) -> None:
    sql = f"""
    UPDATE {REQUEST_TABLE_NAME}
    SET
        request_status = 'failed',
        processed_at = now(),
        trigger_error = %(error_message)s
    WHERE request_id = %(request_id)s;
    """

    with _connect_request_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                {
                    "request_id": str(request_id),
                    "error_message": error_message[:4000],
                },
            )
        connection.commit()


def _mark_request_success(
    settings: IngestionRequestSettings,
    *,
    request_id: UUID,
) -> None:
    sql = f"""
    UPDATE {REQUEST_TABLE_NAME}
    SET
        request_status = 'success',
        processed_at = now(),
        trigger_error = NULL
    WHERE request_id = %(request_id)s;
    """

    with _connect_request_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, {"request_id": str(request_id)})
        connection.commit()


def _requeue_stale_claims(settings: IngestionRequestSettings) -> list[str]:
    sql = f"""
    UPDATE {REQUEST_TABLE_NAME}
    SET
        request_status = 'pending',
        claimed_at = NULL,
        claimed_by = NULL,
        trigger_error = CASE
            WHEN trigger_error IS NULL OR trigger_error = '' THEN
                'Stale processing request requeued by maintenance flow.'
            ELSE
                trigger_error || E'\\nStale processing request requeued by maintenance flow.'
        END
    WHERE request_status = 'processing'
      AND triggered_flow_run_id IS NULL
      AND claimed_at < now() - (%(claim_timeout_seconds)s * interval '1 second')
    RETURNING request_id::text;
    """

    with _connect_request_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                {"claim_timeout_seconds": settings.claim_timeout_seconds},
            )
            rows = cursor.fetchall()
        connection.commit()
        return [row["request_id"] for row in rows]


def _build_request_parameters(
    settings: IngestionRequestSettings,
    *,
    request_id: UUID,
) -> dict[str, object]:
    return {
        "request_id": str(request_id),
        "config_path": settings.config_path,
        "run_airbyte_sync_step": settings.run_airbyte_sync_step,
        "run_dbt_phase_2_step": settings.run_dbt_phase_2_step,
        "airbyte_connection_names": (
            settings.airbyte_connection_names
            if settings.run_airbyte_sync_step
            else None
        ),
    }


async def _trigger_ingestion_request_run(
    settings: IngestionRequestSettings,
    *,
    request_row: dict[str, Any],
) -> str:
    request_id = request_row["request_id"]
    labels = {
        "request_id": str(request_id),
        "request_source": str(request_row["request_source"]),
        "requested_by": str(request_row["requested_by_metabase_user"]),
    }

    async with get_client() as client:
        deployment = await client.read_deployment_by_name(
            settings.main_deployment_name
        )
        flow_run = await client.create_flow_run_from_deployment(
            deployment.id,
            parameters=_build_request_parameters(
                settings,
                request_id=request_id,
            ),
            name=f"{settings.flow_run_name_prefix}-{request_id}",
            idempotency_key=str(request_id),
            labels=labels,
        )
    return str(flow_run.id)


def _run(command: list[str], step_name: str, cwd: Path | None = None) -> None:
    logger = get_run_logger()
    pretty_command = " ".join(shlex.quote(part) for part in command)
    logger.info("Starting step '%s' with command: %s", step_name, pretty_command)

    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    if process.stdout is not None:
        for line in process.stdout:
            logger.info("[%s] %s", step_name, line.rstrip())

    return_code = process.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)

    logger.info("Finished step '%s' successfully.", step_name)


def _wait_for_airbyte_job(
    *,
    api_base_url: str,
    token: str,
    job_id: str,
    connection_name: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> None:
    logger = get_run_logger()
    started_at = time.monotonic()

    while True:
        job = get_job(api_base_url, token, job_id)
        status = extract_job_status(job)
        elapsed_seconds = int(time.monotonic() - started_at)
        logger.info(
            "Airbyte job status: connection=%s job_id=%s status=%s elapsed_seconds=%s",
            connection_name,
            job_id,
            status or "unknown",
            elapsed_seconds,
        )

        if is_success_job_status(status):
            logger.info(
                "Airbyte sync completed successfully: connection=%s job_id=%s",
                connection_name,
                job_id,
            )
            return

        if is_failed_job_status(status):
            raise RuntimeError(
                f"Airbyte sync failed for connection '{connection_name}' with job {job_id} and status '{status}'."
            )

        if not is_running_job_status(status):
            raise RuntimeError(
                f"Airbyte sync returned unexpected status '{status}' for connection '{connection_name}' and job {job_id}."
            )

        if (time.monotonic() - started_at) >= timeout_seconds:
            raise TimeoutError(
                f"Airbyte sync timed out after {timeout_seconds}s for connection '{connection_name}' and job {job_id}."
            )

        time.sleep(poll_seconds)


def _run_airbyte_sync_step(
    enabled: bool = False,
    connection_names: list[str] | None = None,
) -> None:
    logger = get_run_logger()
    requested_names = connection_names or []
    logger.info(
        "Task parameters: enabled=%s, connection_names=%s",
        enabled,
        requested_names,
    )
    if not enabled:
        logger.info("Airbyte sync phase skipped.")
        return

    if not requested_names:
        raise ValueError(
            "Airbyte sync phase was enabled but no connection names were provided."
        )

    api_base_url = get_api_base_url()
    token = get_access_token(api_base_url)
    workspace_id = ensure_workspace_id(api_base_url, token)
    connections = list_connections(api_base_url, token, workspace_id)

    for connection_name in requested_names:
        connection = find_by_name(connections, connection_name)
        if connection is None:
            available_names = sorted(
                str(item.get("name"))
                for item in connections
                if item.get("name")
            )
            raise RuntimeError(
                f"Unable to find Airbyte connection named '{connection_name}'. Available connections: {available_names}"
            )

        connection_id = str(connection["connectionId"])
        running_job = find_running_job_for_connection(
            api_base_url,
            token,
            connection_id=connection_id,
        )
        if running_job is not None:
            job_id = extract_job_id(running_job)
            logger.info(
                "Reusing running Airbyte sync job: connection=%s connection_id=%s job_id=%s",
                connection_name,
                connection_id,
                job_id,
            )
        else:
            created_job = trigger_sync(api_base_url, token, connection_id)
            job_id = extract_job_id(created_job)
            logger.info(
                "Triggered Airbyte sync job: connection=%s connection_id=%s job_id=%s",
                connection_name,
                connection_id,
                job_id,
            )

        _wait_for_airbyte_job(
            api_base_url=api_base_url,
            token=token,
            job_id=job_id,
            connection_name=connection_name,
            timeout_seconds=DEFAULT_AIRBYTE_SYNC_TIMEOUT_SECONDS,
            poll_seconds=DEFAULT_AIRBYTE_SYNC_POLL_SECONDS,
        )


@flow(
    name="Synchroniser les sources",
    description="Declenche les synchronisations Airbyte lorsqu'elles sont activees pour ce run.",
)
def run_airbyte_sync(
    enabled: bool = False,
    connection_names: list[str] | None = None,
) -> None:
    _run_airbyte_sync_step(
        enabled=enabled,
        connection_names=connection_names,
    )


def _run_dbt_phase_1_step() -> None:
    _run(
        [
            "dbt",
            "build",
            "--select",
            "tag:phase1",
            "--profile",
            "ric",
            "--project-dir",
            str(DBT_PROJECT_DIR),
        ],
        step_name="Preparer les donnees",
        cwd=REPO_ROOT,
    )


@flow(
    name="Preparer les donnees",
    description="Execute la preparation dbt avant le scraping Allocine.",
)
def run_dbt_phase_1() -> None:
    _run_dbt_phase_1_step()


def _run_allocine_scraping_step(config_path: str = str(ALLOCINE_CONFIG_PATH)) -> None:
    logger = get_run_logger()
    logger.info("Task parameters: config_path=%s", config_path)
    _run(
        [
            "python3",
            "-u",
            str(ALLOCINE_MAIN_PATH),
            "sync",
            "--config",
            config_path,
        ],
        step_name="Recuperer les donnees Allocine",
        cwd=REPO_ROOT,
    )


@flow(
    name="Recuperer les donnees Allocine",
    description="Lance le scraping Allocine avec la configuration fournie.",
)
def run_allocine_scraping(config_path: str = str(ALLOCINE_CONFIG_PATH)) -> None:
    _run_allocine_scraping_step(config_path=config_path)


def _run_dbt_phase_2_step(enabled: bool = False) -> None:
    logger = get_run_logger()
    logger.info("Task parameters: enabled=%s", enabled)
    if not enabled:
        logger.info(
            "dbt phase 2 skipped. Step is implemented but disabled for this run."
        )
        return

    _run(
        [
            "dbt",
            "build",
            "--select",
            "tag:phase2",
            "--profile",
            "ric",
            "--project-dir",
            str(DBT_PROJECT_DIR),
        ],
        step_name="Finaliser les donnees",
        cwd=REPO_ROOT,
    )


@flow(
    name="Finaliser les donnees",
    description="Execute la phase dbt finale lorsque cette etape est activee.",
)
def run_dbt_phase_2(enabled: bool = False) -> None:
    _run_dbt_phase_2_step(enabled=enabled)


@flow(
    name="Lancer l'ingestion complete",
    description="Orchestre la preparation des donnees, le scraping Allocine et les etapes optionnelles de synchronisation et de finalisation.",
)
def main_ingestion_flow(
    request_id: str | None = None,
    config_path: str = str(ALLOCINE_CONFIG_PATH),
    run_airbyte_sync_step: bool = False,
    run_dbt_phase_2_step: bool = False,
    airbyte_connection_names: list[str] | None = None,
) -> None:
    logger = get_run_logger()
    logger.info(
        "Flow parameters: config_path=%s, run_airbyte_sync_step=%s, run_dbt_phase_2_step=%s, airbyte_connection_names=%s",
        config_path,
        run_airbyte_sync_step,
        run_dbt_phase_2_step,
        airbyte_connection_names or [],
    )
    request_settings = None
    request_uuid = None
    if request_id is not None:
        request_uuid = UUID(request_id)
        request_settings = IngestionRequestSettings.from_env()
        _mark_request_processing(
            request_settings,
            request_id=request_uuid,
        )

    try:
        _run_airbyte_sync_step(
            enabled=run_airbyte_sync_step,
            connection_names=airbyte_connection_names,
        )
        _run_dbt_phase_1_step()
        _run_allocine_scraping_step(config_path=config_path)
        _run_dbt_phase_2_step(enabled=run_dbt_phase_2_step)
    except Exception as exc:
        if request_settings is not None and request_uuid is not None:
            _mark_request_failed(
                request_settings,
                request_id=request_uuid,
                error_message=str(exc),
            )
        raise

    if request_settings is not None and request_uuid is not None:
        _mark_request_success(
            request_settings,
            request_id=request_uuid,
        )


@flow(
    name="Traiter les demandes d'ingestion",
    description="Claim une requete Metabase, declenche le deployment d'ingestion principal, puis persiste l'etat terminal dans ops.ingestion_run_requests.",
)
def dispatch_ingestion_requests(max_requests_per_run: int = 1) -> int:
    logger = get_run_logger()
    settings = IngestionRequestSettings.from_env()
    _ensure_request_queue(settings)

    processed_count = 0
    for _ in range(max_requests_per_run):
        request_row = _claim_next_request(settings)
        if request_row is None:
            logger.info("No pending ingestion request found.")
            break

        request_id = request_row["request_id"]
        logger.info(
            "Claimed request %s from %s.",
            request_id,
            request_row["requested_by_metabase_user"],
        )

        try:
            flow_run_id = asyncio.run(
                _trigger_ingestion_request_run(
                    settings,
                    request_row=request_row,
                )
            )
        except Exception as exc:
            logger.exception("Prefect trigger failed for request %s.", request_id)
            _mark_request_failed(
                settings,
                request_id=request_id,
                error_message=str(exc),
            )
        else:
            _mark_request_processing(
                settings,
                request_id=request_id,
                flow_run_id=flow_run_id,
            )
            logger.info(
                "Triggered flow run %s for request %s.",
                flow_run_id,
                request_id,
            )

        processed_count += 1

    logger.info("Dispatcher processed_count=%s", processed_count)
    return processed_count


@flow(
    name="Requeue les demandes d'ingestion stale",
    description="Maintenance explicite: remet en pending les requetes processing trop anciennes sans flow run associe.",
)
def requeue_stale_ingestion_requests() -> int:
    logger = get_run_logger()
    settings = IngestionRequestSettings.from_env()
    _ensure_request_queue(settings)
    request_ids = _requeue_stale_claims(settings)
    if request_ids:
        logger.info("Requeued stale requests: %s", ", ".join(request_ids))
    else:
        logger.info("No stale processing requests to requeue.")
    return len(request_ids)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Flows Prefect du module ingestion"
    )
    parser.add_argument(
        "flow_name",
        nargs="?",
        default="main-ingestion",
        choices=[
            "main-ingestion",
            "dispatch-ingestion-requests",
            "requeue-stale-ingestion-requests",
        ],
    )
    parser.add_argument(
        "--config-path",
        default=str(ALLOCINE_CONFIG_PATH),
        help="Chemin du fichier de configuration du scraping Allocine.",
    )
    parser.add_argument(
        "--request-id",
        default=None,
        help="Identifiant ops.ingestion_run_requests a mettre a jour pendant l'execution.",
    )
    parser.add_argument(
        "--run-airbyte-sync",
        action="store_true",
        help="Exécute l'étape Airbyte sync. Sinon, elle est explicitement sautée.",
    )
    parser.add_argument(
        "--run-dbt-phase-2",
        action="store_true",
        help="Exécute la phase dbt 2. Sinon, elle est explicitement sautée.",
    )
    parser.add_argument(
        "--airbyte-connection-name",
        action="append",
        dest="airbyte_connection_names",
        default=[],
        help="Nom d'une connexion Airbyte cible. Répéter l'option pour plusieurs connexions.",
    )
    parser.add_argument(
        "--max-requests-per-run",
        type=int,
        default=1,
        help="Nombre maximal de requetes a claim et dispatcher pendant un run du poller.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    if args.flow_name == "dispatch-ingestion-requests":
        dispatch_ingestion_requests(
            max_requests_per_run=args.max_requests_per_run
        )
        return

    if args.flow_name == "requeue-stale-ingestion-requests":
        requeue_stale_ingestion_requests()
        return

    main_ingestion_flow(
        request_id=args.request_id,
        config_path=args.config_path,
        run_airbyte_sync_step=args.run_airbyte_sync,
        run_dbt_phase_2_step=args.run_dbt_phase_2,
        airbyte_connection_names=args.airbyte_connection_names,
    )


if __name__ == "__main__":
    main()
