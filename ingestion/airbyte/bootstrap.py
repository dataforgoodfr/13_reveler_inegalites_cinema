#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib import error, parse, request


ROOT_DIR = Path(__file__).resolve().parents[2]
INGESTION_DIR = ROOT_DIR / "ingestion"
AIRBYTE_DIR = INGESTION_DIR / "airbyte"
DEFAULT_ENV_PATH = INGESTION_DIR / ".env"
SOURCE_DIR = AIRBYTE_DIR / "sources"
JSON_CREDENTIALS_DIR = AIRBYTE_DIR / "json_credentials"
ENV_PATTERN = re.compile(r"^\$\{(?P<name>[A-Z0-9_]+)(?::-?(?P<default>.*))?\}$")
ABCTL_CREDENTIALS_PATTERN = re.compile(r"^\s*(?P<key>[A-Za-z-]+):\s*(?P<value>.+?)\s*$")


def load_dotenv(path: Path) -> None:
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


def resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: resolve_env_placeholders(nested_value)
            for key, nested_value in value.items()
        }

    if isinstance(value, list):
        return [resolve_env_placeholders(item) for item in value]

    if not isinstance(value, str):
        return value

    match = ENV_PATTERN.match(value)
    if not match:
        return value

    env_name = match.group("name")
    default_value = match.group("default")
    resolved = os.getenv(env_name, default_value)
    return value if resolved is None else resolved


def json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_as_string(path: Path) -> str:
    parsed = json_load(path)
    return json.dumps(parsed, ensure_ascii=False)


def request_json(
    method: str,
    url: str,
    *,
    token: str | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any]:
    payload = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        payload = json.dumps(body).encode("utf-8")

    req = request.Request(url, data=payload, headers=headers, method=method)
    try:
        with request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: {exc.code} {detail}") from exc

    if not raw:
        return {}
    return json.loads(raw)


def get_api_base_url() -> str:
    api_url = os.getenv("AIRBYTE_API_URL")
    if api_url:
        return api_url.rstrip("/")

    host = os.getenv("AIRBYTE_HOST", "localhost")
    port = os.getenv("AIRBYTE_PORT", "8000")
    return f"http://{host}:{port}/api/public/v1"


def ensure_airbyte_api_credentials() -> None:
    if os.getenv("AIRBYTE_CLIENT_ID") and os.getenv("AIRBYTE_CLIENT_SECRET"):
        return

    process = subprocess.run(
        ["abctl", "local", "credentials"],
        check=True,
        capture_output=True,
        text=True,
    )

    parsed: dict[str, str] = {}
    for line in process.stdout.splitlines():
        match = ABCTL_CREDENTIALS_PATTERN.match(line)
        if not match:
            continue
        parsed[match.group("key").lower()] = match.group("value")

    client_id = parsed.get("client-id")
    client_secret = parsed.get("client-secret")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Unable to infer AIRBYTE_CLIENT_ID / AIRBYTE_CLIENT_SECRET from `abctl local credentials`."
        )

    os.environ.setdefault("AIRBYTE_CLIENT_ID", client_id)
    os.environ.setdefault("AIRBYTE_CLIENT_SECRET", client_secret)


def get_access_token(api_base_url: str) -> str:
    ensure_airbyte_api_credentials()
    body = {
        "client_id": os.environ["AIRBYTE_CLIENT_ID"],
        "client_secret": os.environ["AIRBYTE_CLIENT_SECRET"],
        "grant_type": "client_credentials",
    }
    response = request_json("POST", f"{api_base_url}/applications/token", body=body)
    if not isinstance(response, dict) or not response.get("access_token"):
        raise RuntimeError("Airbyte token response does not contain access_token")
    return str(response["access_token"])


def list_workspaces(api_base_url: str, token: str) -> list[dict[str, Any]]:
    response = request_json("GET", f"{api_base_url}/workspaces?limit=100", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def ensure_workspace_id(api_base_url: str, token: str) -> str:
    existing = os.getenv("AIRBYTE_WORKSPACE_ID")
    if existing:
        return existing

    workspaces = list_workspaces(api_base_url, token)
    if len(workspaces) != 1:
        raise RuntimeError(
            "AIRBYTE_WORKSPACE_ID is unset and bootstrap could not infer a single workspace."
        )

    workspace_id = str(workspaces[0]["workspaceId"])
    os.environ["AIRBYTE_WORKSPACE_ID"] = workspace_id
    return workspace_id


def list_definitions(
    api_base_url: str,
    token: str,
    workspace_id: str,
    kind: str,
) -> list[dict[str, Any]]:
    path = "sources" if kind == "source" else "destinations"
    response = request_json(
        "GET",
        f"{api_base_url}/workspaces/{workspace_id}/definitions/{path}",
        token=token,
    )
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def get_definition_id_by_name(
    api_base_url: str,
    token: str,
    workspace_id: str,
    *,
    kind: str,
    name: str,
) -> str:
    for definition in list_definitions(api_base_url, token, workspace_id, kind):
        if definition.get("name") == name:
            return str(definition["id"])
    raise RuntimeError(f"Unable to find {kind} definition named '{name}' in workspace {workspace_id}")


def infer_single_service_account_file() -> Path:
    files = sorted(
        path
        for path in JSON_CREDENTIALS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".json"
    )
    if len(files) != 1:
        raise RuntimeError(
            "Bootstrap expects exactly one JSON credentials file in ingestion/airbyte/json_credentials/ "
            "when service_account_info_file is omitted."
        )
    return files[0]


def resolve_service_account_path(raw_value: str | None, base_dir: Path) -> Path:
    if raw_value:
        path = Path(raw_value)
        if not path.is_absolute():
            path = (base_dir / raw_value).resolve()
        return path
    return infer_single_service_account_file().resolve()


def expand_source_configuration(value: Any, base_dir: Path) -> Any:
    if isinstance(value, dict):
        expanded = {
            key: expand_source_configuration(nested_value, base_dir)
            for key, nested_value in value.items()
        }

        if expanded.get("auth_type") == "Service":
            raw_file = expanded.pop("service_account_info_file", None)
            file_path = resolve_service_account_path(
                str(raw_file) if raw_file is not None else None,
                base_dir,
            )
            expanded["service_account_info"] = load_json_as_string(file_path)

        return expanded

    if isinstance(value, list):
        return [expand_source_configuration(item, base_dir) for item in value]

    return value


def list_sources(api_base_url: str, token: str, workspace_id: str) -> list[dict[str, Any]]:
    query = parse.urlencode({"workspaceIds": workspace_id, "limit": 100})
    response = request_json("GET", f"{api_base_url}/sources?{query}", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def list_destinations(api_base_url: str, token: str, workspace_id: str) -> list[dict[str, Any]]:
    query = parse.urlencode({"workspaceIds": workspace_id, "limit": 100})
    response = request_json("GET", f"{api_base_url}/destinations?{query}", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def list_connections(api_base_url: str, token: str, workspace_id: str) -> list[dict[str, Any]]:
    query = parse.urlencode({"workspaceIds": workspace_id, "limit": 100})
    response = request_json("GET", f"{api_base_url}/connections?{query}", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def find_by_name(items: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("name") == name:
            return item
    return None


def find_connection(
    connections: list[dict[str, Any]],
    source_id: str,
    destination_id: str,
) -> dict[str, Any] | None:
    for connection in connections:
        if (
            connection.get("sourceId") == source_id
            and connection.get("destinationId") == destination_id
        ):
            return connection
    return None


def default_source_name(manifest_path: Path) -> str:
    return manifest_path.stem.replace("_", " ").replace("-", " ").strip() or "Google Sheets"


def build_source_payload(
    api_base_url: str,
    token: str,
    manifest: dict[str, Any],
    manifest_path: Path,
    workspace_id: str,
) -> dict[str, Any]:
    configuration = manifest.get("configuration")
    if not isinstance(configuration, dict):
        raise RuntimeError(
            f"Manifest {manifest_path} is missing required object field: configuration"
        )

    spreadsheet_id = configuration.get("spreadsheet_id")
    if not spreadsheet_id or str(spreadsheet_id).startswith("REPLACE_WITH_"):
        raise RuntimeError(
            f"Manifest {manifest_path} must define configuration.spreadsheet_id."
        )

    definition_id = (
        manifest.get("definition_id")
        or get_definition_id_by_name(
            api_base_url,
            token,
            workspace_id,
            kind="source",
            name="Google Sheets",
        )
    )

    defaults = {
        "batch_size": 1000000,
        "credentials": {
            "auth_type": "Service",
        },
        "names_conversion": False,
        "allow_leading_numbers": False,
        "stream_name_overrides": [],
        "combine_number_word_pairs": False,
        "read_empty_header_columns": False,
        "remove_special_characters": False,
        "combine_letter_number_pairs": False,
        "remove_leading_trailing_underscores": False,
    }
    merged_configuration = {**defaults, **configuration}
    if isinstance(defaults["credentials"], dict) and isinstance(
        merged_configuration.get("credentials"), dict
    ):
        merged_configuration["credentials"] = {
            **defaults["credentials"],
            **merged_configuration["credentials"],
        }

    resolved = resolve_env_placeholders(merged_configuration)
    expanded = expand_source_configuration(resolved, manifest_path.parent)

    return {
        "name": str(manifest.get("name") or default_source_name(manifest_path)),
        "workspaceId": workspace_id,
        "definitionId": str(definition_id),
        "configuration": expanded,
    }


def ensure_source(
    api_base_url: str,
    token: str,
    manifest_path: Path,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    workspace_id = ensure_workspace_id(api_base_url, token)
    manifest = resolve_env_placeholders(json_load(manifest_path))
    payload = build_source_payload(api_base_url, token, manifest, manifest_path, workspace_id)
    existing = find_by_name(list_sources(api_base_url, token, workspace_id), payload["name"])

    action = "update" if existing else "create"
    print(f"[source:{action}] {manifest_path}")

    if dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if existing:
            preview = dict(existing)
            preview["name"] = payload["name"]
            preview["workspaceId"] = payload["workspaceId"]
            preview["definitionId"] = payload["definitionId"]
            preview["configuration"] = payload["configuration"]
            return preview
        return payload

    if existing:
        source_id = str(existing["sourceId"])
        response = request_json(
            "PUT",
            f"{api_base_url}/sources/{source_id}",
            token=token,
            body={"name": payload["name"], "configuration": payload["configuration"]},
        )
        if not isinstance(response, dict):
            raise RuntimeError("Unexpected Airbyte response while updating source")
        return response

    response = request_json(
        "POST",
        f"{api_base_url}/sources",
        token=token,
        body=payload,
    )
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Airbyte response while creating source")
    return response


def build_destination_payload(
    api_base_url: str,
    token: str,
    workspace_id: str,
) -> dict[str, Any]:
    definition_id = get_definition_id_by_name(
        api_base_url,
        token,
        workspace_id,
        kind="destination",
        name="Postgres",
    )
    user = "airbyte_user"
    password = os.getenv("AIRBYTE_DESTINATION_POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "Missing AIRBYTE_DESTINATION_POSTGRES_PASSWORD for Postgres destination bootstrap."
        )

    ssl_mode = os.getenv("POSTGRES_SSLMODE", "disable")
    return {
        "name": os.getenv("AIRBYTE_DESTINATION_NAME", "dst_pg_raw"),
        "workspaceId": workspace_id,
        "definitionId": definition_id,
        "configuration": {
            "host": os.getenv("POSTGRES_HOST"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB"),
            "schema": "raw",
            "username": user,
            "password": password,
            "ssl": ssl_mode != "disable",
            "ssl_mode": {"mode": ssl_mode},
            "tunnel_method": {"tunnel_method": "NO_TUNNEL"},
        },
    }


def ensure_destination(
    api_base_url: str,
    token: str,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    workspace_id = ensure_workspace_id(api_base_url, token)
    payload = build_destination_payload(api_base_url, token, workspace_id)
    existing = find_by_name(list_destinations(api_base_url, token, workspace_id), payload["name"])

    action = "update" if existing else "create"
    print(f"[destination:{action}] {payload['name']}")

    if dry_run:
        redacted = json.loads(json.dumps(payload))
        redacted["configuration"]["password"] = "**********"
        print(json.dumps(redacted, ensure_ascii=False, indent=2))
        if existing:
            preview = dict(existing)
            preview["name"] = payload["name"]
            preview["workspaceId"] = payload["workspaceId"]
            preview["definitionId"] = payload["definitionId"]
            preview["configuration"] = payload["configuration"]
            return preview
        return payload

    if existing:
        destination_id = str(existing["destinationId"])
        response = request_json(
            "PUT",
            f"{api_base_url}/destinations/{destination_id}",
            token=token,
            body={"name": payload["name"], "configuration": payload["configuration"]},
        )
        if not isinstance(response, dict):
            raise RuntimeError("Unexpected Airbyte response while updating destination")
        return response

    response = request_json(
        "POST",
        f"{api_base_url}/destinations",
        token=token,
        body=payload,
    )
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Airbyte response while creating destination")
    return response


def get_streams(
    api_base_url: str,
    token: str,
    source_id: str,
    destination_id: str,
) -> list[dict[str, Any]]:
    query = parse.urlencode(
        {
            "sourceId": source_id,
            "destinationId": destination_id,
            "ignoreCache": "false",
        }
    )
    response = request_json("GET", f"{api_base_url}/streams?{query}", token=token)
    if not isinstance(response, list):
        raise RuntimeError("Unexpected Airbyte stream metadata response")
    return response


def build_connection_payload(
    source: dict[str, Any],
    destination: dict[str, Any],
    streams: list[dict[str, Any]],
) -> dict[str, Any]:
    stream_configs = []
    for stream in streams:
        sync_modes = stream.get("syncModes") or []
        if not sync_modes:
            continue
        stream_configs.append(
            {
                "name": stream["streamName"],
                "syncMode": sync_modes[0],
                "selected": True,
            }
        )

    if not stream_configs:
        raise RuntimeError(
            f"No stream configurations available for source {source['sourceId']} and destination {destination['destinationId']}"
        )

    return {
        "name": os.getenv(
            "AIRBYTE_CONNECTION_NAME",
            f"{source['name']} -> {destination['name']}",
        ),
        "sourceId": source["sourceId"],
        "destinationId": destination["destinationId"],
        "configurations": {
            "streams": stream_configs,
            "namespaceDefinition": os.getenv("AIRBYTE_CONNECTION_NAMESPACE_DEFINITION", "destination"),
            "prefix": os.getenv("AIRBYTE_CONNECTION_PREFIX", ""),
            "nonBreakingSchemaUpdatesBehavior": os.getenv(
                "AIRBYTE_CONNECTION_SCHEMA_UPDATES_BEHAVIOR", "ignore"
            ),
            "status": os.getenv("AIRBYTE_CONNECTION_STATUS", "active"),
        },
    }


def ensure_connection(
    api_base_url: str,
    token: str,
    source: dict[str, Any],
    destination: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    workspace_id = ensure_workspace_id(api_base_url, token)
    if "sourceId" not in source or "destinationId" not in destination:
        print(
            "[connection:skip] dry-run cannot preview connection for resources that do not exist yet."
        )
        return {}
    streams = get_streams(api_base_url, token, source["sourceId"], destination["destinationId"])
    payload = build_connection_payload(source, destination, streams)
    existing = find_connection(
        list_connections(api_base_url, token, workspace_id),
        source["sourceId"],
        destination["destinationId"],
    )

    action = "update" if existing else "create"
    print(f"[connection:{action}] {payload['name']}")

    if dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return payload

    if existing:
        connection_id = str(existing["connectionId"])
        response = request_json(
            "PATCH",
            f"{api_base_url}/connections/{connection_id}",
            token=token,
            body={"configurations": payload["configurations"]},
        )
        if not isinstance(response, dict):
            raise RuntimeError("Unexpected Airbyte response while updating connection")
        return response

    response = request_json(
        "POST",
        f"{api_base_url}/connections",
        token=token,
        body=payload,
    )
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Airbyte response while creating connection")
    return response


def iter_source_manifests(paths: list[str]) -> list[Path]:
    if not paths:
        return sorted(path for path in SOURCE_DIR.glob("*.json") if path.is_file())

    result: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).resolve()
        if path.is_dir():
            result.extend(sorted(child for child in path.glob("*.json") if child.is_file()))
        else:
            result.append(path)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap Airbyte sources, Postgres destination and connections from versioned manifests."
    )
    parser.add_argument(
        "command",
        choices=["apply", "list-sources", "list-workspaces"],
        help="Action to run against Airbyte.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Manifest file(s) or directory(ies). Defaults to ingestion/airbyte/sources/.",
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_PATH),
        help="Path to the .env file to preload before resolving placeholders.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve manifests and print payloads without calling the Airbyte API.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(Path(args.env_file))

    api_base_url = get_api_base_url()
    token = get_access_token(api_base_url)

    if args.command == "list-workspaces":
        print(json.dumps(list_workspaces(api_base_url, token), ensure_ascii=False, indent=2))
        return 0

    if args.command == "list-sources":
        workspace_id = ensure_workspace_id(api_base_url, token)
        print(
            json.dumps(
                list_sources(api_base_url, token, workspace_id),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    manifests = iter_source_manifests(args.paths)
    if not manifests:
        raise RuntimeError("No source manifests found to apply.")

    destination = ensure_destination(api_base_url, token, dry_run=args.dry_run)
    for manifest_path in manifests:
        source = ensure_source(
            api_base_url,
            token,
            manifest_path.resolve(),
            dry_run=args.dry_run,
        )
        ensure_connection(
            api_base_url,
            token,
            source,
            destination,
            dry_run=args.dry_run,
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
