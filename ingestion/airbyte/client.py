#!/usr/bin/env python3
import json
import os
from typing import Any
from urllib import error, parse, request

RUNNING_JOB_STATUSES = {"pending", "running", "incomplete"}
SUCCESS_JOB_STATUSES = {"succeeded", "success", "completed"}
FAILED_JOB_STATUSES = {"failed", "cancelled", "canceled"}


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
    client_id = os.getenv("AIRBYTE_CLIENT_ID")
    client_secret = os.getenv("AIRBYTE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing AIRBYTE_CLIENT_ID / AIRBYTE_CLIENT_SECRET. Populate both values in ingestion/.env before using Airbyte API features."
        )


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
            "AIRBYTE_WORKSPACE_ID is unset and Airbyte client could not infer a single workspace."
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
    raise RuntimeError(
        f"Unable to find {kind} definition named '{name}' in workspace {workspace_id}"
    )


def list_sources(
    api_base_url: str, token: str, workspace_id: str
) -> list[dict[str, Any]]:
    query = parse.urlencode({"workspaceIds": workspace_id, "limit": 100}, doseq=True)
    response = request_json("GET", f"{api_base_url}/sources?{query}", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def list_destinations(
    api_base_url: str, token: str, workspace_id: str
) -> list[dict[str, Any]]:
    query = parse.urlencode({"workspaceIds": workspace_id, "limit": 100}, doseq=True)
    response = request_json("GET", f"{api_base_url}/destinations?{query}", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def list_connections(
    api_base_url: str, token: str, workspace_id: str
) -> list[dict[str, Any]]:
    query = parse.urlencode({"workspaceIds": workspace_id, "limit": 100}, doseq=True)
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


def list_jobs(
    api_base_url: str,
    token: str,
    *,
    connection_id: str | None = None,
    job_type: str | None = "sync",
    limit: int = 20,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit}
    if connection_id:
        params["connectionId"] = connection_id
    if job_type:
        params["jobType"] = job_type

    query = parse.urlencode(params, doseq=True)
    response = request_json("GET", f"{api_base_url}/jobs?{query}", token=token)
    if not isinstance(response, dict):
        return []
    return list(response.get("data", []))


def trigger_sync(api_base_url: str, token: str, connection_id: str) -> dict[str, Any]:
    response = request_json(
        "POST",
        f"{api_base_url}/jobs",
        token=token,
        body={"connectionId": connection_id, "jobType": "sync"},
    )
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Airbyte response while creating sync job")
    return response


def get_job(api_base_url: str, token: str, job_id: str) -> dict[str, Any]:
    response = request_json("GET", f"{api_base_url}/jobs/{job_id}", token=token)
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Airbyte response while fetching job")
    return response


def cancel_job(api_base_url: str, token: str, job_id: str) -> dict[str, Any]:
    response = request_json("DELETE", f"{api_base_url}/jobs/{job_id}", token=token)
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Airbyte response while cancelling job")
    return response


def extract_job_id(job: dict[str, Any]) -> str:
    for key in ("jobId", "id"):
        value = job.get(key)
        if value is not None:
            return str(value)

    nested_job = job.get("job")
    if isinstance(nested_job, dict):
        for key in ("jobId", "id"):
            value = nested_job.get(key)
            if value is not None:
                return str(value)

    raise RuntimeError(f"Unable to extract Airbyte job id from payload: {job}")


def normalize_job_status(status: Any) -> str:
    if status is None:
        return ""
    return str(status).strip().lower()


def extract_job_status(job: dict[str, Any]) -> str:
    for key in ("status",):
        value = job.get(key)
        if value is not None:
            return normalize_job_status(value)

    nested_job = job.get("job")
    if isinstance(nested_job, dict):
        value = nested_job.get("status")
        if value is not None:
            return normalize_job_status(value)

    return ""


def is_running_job_status(status: str) -> bool:
    return normalize_job_status(status) in RUNNING_JOB_STATUSES


def is_success_job_status(status: str) -> bool:
    return normalize_job_status(status) in SUCCESS_JOB_STATUSES


def is_failed_job_status(status: str) -> bool:
    return normalize_job_status(status) in FAILED_JOB_STATUSES


def find_running_job_for_connection(
    api_base_url: str,
    token: str,
    *,
    connection_id: str,
) -> dict[str, Any] | None:
    for job in list_jobs(
        api_base_url,
        token,
        connection_id=connection_id,
        job_type="sync",
        limit=20,
    ):
        if is_running_job_status(extract_job_status(job)):
            return job
    return None
