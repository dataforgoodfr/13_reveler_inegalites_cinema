"""CNC-driven Mubi scraper.

Unlike the discovery-driven job in ``ingestion/scraping/mubi`` (which crawls
every festival x year x page on Mubi and filters to CNC films downstream in
dbt), this job is *input-driven* like the Allocine scraper: it reads the CNC
reference list ``raw.id_matching`` and scrapes only the films CNC has agreed to.

Two phases, both writing the SAME output tables as the discovery job
(``raw.mubi_film_awards`` and ``raw.mubi_festival_films``), so downstream dbt
models are unchanged:

  Phase A — for each CNC film with a numeric ``ID_MUBI``, fetch
            ``/fr/films/{mubi_id}/awards`` and read the structured
            ``pageProps.awards`` payload. Write one ``mubi_film_awards`` row per
            award. Collect the distinct ``(festival_slug, year)`` editions whose
            ``industry_event.type == 'festival'``.

  Phase B — scrape only those collected ``(festival_slug, year)`` editions
            (not all festivals x all years) with the existing edition HTML
            scraper, writing ``mubi_festival_films``.

Locale: every page is fetched on the ``/fr/`` locale so the parsed
``distinction`` / ``award`` / ``festival`` strings stay French, matching the
rows the discovery job already wrote into the same tables. The festival-edition
scrape is keyed off ``industry_event.slug`` (language-invariant), never the
localized name.

Deduplication is enforced at three levels:
  1. Skip CNC films already completed (``success``/``no_awards``) in
     ``mubi_film_awards`` and editions already completed in
     ``mubi_festival_films`` — no re-scraping.
  2. Within a run, each ``(festival_slug, year)`` edition is scraped at most once.
  3. Before insert, drop any record whose ``record_hash`` already exists in the
     target table, so re-runs / overlapping CNC films never append duplicate
     rows.
"""

import asyncio
import builtins
import hashlib
import json
import os
import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

from ingestion.scraping.browser import WebsiteBlockedError

print = partial(builtins.print, flush=True)

FESTIVAL_FILMS_STREAM = "mubi_festival_films"
FILM_AWARDS_STREAM = "mubi_film_awards"
DEFAULT_OUTPUT_SCHEMA = "raw"
DEFAULT_FESTIVAL_FILMS_TABLE = FESTIVAL_FILMS_STREAM
DEFAULT_FILM_AWARDS_TABLE = FILM_AWARDS_STREAM
DEFAULT_INPUT_SCHEMA = "raw"
DEFAULT_INPUT_TABLE = "id_matching"
DEFAULT_INPUT_MUBI_ID_COLUMN = "ID_MUBI"
DEFAULT_MAX_PAGES_PER_EDITION = 100
DEFAULT_MAX_REQUESTS_PER_SESSION = 6
DEFAULT_RECORD_TIMEOUT_SECONDS = 60.0
DEFAULT_FETCH_MAX_ATTEMPTS = 3
DEFAULT_FETCH_RETRY_BASE_DELAY_SECONDS = 3.0
DEFAULT_COMPLETED_FESTIVAL_STATUSES = ["success", "empty"]
DEFAULT_COMPLETED_AWARD_STATUSES = ["success", "no_awards"]
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


CONNECTION_SPECIFICATION = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Mubi CNC Airbyte Source",
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
            "enum": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"],
        },
        "input_schema": {
            "type": "string",
            "title": "Input schema (CNC reference)",
            "default": DEFAULT_INPUT_SCHEMA,
        },
        "input_table": {
            "type": "string",
            "title": "Input table (CNC reference)",
            "default": DEFAULT_INPUT_TABLE,
            "description": "Table holding the CNC films. Only rows with a non-null Mubi id are scraped.",
        },
        "input_mubi_id_column": {
            "type": "string",
            "title": "Mubi id column in the input table",
            "default": DEFAULT_INPUT_MUBI_ID_COLUMN,
        },
        "output_schema": {
            "type": "string",
            "title": "Output schema",
            "default": DEFAULT_OUTPUT_SCHEMA,
        },
        "festival_films_table": {
            "type": "string",
            "title": "Festival films output table",
            "default": DEFAULT_FESTIVAL_FILMS_TABLE,
        },
        "film_awards_table": {
            "type": "string",
            "title": "Film awards output table",
            "default": DEFAULT_FILM_AWARDS_TABLE,
        },
        "max_pages_per_edition": {
            "type": "integer",
            "title": "Max pages to scrape per festival-year edition",
            "default": DEFAULT_MAX_PAGES_PER_EDITION,
            "minimum": 1,
        },
        "completed_festival_statuses": {
            "type": "array",
            "title": "Statuses considered processed for festival films",
            "default": DEFAULT_COMPLETED_FESTIVAL_STATUSES,
            "items": {"type": "string"},
        },
        "completed_award_statuses": {
            "type": "array",
            "title": "Statuses considered processed for film awards",
            "default": DEFAULT_COMPLETED_AWARD_STATUSES,
            "items": {"type": "string"},
        },
        "scrape_limit": {
            "type": ["integer", "null"],
            "title": "Maximum number of CNC films to scrape in Phase A",
            "minimum": 1,
            "description": "Optional debug limit applied after filtering already processed films.",
        },
        "record_timeout_seconds": {
            "type": "number",
            "title": "Per-request timeout in seconds",
            "default": DEFAULT_RECORD_TIMEOUT_SECONDS,
            "minimum": 0,
        },
        "fetch_max_attempts": {
            "type": "integer",
            "title": "Attempts per page fetch before recording an error",
            "default": DEFAULT_FETCH_MAX_ATTEMPTS,
            "minimum": 1,
        },
        "fetch_retry_base_delay_seconds": {
            "type": "number",
            "title": "Base backoff delay between fetch retries",
            "default": DEFAULT_FETCH_RETRY_BASE_DELAY_SECONDS,
            "minimum": 0,
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
        },
        "max_requests_per_session": {
            "type": "integer",
            "title": "Restart browser session after this many requests",
            "default": DEFAULT_MAX_REQUESTS_PER_SESSION,
            "minimum": 1,
        },
        "inter_request_delay_min_seconds": {
            "type": "number",
            "title": "Minimum delay between requests",
            "default": 2.0,
            "minimum": 0,
        },
        "inter_request_delay_max_seconds": {
            "type": "number",
            "title": "Maximum delay between requests",
            "default": 5.0,
            "minimum": 0,
        },
        "verbose": {
            "type": "boolean",
            "title": "Verbose logging",
            "default": False,
        },
    },
}


@dataclass
class ConnectorConfig:
    database_url: str
    input_schema: str
    input_table: str
    input_mubi_id_column: str
    output_schema: str
    festival_films_table: str
    film_awards_table: str
    max_pages_per_edition: int
    completed_festival_statuses: list[str]
    completed_award_statuses: list[str]
    scrape_limit: int | None
    record_timeout_seconds: float
    fetch_max_attempts: int
    fetch_retry_base_delay_seconds: float
    playwright_ws_endpoint: str | None
    headless: bool
    max_requests_per_session: int
    inter_request_delay_min_seconds: float
    inter_request_delay_max_seconds: float
    verbose: bool

    @classmethod
    def from_dict(cls, raw_config: dict[str, Any]) -> "ConnectorConfig":
        database_url = raw_config.get("database_url") or _build_database_url(raw_config)
        delay_min = float(raw_config.get("inter_request_delay_min_seconds", 2.0))
        delay_max = float(raw_config.get("inter_request_delay_max_seconds", 5.0))
        if delay_max < delay_min:
            raise ValueError("inter_request_delay_max_seconds must be >= inter_request_delay_min_seconds")

        values = {
            "database_url": database_url,
            "input_schema": raw_config.get("input_schema", DEFAULT_INPUT_SCHEMA),
            "input_table": raw_config.get("input_table", DEFAULT_INPUT_TABLE),
            "input_mubi_id_column": raw_config.get("input_mubi_id_column", DEFAULT_INPUT_MUBI_ID_COLUMN),
            "output_schema": raw_config.get("output_schema", DEFAULT_OUTPUT_SCHEMA),
            "festival_films_table": raw_config.get("festival_films_table", DEFAULT_FESTIVAL_FILMS_TABLE),
            "film_awards_table": raw_config.get("film_awards_table", DEFAULT_FILM_AWARDS_TABLE),
            "max_pages_per_edition": max(1, int(raw_config.get("max_pages_per_edition", DEFAULT_MAX_PAGES_PER_EDITION))),
            "completed_festival_statuses": [
                str(s).lower() for s in (raw_config.get("completed_festival_statuses") or DEFAULT_COMPLETED_FESTIVAL_STATUSES)
            ],
            "completed_award_statuses": [
                str(s).lower() for s in (raw_config.get("completed_award_statuses") or DEFAULT_COMPLETED_AWARD_STATUSES)
            ],
            "scrape_limit": _normalize_positive_int(raw_config.get("scrape_limit")),
            "record_timeout_seconds": max(0.0, float(raw_config.get("record_timeout_seconds", DEFAULT_RECORD_TIMEOUT_SECONDS))),
            "fetch_max_attempts": max(1, int(raw_config.get("fetch_max_attempts", DEFAULT_FETCH_MAX_ATTEMPTS))),
            "fetch_retry_base_delay_seconds": max(0.0, float(raw_config.get("fetch_retry_base_delay_seconds", DEFAULT_FETCH_RETRY_BASE_DELAY_SECONDS))),
            "playwright_ws_endpoint": raw_config.get("playwright_ws_endpoint") or os.getenv("PLAYWRIGHT_WS_ENDPOINT"),
            "headless": bool(raw_config.get("headless", True)),
            "max_requests_per_session": max(1, int(raw_config.get("max_requests_per_session", DEFAULT_MAX_REQUESTS_PER_SESSION))),
            "inter_request_delay_min_seconds": delay_min,
            "inter_request_delay_max_seconds": delay_max,
            "verbose": bool(raw_config.get("verbose", False)),
        }

        for key, value in values.items():
            if (key.endswith("_table") or key.endswith("_schema") or key.endswith("_column")) and value:
                _validate_identifier(value)

        return cls(**values)


def _build_database_url(raw_config: dict[str, Any]) -> str:
    required = ["postgres_host", "postgres_port", "postgres_db", "postgres_user", "postgres_password"]
    missing = [k for k in required if raw_config.get(k) in (None, "")]
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


def _normalize_positive_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    if n < 1:
        raise ValueError("scrape_limit must be >= 1")
    return n


def _hash_record(record: dict[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class MubiCncAirbyteSource:
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
                    "name": FESTIVAL_FILMS_STREAM,
                    "json_schema": _FESTIVAL_FILMS_SCHEMA,
                    "supported_sync_modes": ["full_refresh"],
                    "supported_destination_sync_modes": ["append"],
                    "namespace": DEFAULT_OUTPUT_SCHEMA,
                },
                {
                    "name": FILM_AWARDS_STREAM,
                    "json_schema": _FILM_AWARDS_SCHEMA,
                    "supported_sync_modes": ["full_refresh"],
                    "supported_destination_sync_modes": ["append"],
                    "namespace": DEFAULT_OUTPUT_SCHEMA,
                },
            ]
        }

    def check(self, raw_config: dict[str, Any]) -> tuple[bool, str]:
        config = ConnectorConfig.from_dict(raw_config)
        engine = create_engine(config.database_url)
        try:
            with engine.connect() as conn:
                conn.execute(text("select 1"))
                if not _table_exists(conn, config.input_schema, config.input_table):
                    return False, (
                        f"Input table {config.input_schema}.{config.input_table} not found."
                    )
            return True, "Postgres connection ok. CNC input table reachable."
        except Exception as exc:
            return False, str(exc)
        finally:
            engine.dispose()

    def sync_to_postgres(self, raw_config: dict[str, Any]) -> dict[str, int]:
        config = ConnectorConfig.from_dict(raw_config)

        # Phase A — awards per CNC film. Returns the inserted award records and
        # the distinct (festival_slug, year) editions to scrape in Phase B.
        award_records, editions = asyncio.run(self._scrape_cnc_film_awards(config))

        if award_records:
            self._insert_deduped(
                config,
                config.film_awards_table,
                award_records,
                _insert_film_awards,
            )

        # Phase B — only the festival editions referenced by CNC films' awards.
        festival_records = asyncio.run(self._scrape_festival_editions(config, editions))

        if festival_records:
            self._insert_deduped(
                config,
                config.festival_films_table,
                festival_records,
                _insert_festival_films,
            )

        festival_inserted = len([r for r in festival_records if r["scrape_status"] == "success"])
        awards_inserted = len([r for r in award_records if r["scrape_status"] == "success"])
        print(
            f"Mubi CNC scraping complete: "
            f"{awards_inserted} film award records, "
            f"{festival_inserted} festival film records (before hash dedup)."
        )
        return {"festival_films": len(festival_records), "film_awards": len(award_records)}

    # --- Phase A: awards per CNC film ---

    async def _scrape_cnc_film_awards(
        self, config: ConnectorConfig
    ) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
        from ingestion.scraping.mubi.mubi_scraper import MubiPageScraper
        from ingestion.scraping.browser import AsyncBrowserSession

        scraper = MubiPageScraper()
        run_id = str(uuid.uuid4())

        engine = create_engine(config.database_url)
        try:
            with engine.begin() as conn:
                _ensure_schema(conn, config.output_schema)
                _ensure_festival_films_table(conn, config)
                _ensure_film_awards_table(conn, config)
                pending_ids = _fetch_pending_mubi_ids(conn, config)
        finally:
            engine.dispose()

        if config.scrape_limit is not None:
            pending_ids = pending_ids[: config.scrape_limit]

        if not pending_ids:
            print("Mubi CNC film awards: nothing pending.")
            return [], []

        print(f"Mubi CNC film awards: {len(pending_ids)} CNC films to scrape.")

        records: list[dict[str, Any]] = []
        # (slug, year) editions of type 'festival' collected from the awards.
        editions: set[tuple[str, str]] = set()
        request_count = 0
        session_cm = None
        session = None

        async def open_session():
            nonlocal session_cm, session
            session_cm = AsyncBrowserSession(
                ws_endpoint=config.playwright_ws_endpoint,
                headless=config.headless,
                verbose=config.verbose,
            )
            session = await session_cm.__aenter__()

        async def close_session():
            nonlocal session_cm, session
            if session_cm is not None:
                try:
                    await session_cm.__aexit__(None, None, None)
                finally:
                    session_cm = None
                    session = None

        await open_session()
        try:
            for i, mubi_id in enumerate(pending_ids):
                if i > 0:
                    delay = random.uniform(
                        config.inter_request_delay_min_seconds,
                        config.inter_request_delay_max_seconds,
                    )
                    await asyncio.sleep(delay)

                extracted_at = _now_iso()
                url = scraper.FILM_ALL_AWARDS_BY_ID_URL.format(mubi_id=mubi_id)
                if config.verbose:
                    print(f"[awards] mubi_id={mubi_id}: {url}")

                html, last_error = await self._fetch_with_retry(
                    session, url, config, label=f"awards mubi_id={mubi_id}"
                )

                try:
                    if last_error is not None:
                        raise last_error

                    identity = scraper.extract_film_identity(html)
                    film_link = identity.get("film_link")
                    resolved_id = identity.get("mubi_id") or mubi_id
                    awards = scraper.extract_film_awards_structured(html)

                    if not awards:
                        record = _award_record(
                            run_id, extracted_at, film_link, resolved_id,
                            festival=None, year=None, distinction=None, award=None,
                            scrape_status="no_awards", error_message=None,
                        )
                        records.append(record)
                        print(f"[awards] mubi_id={mubi_id}: no awards (film_link={film_link})")
                    else:
                        for a in awards:
                            records.append(_award_record(
                                run_id, extracted_at, film_link, resolved_id,
                                festival=a.get("festival"), year=a.get("year"),
                                distinction=a.get("distinction"), award=a.get("award"),
                                scrape_status="success", error_message=None,
                            ))
                            slug = a.get("event_slug")
                            yr = a.get("year")
                            if a.get("event_type") == "festival" and slug and yr:
                                editions.add((slug, str(yr)))
                        print(f"[awards] mubi_id={mubi_id}: {len(awards)} awards (film_link={film_link})")

                except WebsiteBlockedError as exc:
                    records.append(_award_record(
                        run_id, extracted_at, None, mubi_id,
                        festival=None, year=None, distinction=None, award=None,
                        scrape_status="blocked", error_message=str(exc),
                    ))
                    print(f"[awards] mubi_id={mubi_id}: blocked — restarting session")
                    await close_session()
                    await open_session()
                    request_count = 0
                    continue

                except asyncio.TimeoutError as exc:
                    records.append(_award_record(
                        run_id, extracted_at, None, mubi_id,
                        festival=None, year=None, distinction=None, award=None,
                        scrape_status="error",
                        error_message=str(exc) or f"Timeout after {config.record_timeout_seconds:.0f}s",
                    ))
                    print(f"[awards] mubi_id={mubi_id}: timeout after {config.fetch_max_attempts} attempts")

                except Exception as exc:
                    records.append(_award_record(
                        run_id, extracted_at, None, mubi_id,
                        festival=None, year=None, distinction=None, award=None,
                        scrape_status="error", error_message=str(exc),
                    ))
                    print(f"[awards] mubi_id={mubi_id}: error — {exc}")

                request_count += 1
                if request_count >= config.max_requests_per_session:
                    await close_session()
                    await open_session()
                    request_count = 0
        finally:
            await close_session()

        _print_status_summary("Mubi CNC film awards", records)
        print(f"Mubi CNC: {len(editions)} distinct festival editions referenced by CNC films.")
        return records, sorted(editions)

    # --- Phase B: only the festival editions referenced by CNC films ---

    async def _scrape_festival_editions(
        self, config: ConnectorConfig, editions: list[tuple[str, str]]
    ) -> list[dict[str, Any]]:
        from ingestion.scraping.mubi.mubi_scraper import MubiPageScraper
        from ingestion.scraping.browser import AsyncBrowserSession

        if not editions:
            print("Mubi CNC festival films: no editions to scrape.")
            return []

        scraper = MubiPageScraper()
        run_id = str(uuid.uuid4())

        engine = create_engine(config.database_url)
        try:
            with engine.connect() as conn:
                processed_page_combos = _fetch_processed_page_combos(conn, config)
                edition_empty_boundaries = _fetch_edition_empty_boundaries(conn, config)
        finally:
            engine.dispose()

        # Build the pending (slug, year, page) list, skipping editions already
        # completed in a prior run and pages past a known empty boundary.
        pending: list[tuple[str, int, int]] = []
        for slug, year_str in editions:
            try:
                year = int(year_str)
            except (TypeError, ValueError):
                continue
            empty_from = edition_empty_boundaries.get((slug, year))
            last_page = config.max_pages_per_edition
            if empty_from is not None:
                last_page = min(last_page, empty_from - 1)
            for page in range(1, last_page + 1):
                if (slug, year, page) not in processed_page_combos:
                    pending.append((slug, year, page))

        if not pending:
            print("Mubi CNC festival films: nothing pending (all editions already scraped).")
            return []

        print(f"Mubi CNC festival films: {len(pending)} (festival, year, page) combos to scrape.")

        records: list[dict[str, Any]] = []
        request_count = 0
        session_cm = None
        session = None
        # Editions whose pages have run out this run — pending is ordered by page
        # within each edition, so once a page is empty every higher page is too.
        exhausted_editions: set[tuple] = set()

        async def open_session():
            nonlocal session_cm, session
            session_cm = AsyncBrowserSession(
                ws_endpoint=config.playwright_ws_endpoint,
                headless=config.headless,
                verbose=config.verbose,
            )
            session = await session_cm.__aenter__()

        async def close_session():
            nonlocal session_cm, session
            if session_cm is not None:
                try:
                    await session_cm.__aexit__(None, None, None)
                finally:
                    session_cm = None
                    session = None

        await open_session()
        try:
            for i, (slug, year, page) in enumerate(pending):
                if (slug, year) in exhausted_editions:
                    continue

                if i > 0:
                    delay = random.uniform(
                        config.inter_request_delay_min_seconds,
                        config.inter_request_delay_max_seconds,
                    )
                    await asyncio.sleep(delay)

                extracted_at = _now_iso()
                url = scraper.FESTIVAL_EDITION_ALL_FILMS_URL.format(
                    festival=slug, page_num=page, year=year
                )
                if config.verbose:
                    print(f"[films] {slug} {year} p{page}: {url}")

                base = {
                    "run_id": run_id,
                    "extracted_at": extracted_at,
                    "festival_slug": slug,
                    "festival_name": slug,
                    "year": year,
                    "page_num": page,
                }

                html, last_error = await self._fetch_with_retry(
                    session, url, config, label=f"films {slug} {year} p{page}"
                )

                try:
                    if last_error is not None:
                        raise last_error

                    films = scraper.extract_festival_edition_all_films(html)

                    if not films:
                        record = {
                            **base,
                            "title": None, "director": None, "country": None,
                            "nominations": None, "film_link": None,
                            "scrape_status": "empty", "error_message": None,
                        }
                        record["record_hash"] = _hash_record(record)
                        records.append(record)
                        exhausted_editions.add((slug, year))
                        print(f"[films] {slug} {year} p{page}: empty — skipping remaining pages")
                    else:
                        for film in films:
                            record = {
                                **base,
                                "title": film.get("title"),
                                "director": film.get("director"),
                                "country": film.get("country"),
                                "nominations": film.get("nominations"),
                                "film_link": film.get("link"),
                                "scrape_status": "success",
                                "error_message": None,
                            }
                            record["record_hash"] = _hash_record(record)
                            records.append(record)
                        print(f"[films] {slug} {year} p{page}: {len(films)} films")

                except WebsiteBlockedError as exc:
                    record = {
                        **base,
                        "title": None, "director": None, "country": None,
                        "nominations": None, "film_link": None,
                        "scrape_status": "blocked", "error_message": str(exc),
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[films] {slug} {year} p{page}: blocked — restarting session")
                    await close_session()
                    await open_session()
                    request_count = 0
                    continue

                except asyncio.TimeoutError as exc:
                    record = {
                        **base,
                        "title": None, "director": None, "country": None,
                        "nominations": None, "film_link": None,
                        "scrape_status": "error",
                        "error_message": str(exc) or f"Timeout after {config.record_timeout_seconds:.0f}s",
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[films] {slug} {year} p{page}: timeout after {config.fetch_max_attempts} attempts")

                except Exception as exc:
                    record = {
                        **base,
                        "title": None, "director": None, "country": None,
                        "nominations": None, "film_link": None,
                        "scrape_status": "error", "error_message": str(exc),
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[films] {slug} {year} p{page}: error — {exc}")

                request_count += 1
                if request_count >= config.max_requests_per_session:
                    await close_session()
                    await open_session()
                    request_count = 0
        finally:
            await close_session()

        _print_status_summary("Mubi CNC festival films", records)
        return records

    async def _fetch_with_retry(
        self, session: Any, url: str, config: ConnectorConfig, label: str
    ) -> tuple[str | None, Exception | None]:
        """Fetch a URL with linear backoff on transient errors.

        WebsiteBlockedError is not transient — it stops retrying immediately and
        is returned so the caller can restart the browser session.
        """
        html = None
        last_error: Exception | None = None
        for attempt in range(1, config.fetch_max_attempts + 1):
            try:
                task = session.fetch_html(url)
                if config.record_timeout_seconds > 0:
                    html = await asyncio.wait_for(task, timeout=config.record_timeout_seconds)
                else:
                    html = await task
                return html, None
            except WebsiteBlockedError as exc:
                return None, exc
            except asyncio.TimeoutError:
                last_error = asyncio.TimeoutError(
                    f"Timeout after {config.record_timeout_seconds:.0f}s"
                )
            except Exception as exc:
                last_error = exc

            if attempt < config.fetch_max_attempts:
                backoff = config.fetch_retry_base_delay_seconds * attempt
                print(
                    f"[{label}] attempt {attempt}/{config.fetch_max_attempts} "
                    f"failed ({last_error}); retrying in {backoff:.0f}s"
                )
                if backoff > 0:
                    await asyncio.sleep(backoff)

        return html, last_error

    def _insert_deduped(self, config, table, records, insert_fn) -> None:
        """Insert records whose record_hash is not already in the target table.

        Filters in-batch duplicates and rows whose hash already exists, so
        re-runs and CNC films sharing a festival edition never append duplicate
        rows into the append-only tables.
        """
        engine = create_engine(config.database_url)
        try:
            with engine.begin() as conn:
                existing = _fetch_existing_hashes(conn, config.output_schema, table)
                fresh: list[dict[str, Any]] = []
                seen: set[str] = set()
                for r in records:
                    h = r.get("record_hash")
                    if not h or h in existing or h in seen:
                        continue
                    seen.add(h)
                    fresh.append(r)
                skipped = len(records) - len(fresh)
                if skipped:
                    print(f"Mubi CNC: skipped {skipped} duplicate rows for {table} (record_hash already present).")
                if fresh:
                    insert_fn(conn, config, fresh)
                    print(f"Mubi CNC: inserted {len(fresh)} rows into {config.output_schema}.{table}.")
        finally:
            engine.dispose()


# --- record builders ---

def _award_record(
    run_id, extracted_at, film_link, mubi_id, *,
    festival, year, distinction, award, scrape_status, error_message,
) -> dict[str, Any]:
    record = {
        "run_id": run_id,
        "extracted_at": extracted_at,
        "film_link": film_link,
        "mubi_id": mubi_id,
        "festival": festival,
        "year": year,
        "distinction": distinction,
        "award": award,
        "scrape_status": scrape_status,
        "error_message": error_message,
    }
    record["record_hash"] = _hash_record(record)
    return record


def _print_status_summary(prefix: str, records: list[dict[str, Any]]) -> None:
    summary: dict[str, int] = {}
    for r in records:
        s = r["scrape_status"]
        summary[s] = summary.get(s, 0) + 1
    print(f"{prefix} summary: " + ", ".join(f"{s}={n}" for s, n in summary.items()))


# --- DB helpers ---

def _ensure_schema(conn, schema_name: str) -> None:
    exists = conn.execute(text(
        "select 1 from information_schema.schemata where schema_name = :s"
    ), {"s": schema_name}).scalar()
    if not exists:
        conn.execute(text(f"create schema {_quote_identifier(schema_name)}"))


def _table_exists(conn, schema_name: str, table_name: str) -> bool:
    return conn.execute(text(
        "select 1 from information_schema.tables "
        "where table_schema = :s and table_name = :t"
    ), {"s": schema_name, "t": table_name}).scalar() == 1


def _ensure_festival_films_table(conn, config: ConnectorConfig) -> None:
    rel = _relation(config.output_schema, config.festival_films_table)
    if _table_exists(conn, config.output_schema, config.festival_films_table):
        return
    conn.execute(text(f"""
        create table if not exists {rel} (
            run_id text,
            extracted_at timestamptz,
            festival_slug text,
            festival_name text,
            year integer,
            page_num integer,
            title text,
            director text,
            country text,
            nominations text,
            film_link text,
            scrape_status text,
            error_message text,
            record_hash text
        )
    """))
    t = config.festival_films_table
    conn.execute(text(f"create index if not exists idx_{t}_slug_year_page on {rel} (festival_slug, year, page_num)"))
    conn.execute(text(f"create index if not exists idx_{t}_film_link on {rel} (film_link)"))
    conn.execute(text(f"create index if not exists idx_{t}_scrape_status on {rel} (scrape_status)"))
    conn.execute(text(f"create index if not exists idx_{t}_extracted_at on {rel} (extracted_at)"))


def _ensure_film_awards_table(conn, config: ConnectorConfig) -> None:
    rel = _relation(config.output_schema, config.film_awards_table)
    if _table_exists(conn, config.output_schema, config.film_awards_table):
        return
    conn.execute(text(f"""
        create table if not exists {rel} (
            run_id text,
            extracted_at timestamptz,
            film_link text,
            mubi_id integer,
            festival text,
            year text,
            distinction text,
            award text,
            scrape_status text,
            error_message text,
            record_hash text
        )
    """))
    t = config.film_awards_table
    conn.execute(text(f"create index if not exists idx_{t}_film_link on {rel} (film_link)"))
    conn.execute(text(f"create index if not exists idx_{t}_scrape_status on {rel} (scrape_status)"))
    conn.execute(text(f"create index if not exists idx_{t}_extracted_at on {rel} (extracted_at)"))


def _fetch_pending_mubi_ids(conn, config: ConnectorConfig) -> list[int]:
    """CNC films' Mubi ids not yet completed in the film awards table.

    A film is 'done' when it already has a row in mubi_film_awards with a
    completed status (success/no_awards), matched on mubi_id.
    """
    col = _quote_identifier(config.input_mubi_id_column)
    rows = conn.execute(text(
        f"select distinct {col} as mubi_id "
        f"from {_relation(config.input_schema, config.input_table)} "
        f"where {col} is not null"
    )).fetchall()
    candidate_ids: list[int] = []
    for row in rows:
        try:
            candidate_ids.append(int(row[0]))
        except (TypeError, ValueError):
            continue

    processed = _fetch_processed_mubi_ids(conn, config)
    return [i for i in dict.fromkeys(candidate_ids) if i not in processed]


def _fetch_processed_mubi_ids(conn, config: ConnectorConfig) -> set[int]:
    if not _table_exists(conn, config.output_schema, config.film_awards_table):
        return set()
    rows = conn.execute(text(
        f"select distinct mubi_id "
        f"from {_relation(config.output_schema, config.film_awards_table)} "
        f"where mubi_id is not null "
        f"and lower(coalesce(scrape_status, '')) = any(:statuses)"
    ), {"statuses": config.completed_award_statuses}).fetchall()
    out: set[int] = set()
    for row in rows:
        try:
            out.add(int(row[0]))
        except (TypeError, ValueError):
            continue
    return out


def _fetch_processed_page_combos(conn, config: ConnectorConfig) -> set[tuple]:
    if not _table_exists(conn, config.output_schema, config.festival_films_table):
        return set()
    rows = conn.execute(text(
        f"select distinct festival_slug, year, page_num "
        f"from {_relation(config.output_schema, config.festival_films_table)} "
        f"where lower(coalesce(scrape_status, '')) = any(:statuses)"
    ), {"statuses": config.completed_festival_statuses}).fetchall()
    return {(row[0], row[1], row[2]) for row in rows}


def _fetch_edition_empty_boundaries(conn, config: ConnectorConfig) -> dict[tuple, int]:
    if not _table_exists(conn, config.output_schema, config.festival_films_table):
        return {}
    rows = conn.execute(text(
        f"select festival_slug, year, min(page_num) "
        f"from {_relation(config.output_schema, config.festival_films_table)} "
        f"where lower(coalesce(scrape_status, '')) = 'empty' "
        f"group by festival_slug, year"
    )).fetchall()
    return {(row[0], row[1]): row[2] for row in rows if row[2] is not None}


def _fetch_existing_hashes(conn, schema_name: str, table_name: str) -> set[str]:
    if not _table_exists(conn, schema_name, table_name):
        return set()
    rows = conn.execute(text(
        f"select record_hash from {_relation(schema_name, table_name)} "
        f"where record_hash is not null"
    )).fetchall()
    return {row[0] for row in rows}


def _insert_festival_films(conn, config: ConnectorConfig, records: list[dict]) -> None:
    if not records:
        return
    rel = _relation(config.output_schema, config.festival_films_table)
    conn.execute(text(f"""
        insert into {rel} (
            run_id, extracted_at, festival_slug, festival_name,
            year, page_num, title, director, country, nominations,
            film_link, scrape_status, error_message, record_hash
        ) values (
            :run_id, :extracted_at, :festival_slug, :festival_name,
            :year, :page_num, :title, :director, :country, :nominations,
            :film_link, :scrape_status, :error_message, :record_hash
        )
    """), records)


def _insert_film_awards(conn, config: ConnectorConfig, records: list[dict]) -> None:
    if not records:
        return
    rel = _relation(config.output_schema, config.film_awards_table)
    conn.execute(text(f"""
        insert into {rel} (
            run_id, extracted_at, film_link, mubi_id, festival, year,
            distinction, award, scrape_status, error_message, record_hash
        ) values (
            :run_id, :extracted_at, :film_link, :mubi_id, :festival, :year,
            :distinction, :award, :scrape_status, :error_message, :record_hash
        )
    """), records)


_FESTIVAL_FILMS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "run_id": {"type": "string"},
        "extracted_at": {"type": "string", "format": "date-time"},
        "festival_slug": {"type": ["string", "null"]},
        "festival_name": {"type": ["string", "null"]},
        "year": {"type": ["integer", "null"]},
        "page_num": {"type": ["integer", "null"]},
        "title": {"type": ["string", "null"]},
        "director": {"type": ["string", "null"]},
        "country": {"type": ["string", "null"]},
        "nominations": {"type": ["string", "null"]},
        "film_link": {"type": ["string", "null"]},
        "scrape_status": {"type": "string"},
        "error_message": {"type": ["string", "null"]},
        "record_hash": {"type": "string"},
    },
}

_FILM_AWARDS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "run_id": {"type": "string"},
        "extracted_at": {"type": "string", "format": "date-time"},
        "film_link": {"type": ["string", "null"]},
        "mubi_id": {"type": ["integer", "null"]},
        "festival": {"type": ["string", "null"]},
        "year": {"type": ["string", "null"]},
        "distinction": {"type": ["string", "null"]},
        "award": {"type": ["string", "null"]},
        "scrape_status": {"type": "string"},
        "error_message": {"type": ["string", "null"]},
        "record_hash": {"type": "string"},
    },
}
