import asyncio
import hashlib
import json
import os
import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy import bindparam, create_engine, text

from backend.utils.date_utils import parse_duration, parse_release_date
from ingestion.scraping.browser import WebsiteBlockedError

STREAM_NAME = "allocine_data"
DEFAULT_INPUT_SCHEMA = "raw"
DEFAULT_INPUT_TABLE = "id_matching"
DEFAULT_OUTPUT_SCHEMA = "raw"
DEFAULT_OUTPUT_TABLE = STREAM_NAME
DEFAULT_COMPLETED_STATUSES = ["success", "not_found", "visa_mismatch"]
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


CONNECTION_SPECIFICATION = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Allocine Airbyte Source",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "database_url": {
            "type": "string",
            "title": "Database URL",
            "description": "Optional SQLAlchemy URL. Overrides individual Postgres fields when set.",
            "airbyte_secret": True,
        },
        "postgres_host": {"type": "string", "title": "Postgres host"},
        "postgres_port": {"type": "integer", "title": "Postgres port", "default": 5432},
        "postgres_db": {"type": "string", "title": "Postgres database"},
        "postgres_user": {"type": "string", "title": "Postgres user"},
        "postgres_password": {
            "type": "string",
            "title": "Postgres password",
            "airbyte_secret": True,
        },
        "postgres_sslmode": {
            "type": "string",
            "title": "Postgres SSL mode",
            "default": "disable",
            "enum": [
                "disable",
                "allow",
                "prefer",
                "require",
                "verify-ca",
                "verify-full",
            ],
        },
        "input_schema": {
            "type": "string",
            "title": "Input schema",
            "default": DEFAULT_INPUT_SCHEMA,
        },
        "input_table": {
            "type": "string",
            "title": "Input table",
            "default": DEFAULT_INPUT_TABLE,
        },
        "output_schema": {
            "type": "string",
            "title": "Output schema memory",
            "default": DEFAULT_OUTPUT_SCHEMA,
        },
        "output_table": {
            "type": "string",
            "title": "Output table memory",
            "default": DEFAULT_OUTPUT_TABLE,
        },
        "input_id_column": {
            "type": "string",
            "title": "Record id column",
            "default": "film_id",
        },
        "input_visa_column": {
            "type": "string",
            "title": "Visa column",
            "default": "visa_number",
        },
        "input_title_column": {
            "type": "string",
            "title": "Title column",
            "default": "original_name",
        },
        "input_year_column": {
            "type": ["string", "null"],
            "title": "Agreement year column",
            "default": "cnc_agrement_year",
        },
        "input_allocine_id_column": {
            "type": ["string", "null"],
            "title": "Optional existing Allocine id column",
            "default": "allocine_id",
        },
        "input_allocine_url_column": {
            "type": ["string", "null"],
            "title": "Optional existing Allocine URL column",
            "default": "allocine_url",
        },
        "completed_statuses": {
            "type": "array",
            "title": "Statuses considered already processed",
            "default": DEFAULT_COMPLETED_STATUSES,
            "items": {"type": "string"},
        },
        "scrape_limit": {
            "type": ["integer", "null"],
            "title": "Maximum number of pending items to scrape",
            "minimum": 1,
            "description": "Optional debug limit applied after filtering already processed records.",
        },
        "playwright_ws_endpoint": {
            "type": "string",
            "title": "Playwright websocket endpoint",
            "description": "Optional override for PLAYWRIGHT_WS_ENDPOINT.",
        },
        "headless": {
            "type": "boolean",
            "title": "Headless browser",
            "default": True,
            "description": "Run the browser in headless mode. Set to false for local visual debugging (requires no ws_endpoint).",
        },
        "debug_pause_between_actions": {
            "type": "boolean",
            "title": "Pause between actions for debugging",
            "default": False,
            "description": "When true, pause for Enter between browser actions. Recommended only with headless=false.",
        },
        "parallel_sessions": {
            "type": "integer",
            "title": "Parallel browser sessions",
            "default": 1,
            "minimum": 1,
            "maximum": 5,
            "description": "Number of concurrent browser sessions. Values above 1 disable debug_pause_between_actions.",
        },
        "verbose": {
            "type": "boolean",
            "title": "Verbose logging",
            "default": False,
            "description": "When true, print detailed step-by-step progress during scraping.",
        },
    },
}


STREAM_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "run_id": {"type": "string"},
        "extracted_at": {"type": "string", "format": "date-time"},
        "source_record_id": {"type": ["string", "null"]},
        "visa_number": {"type": ["string", "null"]},
        "original_name": {"type": ["string", "null"]},
        "cnc_agrement_year": {"type": ["integer", "null"]},
        "match_strategy": {"type": ["string", "null"]},
        "search_url": {"type": ["string", "null"]},
        "source_url": {"type": ["string", "null"]},
        "allocine_id": {"type": ["integer", "null"]},
        "allocine_title": {"type": ["string", "null"]},
        "allocine_url": {"type": ["string", "null"]},
        "allocine_visa_number": {"type": ["string", "null"]},
        "release_date_raw": {"type": ["string", "null"]},
        "release_date": {"type": ["string", "null"], "format": "date"},
        "duration_raw": {"type": ["string", "null"]},
        "duration_minutes": {"type": ["integer", "null"]},
        "genres": {"type": ["array", "null"], "items": {"type": "string"}},
        "trailer_url": {"type": ["string", "null"]},
        "direction": {"type": ["array", "null"], "items": {"type": "string"}},
        "casting": {"type": ["array", "null"], "items": {"type": "string"}},
        "screenwriters": {"type": ["array", "null"], "items": {"type": "object"}},
        "production": {"type": ["array", "null"], "items": {"type": "object"}},
        "technical_team": {"type": ["array", "null"], "items": {"type": "object"}},
        "soundtrack": {"type": ["array", "null"], "items": {"type": "object"}},
        "distribution": {"type": ["array", "null"], "items": {"type": "object"}},
        "companies": {"type": ["array", "null"], "items": {"type": "object"}},
        "scrape_status": {"type": "string"},
        "error_message": {"type": ["string", "null"]},
        "record_hash": {"type": "string"},
    },
}


@dataclass
class ConnectorConfig:
    database_url: str
    input_schema: str
    input_table: str
    output_schema: str
    output_table: str
    input_id_column: str
    input_visa_column: str
    input_title_column: str
    input_year_column: str | None
    input_allocine_id_column: str | None
    input_allocine_url_column: str | None
    completed_statuses: list[str]
    scrape_limit: int | None
    playwright_ws_endpoint: str | None
    headless: bool
    debug_pause_between_actions: bool
    parallel_sessions: int
    verbose: bool

    @classmethod
    def from_dict(cls, raw_config: dict[str, Any]) -> "ConnectorConfig":
        database_url = raw_config.get("database_url") or _build_database_url(raw_config)
        completed_statuses = (
            raw_config.get("completed_statuses") or DEFAULT_COMPLETED_STATUSES
        )

        values = {
            "database_url": database_url,
            "input_schema": raw_config.get("input_schema", DEFAULT_INPUT_SCHEMA),
            "input_table": raw_config.get("input_table", DEFAULT_INPUT_TABLE),
            "output_schema": raw_config.get("output_schema", DEFAULT_OUTPUT_SCHEMA),
            "output_table": raw_config.get("output_table", DEFAULT_OUTPUT_TABLE),
            "input_id_column": raw_config.get("input_id_column", "film_id"),
            "input_visa_column": raw_config.get("input_visa_column", "visa_number"),
            "input_title_column": raw_config.get("input_title_column", "original_name"),
            "input_year_column": raw_config.get(
                "input_year_column", "cnc_agrement_year"
            ),
            "input_allocine_id_column": raw_config.get(
                "input_allocine_id_column", "allocine_id"
            ),
            "input_allocine_url_column": raw_config.get(
                "input_allocine_url_column", "allocine_url"
            ),
            "completed_statuses": [
                str(status).lower() for status in completed_statuses
            ],
            "scrape_limit": _normalize_positive_int(raw_config.get("scrape_limit")),
            "playwright_ws_endpoint": raw_config.get("playwright_ws_endpoint")
            or os.getenv("PLAYWRIGHT_WS_ENDPOINT"),
            "headless": bool(raw_config.get("headless", True)),
            "debug_pause_between_actions": bool(
                raw_config.get("debug_pause_between_actions", False)
            ),
            "parallel_sessions": max(1, int(raw_config.get("parallel_sessions", 1) or 1)),
            "verbose": bool(raw_config.get("verbose", False)),
        }

        for key, value in values.items():
            if (
                key.endswith("_column")
                or key.endswith("_schema")
                or key.endswith("_table")
            ):
                if value:
                    _validate_identifier(value)

        return cls(**values)


def _build_database_url(raw_config: dict[str, Any]) -> str:
    required = [
        "postgres_host",
        "postgres_port",
        "postgres_db",
        "postgres_user",
        "postgres_password",
    ]
    missing = [key for key in required if raw_config.get(key) in (None, "")]
    if missing:
        raise ValueError(f"Missing config fields: {', '.join(missing)}")

    user = quote_plus(str(raw_config["postgres_user"]))
    password = quote_plus(str(raw_config["postgres_password"]))
    host = str(raw_config["postgres_host"])
    port = int(raw_config["postgres_port"])
    db_name = quote_plus(str(raw_config["postgres_db"]))
    sslmode = raw_config.get("postgres_sslmode", "disable")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}?sslmode={sslmode}"


def _validate_identifier(identifier: str) -> str:
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")
    return identifier


def _quote_identifier(identifier: str) -> str:
    return f'"{_validate_identifier(identifier)}"'


def _relation(schema_name: str, table_name: str) -> str:
    return f"{_quote_identifier(schema_name)}.{_quote_identifier(table_name)}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_positive_int(value: Any) -> int | None:
    normalized_value = _normalize_int(value)
    if normalized_value is None:
        return None
    if normalized_value < 1:
        raise ValueError("scrape_limit must be greater than or equal to 1")
    return normalized_value


def _normalize_record_id(source_row: dict[str, Any]) -> str | None:
    for key in ("source_record_id", "film_id", "visa_number"):
        value = source_row.get(key)
        if value not in (None, ""):
            return str(value)
    title = source_row.get("original_name")
    year = source_row.get("cnc_agrement_year")
    if title:
        return f"{title}:{year}"
    return None


def _hash_record(record: dict[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AllocineAirbyteSource:
    def spec(self) -> dict[str, Any]:
        return {
            "documentationUrl": "https://docs.airbyte.com/platform/next/connector-development/custom-connectors",
            "connectionSpecification": CONNECTION_SPECIFICATION,
            "supportsIncremental": False,
            "supported_destination_sync_modes": ["append"],
        }

    def discover(self) -> dict[str, Any]:
        return {
            "streams": [
                {
                    "name": STREAM_NAME,
                    "json_schema": STREAM_JSON_SCHEMA,
                    "supported_sync_modes": ["full_refresh"],
                    "supported_destination_sync_modes": ["append"],
                    "namespace": DEFAULT_OUTPUT_SCHEMA,
                }
            ]
        }

    def check(self, raw_config: dict[str, Any]) -> tuple[bool, str]:
        config = ConnectorConfig.from_dict(raw_config)
        engine = create_engine(config.database_url)

        try:
            with engine.connect() as connection:
                connection.execute(text("select 1"))
                self._assert_input_table_exists(connection, config)
            return True, "Postgres connection ok. Input table reachable."
        finally:
            engine.dispose()

    def read(
        self,
        raw_config: dict[str, Any],
        catalog: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        config = ConnectorConfig.from_dict(raw_config)
        if catalog and not self._stream_selected(catalog):
            return []
        return asyncio.run(self._read_async(config))

    def sync_to_postgres(self, raw_config: dict[str, Any]) -> int:
        config = ConnectorConfig.from_dict(raw_config)
        records = asyncio.run(self._read_async(config))
        if not records:
            return 0
        self._insert_records(config, records)
        return len(records)

    async def _read_async(self, config: ConnectorConfig) -> list[dict[str, Any]]:
        source_rows = self._fetch_pending_rows(config)
        if not source_rows:
            return []

        scraper, browser_factory = self._load_scraping_dependencies()
        run_id = str(uuid.uuid4())
        total_rows = len(source_rows)
        summary_statuses = ["success", "not_found", "blocked", "error", "visa_mismatch"]
        status_counts = {status: 0 for status in summary_statuses}

        print(f"Allocine scraping started: {total_rows} pending rows to process.")

        # debug_pause_between_actions requires sequential execution
        n_sessions = 1 if config.debug_pause_between_actions else config.parallel_sessions
        chunks = [source_rows[i::n_sessions] for i in range(n_sessions) if source_rows[i::n_sessions]]

        chunk_results = await asyncio.gather(*(
            self._scrape_chunk(
                run_id=run_id,
                chunk=chunk,
                browser_factory=browser_factory,
                scraper=scraper,
                config=config,
                start_delay_s=i * 2.0,
                session_index=i,
            )
            for i, chunk in enumerate(chunks)
        ))
        records = [record for chunk_records in chunk_results for record in chunk_records]

        for record in records:
            status = record.get("scrape_status") or "error"
            status_counts[status] = status_counts.get(status, 0) + 1
            if status != "success":
                source_label = record.get("source_record_id") or record.get("visa_number")
                title = record.get("original_name") or "unknown-title"
                reason = record.get("error_message") or "no reason provided"
                print(
                    "Allocine scraping issue: "
                    f"status={status} "
                    f"source_record_id={source_label} "
                    f"title={title!r} "
                    f"reason={reason}"
                )

        print(f"Allocine scraping progress: {total_rows}/{total_rows} rows processed.")
        print(
            "Allocine scraping summary: "
            + ", ".join(
                f"{status}={status_counts.get(status, 0)}"
                for status in summary_statuses
            )
        )

        return records

    async def _scrape_chunk(
        self,
        run_id: str,
        chunk: list[dict[str, Any]],
        browser_factory: Any,
        scraper: Any,
        config: "ConnectorConfig",
        start_delay_s: float = 0.0,
        session_index: int = 0,
    ) -> list[dict[str, Any]]:
        """Process a list of rows in a single browser session, with inter-film delays."""
        records = []
        if start_delay_s:
            if config.verbose:
                print(f"[session {session_index}] Waiting {start_delay_s:.1f}s stagger delay before starting.")
            await asyncio.sleep(start_delay_s)
        if config.verbose:
            print(f"[session {session_index}] Connecting to browser...")
        async with browser_factory(
            ws_endpoint=config.playwright_ws_endpoint,
            headless=config.headless,
            debug_pause_between_actions=config.debug_pause_between_actions,
            verbose=config.verbose,
        ) as session:
            if config.verbose:
                print(f"[session {session_index}] Browser ready. Processing {len(chunk)} records.")
            for index, source_row in enumerate(chunk):
                if index > 0:
                    delay = random.uniform(2.0, 5.0)
                    if config.verbose:
                        print(f"[session {session_index}] Inter-film delay {delay:.1f}s...")
                    await asyncio.sleep(delay)
                label = (
                    source_row.get("original_name")
                    or source_row.get("visa_number")
                    or source_row.get("source_record_id")
                    or "?"
                )
                if config.verbose:
                    print(f"[session {session_index}] Record {index + 1}/{len(chunk)}: {label!r}")
                record = await self._scrape_one_record(
                    run_id=run_id,
                    session=session,
                    scraper=scraper,
                    source_row=source_row,
                    verbose=config.verbose,
                )
                status = record.get("scrape_status", "?")
                if config.verbose:
                    print(f"[session {session_index}] Record {index + 1}/{len(chunk)} done: {label!r} -> {status}")
                records.append(record)
        if config.verbose:
            print(f"[session {session_index}] Browser session closed.")
        return records

    def _load_scraping_dependencies(self):
        from ingestion.scraping.allocine.allocine_scraper import AllocineScraper
        from ingestion.scraping.browser import AsyncBrowserSession

        return AllocineScraper(), AsyncBrowserSession

    def _insert_records(
        self, config: ConnectorConfig, records: list[dict[str, Any]]
    ) -> None:
        engine = create_engine(config.database_url)
        insert_sql = text(f"""
            insert into {_relation(config.output_schema, config.output_table)} (
                run_id,
                extracted_at,
                source_record_id,
                visa_number,
                original_name,
                cnc_agrement_year,
                match_strategy,
                search_url,
                source_url,
                allocine_id,
                allocine_title,
                allocine_url,
                allocine_visa_number,
                release_date_raw,
                release_date,
                duration_raw,
                duration_minutes,
                genres,
                trailer_url,
                direction,
                casting,
                screenwriters,
                production,
                technical_team,
                soundtrack,
                distribution,
                companies,
                scrape_status,
                error_message,
                record_hash
            ) values (
                :run_id,
                :extracted_at,
                :source_record_id,
                :visa_number,
                :original_name,
                :cnc_agrement_year,
                :match_strategy,
                :search_url,
                :source_url,
                :allocine_id,
                :allocine_title,
                :allocine_url,
                :allocine_visa_number,
                :release_date_raw,
                :release_date,
                :duration_raw,
                :duration_minutes,
                cast(:genres as jsonb),
                :trailer_url,
                cast(:direction as jsonb),
                cast(:casting as jsonb),
                cast(:screenwriters as jsonb),
                cast(:production as jsonb),
                cast(:technical_team as jsonb),
                cast(:soundtrack as jsonb),
                cast(:distribution as jsonb),
                cast(:companies as jsonb),
                :scrape_status,
                :error_message,
                :record_hash
            )
            """)

        try:
            with engine.begin() as connection:
                self._ensure_output_table_exists(connection, config)
                connection.execute(
                    insert_sql,
                    [self._serialize_record_for_insert(record) for record in records],
                )
        finally:
            engine.dispose()

    def _serialize_record_for_insert(self, record: dict[str, Any]) -> dict[str, Any]:
        serialized = dict(record)
        for key in (
            "genres",
            "direction",
            "casting",
            "screenwriters",
            "production",
            "technical_team",
            "soundtrack",
            "distribution",
            "companies",
        ):
            value = serialized.get(key)
            serialized[key] = (
                json.dumps(value, ensure_ascii=False) if value is not None else None
            )
        return serialized

    def _fetch_pending_rows(self, config: ConnectorConfig) -> list[dict[str, Any]]:
        engine = create_engine(config.database_url)
        select_columns = [
            f"{_quote_identifier(config.input_id_column)} as source_record_id",
            f"{_quote_identifier(config.input_visa_column)} as visa_number",
            f"{_quote_identifier(config.input_title_column)} as original_name",
        ]
        if config.input_year_column:
            select_columns.append(
                f"{_quote_identifier(config.input_year_column)} as cnc_agrement_year"
            )
        if config.input_allocine_id_column:
            select_columns.append(
                f"{_quote_identifier(config.input_allocine_id_column)} as allocine_id"
            )
        if config.input_allocine_url_column:
            select_columns.append(
                f"{_quote_identifier(config.input_allocine_url_column)} as allocine_url"
            )

        query = text(
            f"select {', '.join(select_columns)} "
            f"from {_relation(config.input_schema, config.input_table)}"
        )

        try:
            with engine.begin() as connection:
                self._assert_input_table_exists(connection, config)
                self._ensure_output_table_exists(connection, config)
                rows = [dict(row._mapping) for row in connection.execute(query)]
                processed_ids = self._fetch_processed_ids(connection, config)
        finally:
            engine.dispose()

        pending_rows: list[dict[str, Any]] = []
        for row in rows:
            normalized_id = _normalize_record_id(row)
            row["source_record_id"] = normalized_id
            if normalized_id and normalized_id in processed_ids:
                continue
            pending_rows.append(row)

        # Shuffle pending rows so concurrent runs are less likely to pick the same records.
        random.shuffle(pending_rows)

        if config.scrape_limit is not None:
            return pending_rows[: config.scrape_limit]
        return pending_rows

    def _fetch_processed_ids(self, connection, config: ConnectorConfig) -> set[str]:
        if not self._table_exists(
            connection, config.output_schema, config.output_table
        ):
            return set()

        query = text(
            f"select distinct source_record_id "
            f"from {_relation(config.output_schema, config.output_table)} "
            "where lower(coalesce(scrape_status, '')) in :completed_statuses"
        ).bindparams(bindparam("completed_statuses", expanding=True))
        return {
            str(value)
            for value in connection.execute(
                query, {"completed_statuses": config.completed_statuses}
            ).scalars()
            if value not in (None, "")
        }

    def _assert_input_table_exists(self, connection, config: ConnectorConfig) -> None:
        if not self._table_exists(connection, config.input_schema, config.input_table):
            raise RuntimeError(
                f"Input table {_relation(config.input_schema, config.input_table)} not found."
            )

    def _ensure_output_table_exists(self, connection, config: ConnectorConfig) -> None:
        if self._table_exists(connection, config.output_schema, config.output_table):
            return

        if not self._schema_exists(connection, config.output_schema):
            connection.execute(
                text(f"create schema {_quote_identifier(config.output_schema)}")
            )
        connection.execute(text(f"""
                create table if not exists {_relation(config.output_schema, config.output_table)} (
                    run_id text,
                    extracted_at timestamptz,
                    source_record_id text,
                    visa_number text,
                    original_name text,
                    cnc_agrement_year integer,
                    match_strategy text,
                    search_url text,
                    source_url text,
                    allocine_id integer,
                    allocine_title text,
                    allocine_url text,
                    allocine_visa_number text,
                    release_date_raw text,
                    release_date date,
                    duration_raw text,
                    duration_minutes integer,
                    genres jsonb,
                    trailer_url text,
                    direction jsonb,
                    casting jsonb,
                    screenwriters jsonb,
                    production jsonb,
                    technical_team jsonb,
                    soundtrack jsonb,
                    distribution jsonb,
                    companies jsonb,
                    scrape_status text,
                    error_message text,
                    record_hash text
                )
                """))
        connection.execute(text(f"""
                create index if not exists idx_{config.output_table}_source_record_id
                on {_relation(config.output_schema, config.output_table)} (source_record_id)
                """))
        connection.execute(text(f"""
                create index if not exists idx_{config.output_table}_scrape_status
                on {_relation(config.output_schema, config.output_table)} (scrape_status)
                """))
        connection.execute(text(f"""
                create index if not exists idx_{config.output_table}_extracted_at
                on {_relation(config.output_schema, config.output_table)} (extracted_at)
                """))

    def _schema_exists(self, connection, schema_name: str) -> bool:
        query = text("""
            select 1
            from information_schema.schemata
            where schema_name = :schema_name
            """)
        return connection.execute(query, {"schema_name": schema_name}).scalar() == 1

    def _table_exists(self, connection, schema_name: str, table_name: str) -> bool:
        query = text("""
            select 1
            from information_schema.tables
            where table_schema = :schema_name
              and table_name = :table_name
            """)
        return (
            connection.execute(
                query, {"schema_name": schema_name, "table_name": table_name}
            ).scalar()
            == 1
        )

    def _stream_selected(self, catalog: dict[str, Any]) -> bool:
        streams = catalog.get("streams") or catalog.get("configuredStreams") or []
        for stream in streams:
            candidate = stream.get("stream", stream)
            if candidate.get("name") == STREAM_NAME:
                return True
        return False

    async def _scrape_one_record(
        self,
        run_id: str,
        session: Any,
        scraper: Any,
        source_row: dict[str, Any],
        verbose: bool = False,
    ) -> dict[str, Any]:
        extracted_at = _now_iso()
        source_record_id = _normalize_record_id(source_row)
        visa_number = source_row.get("visa_number")
        original_name = source_row.get("original_name")
        cnc_agrement_year = _normalize_int(source_row.get("cnc_agrement_year"))
        allocine_id = _normalize_int(source_row.get("allocine_id"))
        allocine_url = source_row.get("allocine_url")
        match_strategy = "provided_allocine_id" if allocine_id else "search"
        search_url = None
        if allocine_id and not allocine_url:
            allocine_url = scraper.FILM_URL.format(allocine_film_id=allocine_id)

        base_record = {
            "run_id": run_id,
            "extracted_at": extracted_at,
            "source_record_id": source_record_id,
            "visa_number": str(visa_number) if visa_number not in (None, "") else None,
            "original_name": (
                str(original_name) if original_name not in (None, "") else None
            ),
            "cnc_agrement_year": cnc_agrement_year,
            "match_strategy": match_strategy,
            "search_url": None,
            "source_url": allocine_url,
            "allocine_id": allocine_id,
            "allocine_title": None,
            "allocine_url": allocine_url,
            "allocine_visa_number": None,
            "release_date_raw": None,
            "release_date": None,
            "duration_raw": None,
            "duration_minutes": None,
            "genres": None,
            "trailer_url": None,
            "direction": None,
            "casting": None,
            "screenwriters": None,
            "production": None,
            "technical_team": None,
            "soundtrack": None,
            "distribution": None,
            "companies": None,
            "scrape_status": "error",
            "error_message": None,
        }

        try:
            if not allocine_id:
                if not original_name:
                    base_record["scrape_status"] = "error"
                    base_record["error_message"] = (
                        "Missing original_name. Cannot search Allocine."
                    )
                    base_record["record_hash"] = _hash_record(base_record)
                    return base_record

                search_term = f"{original_name} {cnc_agrement_year or ''}".strip()
                search_url = scraper.SEARCH_URL.format(
                    film_title_url_styled=scraper._reformat_str_for_url(search_term)
                )
                if verbose:
                    print(f"  [search] {search_term!r} -> {search_url}")
                search_html = await session.fetch_html(search_url)
                search_result = scraper.extract_searched_first_film(search_html)
                base_record["search_url"] = search_url

                if not search_result:
                    if verbose:
                        print(f"  [search] No result found for {search_term!r}")
                    base_record["scrape_status"] = "not_found"
                    base_record["source_url"] = search_url
                    base_record["record_hash"] = _hash_record(base_record)
                    return base_record

                allocine_id = search_result["id"]
                allocine_url = f"{scraper.BASE_URL}{search_result['link']}"
                if verbose:
                    print(f"  [search] Found: allocine_id={allocine_id}, title={search_result['title']!r}")
                base_record["allocine_id"] = allocine_id
                base_record["allocine_title"] = search_result["title"]
                base_record["allocine_url"] = allocine_url
                base_record["source_url"] = allocine_url

            details_url = scraper.FILM_URL.format(allocine_film_id=allocine_id)
            casting_url = scraper.FILM_CASTING_URL.format(allocine_film_id=allocine_id)
            if verbose:
                print(f"  [details] {details_url}")
            details_html = await session.fetch_html(details_url)
            if verbose:
                print(f"  [casting] {casting_url}")
            casting_html = await session.fetch_html(casting_url)
            details = scraper.extract_film_details(details_html)
            casting = scraper.extract_film_casting(casting_html)

            allocine_visa_number = details.get("allocine_visa_number")
            release_date_raw = details.get("release_date")
            release_date = parse_release_date(release_date_raw)
            duration_raw = details.get("duration")
            duration_minutes = parse_duration(duration_raw)

            base_record.update(
                {
                    "source_url": allocine_url or base_record["source_url"],
                    "allocine_url": allocine_url or base_record["allocine_url"],
                    "allocine_visa_number": allocine_visa_number,
                    "release_date_raw": release_date_raw,
                    "release_date": release_date.isoformat() if release_date else None,
                    "duration_raw": duration_raw,
                    "duration_minutes": duration_minutes,
                    "genres": details.get("genres"),
                    "trailer_url": details.get("trailer_url"),
                    "direction": casting.get("Direction"),
                    "casting": casting.get("Casting"),
                    "screenwriters": casting.get("Scénaristes"),
                    "production": casting.get("Production"),
                    "technical_team": casting.get("Equipe technique"),
                    "soundtrack": casting.get("Soundtrack"),
                    "distribution": casting.get("Distribution"),
                    "companies": casting.get("Sociétés"),
                }
            )

            row_visa = str(visa_number) if visa_number not in (None, "") else None
            allocine_visa = (
                str(allocine_visa_number)
                if allocine_visa_number not in (None, "")
                else None
            )
            if row_visa and allocine_visa and row_visa != allocine_visa:
                base_record["scrape_status"] = "visa_mismatch"
                base_record["error_message"] = (
                    f"Allocine visa {allocine_visa} differs from source visa {row_visa}."
                )
            else:
                base_record["scrape_status"] = "success"

        except WebsiteBlockedError as exc:
            base_record["scrape_status"] = "blocked"
            base_record["error_message"] = str(exc)
        except Exception as exc:
            base_record["scrape_status"] = "error"
            base_record["error_message"] = str(exc)

        base_record["record_hash"] = _hash_record(base_record)
        return base_record
