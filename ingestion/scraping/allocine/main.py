import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


ENV_PATTERN = re.compile(r"^\$\{(?P<name>[A-Z0-9_]+)(?::-?(?P<default>.*))?\}$")


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _resolve_env_placeholders(nested_value)
            for key, nested_value in value.items()
        }

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
    from ingestion.scraping.allocine.connector import AllocineAirbyteSource

    parser = argparse.ArgumentParser(description="Allocine Airbyte custom source")
    parser.add_argument(
        "command", choices=["spec", "check", "discover", "read", "sync"]
    )
    parser.add_argument("--config", dest="config_path")
    parser.add_argument("--catalog", dest="catalog_path")
    parser.add_argument("--state", dest="state_path")
    args = parser.parse_args()

    source = AllocineAirbyteSource()

    if args.command == "spec":
        _emit({"type": "SPEC", "spec": source.spec()})
        return 0

    config = _load_json(args.config_path) or {}

    if args.command == "check":
        ok, message = source.check(config)
        _emit(
            {
                "type": "CONNECTION_STATUS",
                "connectionStatus": {
                    "status": "SUCCEEDED" if ok else "FAILED",
                    "message": message,
                },
            }
        )
        return 0 if ok else 1

    if args.command == "discover":
        _emit({"type": "CATALOG", "catalog": source.discover()})
        return 0

    if args.command == "sync":
        inserted_count = source.sync_to_postgres(config)
        print(f"Inserted {inserted_count} rows into configured output table.")
        return 0

    catalog = _load_json(args.catalog_path)
    _ = _load_json(args.state_path)

    for record in source.read(config=config, catalog=catalog):
        _emit(
            {
                "type": "RECORD",
                "record": {
                    "stream": "allocine_data",
                    "emitted_at": _epoch_millis(record["extracted_at"]),
                    "data": record,
                },
            }
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
