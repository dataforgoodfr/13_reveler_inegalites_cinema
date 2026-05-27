import argparse
import builtins
import json
import os
import re
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

INGESTION_DIR = ROOT_DIR / "ingestion"
DEFAULT_ENV_PATH = INGESTION_DIR / ".env"

ENV_PATTERN = re.compile(r"^\$\{(?P<name>[A-Z0-9_]+)(?::-?(?P<default>.*))?\}$")

print = partial(builtins.print, flush=True)


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _resolve_env_placeholders(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_placeholders(item) for item in value]
    if not isinstance(value, str):
        return value
    match = ENV_PATTERN.match(value)
    if not match:
        return value
    env_name = match.group("name")
    default_value = match.group("default")
    resolved = os.getenv(env_name, default_value)
    return value if resolved is None else resolved


def _load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    with open(path, encoding="utf-8") as handle:
        return _resolve_env_placeholders(json.load(handle))


def _emit(message: dict[str, Any]) -> None:
    print(json.dumps(message, ensure_ascii=False))


def _epoch_millis(iso_value: str) -> int:
    return int(datetime.fromisoformat(iso_value).timestamp() * 1000)


def main() -> int:
    from ingestion.scraping.mubi.connector import MubiAirbyteSource

    _load_dotenv(DEFAULT_ENV_PATH)

    parser = argparse.ArgumentParser(description="Mubi Airbyte custom source")
    parser.add_argument("command", choices=["spec", "check", "discover", "sync"])
    parser.add_argument("--config", dest="config_path")
    args = parser.parse_args()

    source = MubiAirbyteSource()

    if args.command == "spec":
        _emit({"type": "SPEC", "spec": source.spec()})
        return 0

    config = _load_json(args.config_path) or {}

    if args.command == "check":
        ok, message = source.check(config)
        _emit({
            "type": "CONNECTION_STATUS",
            "connectionStatus": {
                "status": "SUCCEEDED" if ok else "FAILED",
                "message": message,
            },
        })
        return 0 if ok else 1

    if args.command == "discover":
        _emit({"type": "CATALOG", "catalog": source.discover()})
        return 0

    if args.command == "sync":
        counts = source.sync_to_postgres(config)
        print(
            f"Inserted {counts.get('festival_films', 0)} festival film records "
            f"and {counts.get('film_awards', 0)} film award records."
        )
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
