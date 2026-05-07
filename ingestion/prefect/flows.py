import argparse
import shlex
import subprocess
from pathlib import Path

from prefect import flow, get_run_logger


REPO_ROOT = Path("/app")
DBT_PROJECT_DIR = REPO_ROOT / "ingestion" / "dbt"
ALLOCINE_CONFIG_PATH = (
    REPO_ROOT / "ingestion" / "scraping" / "allocine" / "config.template.json"
)
ALLOCINE_MAIN_PATH = REPO_ROOT / "ingestion" / "scraping" / "allocine" / "main.py"


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
    logger.info(
        "Task parameters: enabled=%s, connection_names=%s",
        enabled,
        connection_names or [],
    )
    if not enabled:
        logger.info(
            "Airbyte sync phase skipped. Future flow scaffolded but not implemented yet."
        )
        return

    names = ", ".join(connection_names or [])
    raise NotImplementedError(
        "Airbyte sync via API is not implemented yet. "
        f"Requested connections: {names or 'none'}."
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
