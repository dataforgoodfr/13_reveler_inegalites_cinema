import argparse
import os
import shlex
import subprocess
import time
from pathlib import Path

from prefect import flow, get_run_logger

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


@flow(
    name="Synchroniser les sources",
    description="Declenche les synchronisations Airbyte lorsqu'elles sont activees pour ce run.",
    flow_run_name="synchroniser-les-sources",
)
def run_airbyte_sync(
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
    name="Preparer les donnees",
    description="Execute la preparation dbt avant le scraping Allocine.",
    flow_run_name="preparer-les-donnees",
)
def run_dbt_phase_1() -> None:
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
    name="Recuperer les donnees Allocine",
    description="Lance le scraping Allocine avec la configuration fournie.",
    flow_run_name="recuperer-les-donnees-allocine",
)
def run_allocine_scraping(config_path: str = str(ALLOCINE_CONFIG_PATH)) -> None:
    logger = get_run_logger()
    logger.info("Task parameters: config_path=%s", config_path)
    _run(
        ["python3", str(ALLOCINE_MAIN_PATH), "sync", "--config", config_path],
        step_name="Recuperer les donnees Allocine",
        cwd=REPO_ROOT,
    )


@flow(
    name="Finaliser les donnees",
    description="Execute la phase dbt finale lorsque cette etape est activee.",
    flow_run_name="finaliser-les-donnees",
)
def run_dbt_phase_2(enabled: bool = False) -> None:
    logger = get_run_logger()
    logger.info("Task parameters: enabled=%s", enabled)
    if not enabled:
        logger.info(
            "dbt phase 2 skipped. Future flow scaffolded but not implemented yet."
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
    name="Lancer l'ingestion complete",
    description="Orchestre la preparation des donnees, le scraping Allocine et les etapes optionnelles de synchronisation et de finalisation.",
)
def main_ingestion_flow(
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
    run_airbyte_sync(
        enabled=run_airbyte_sync_step,
        connection_names=airbyte_connection_names,
    )
    run_dbt_phase_1()
    run_allocine_scraping(config_path=config_path)
    run_dbt_phase_2(enabled=run_dbt_phase_2_step)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Flows Prefect du module ingestion"
    )
    parser.add_argument(
        "flow_name",
        nargs="?",
        default="main-ingestion",
        choices=["main-ingestion"],
    )
    parser.add_argument(
        "--config-path",
        default=str(ALLOCINE_CONFIG_PATH),
        help="Chemin du fichier de configuration du scraping Allocine.",
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
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    main_ingestion_flow(
        config_path=args.config_path,
        run_airbyte_sync_step=args.run_airbyte_sync,
        run_dbt_phase_2_step=args.run_dbt_phase_2,
        airbyte_connection_names=args.airbyte_connection_names,
    )


if __name__ == "__main__":
    main()
