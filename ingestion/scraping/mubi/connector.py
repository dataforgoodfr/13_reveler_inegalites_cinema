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
DEFAULT_START_YEAR = 2000
DEFAULT_MAX_PAGES_PER_EDITION = 10
DEFAULT_FESTIVAL_OR_AWARD = "festival"
DEFAULT_MAX_REQUESTS_PER_SESSION = 6
DEFAULT_RECORD_TIMEOUT_SECONDS = 60.0
DEFAULT_COMPLETED_FESTIVAL_STATUSES = ["success", "empty"]
DEFAULT_COMPLETED_AWARD_STATUSES = ["success", "no_awards"]
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


CONNECTION_SPECIFICATION = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Mubi Airbyte Source",
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
        "start_year": {
            "type": "integer",
            "title": "Start year for festival editions",
            "default": DEFAULT_START_YEAR,
        },
        "end_year": {
            "type": ["integer", "null"],
            "title": "End year for festival editions (null = current year)",
        },
        "max_pages_per_edition": {
            "type": "integer",
            "title": "Max pages to scrape per festival-year edition",
            "default": DEFAULT_MAX_PAGES_PER_EDITION,
            "minimum": 1,
        },
        "festival_or_award": {
            "type": "string",
            "title": "Filter type for festival listing",
            "default": DEFAULT_FESTIVAL_OR_AWARD,
            "enum": ["festival", "award"],
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
            "title": "Maximum number of (festival, year, page) combos to scrape",
            "minimum": 1,
            "description": "Optional debug limit applied after filtering already processed combos.",
        },
        "record_timeout_seconds": {
            "type": "number",
            "title": "Per-request timeout in seconds",
            "default": DEFAULT_RECORD_TIMEOUT_SECONDS,
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
    output_schema: str
    festival_films_table: str
    film_awards_table: str
    start_year: int
    end_year: int
    max_pages_per_edition: int
    festival_or_award: str
    completed_festival_statuses: list[str]
    completed_award_statuses: list[str]
    scrape_limit: int | None
    record_timeout_seconds: float
    playwright_ws_endpoint: str | None
    headless: bool
    max_requests_per_session: int
    inter_request_delay_min_seconds: float
    inter_request_delay_max_seconds: float
    verbose: bool

    @classmethod
    def from_dict(cls, raw_config: dict[str, Any]) -> "ConnectorConfig":
        database_url = raw_config.get("database_url") or _build_database_url(raw_config)
        current_year = datetime.now(timezone.utc).year
        end_year = raw_config.get("end_year") or current_year
        delay_min = float(raw_config.get("inter_request_delay_min_seconds", 2.0))
        delay_max = float(raw_config.get("inter_request_delay_max_seconds", 5.0))
        if delay_max < delay_min:
            raise ValueError("inter_request_delay_max_seconds must be >= inter_request_delay_min_seconds")

        values = {
            "database_url": database_url,
            "output_schema": raw_config.get("output_schema", DEFAULT_OUTPUT_SCHEMA),
            "festival_films_table": raw_config.get("festival_films_table", DEFAULT_FESTIVAL_FILMS_TABLE),
            "film_awards_table": raw_config.get("film_awards_table", DEFAULT_FILM_AWARDS_TABLE),
            "start_year": int(raw_config.get("start_year", DEFAULT_START_YEAR)),
            "end_year": int(end_year),
            "max_pages_per_edition": max(1, int(raw_config.get("max_pages_per_edition", DEFAULT_MAX_PAGES_PER_EDITION))),
            "festival_or_award": raw_config.get("festival_or_award", DEFAULT_FESTIVAL_OR_AWARD),
            "completed_festival_statuses": [
                str(s).lower() for s in (raw_config.get("completed_festival_statuses") or DEFAULT_COMPLETED_FESTIVAL_STATUSES)
            ],
            "completed_award_statuses": [
                str(s).lower() for s in (raw_config.get("completed_award_statuses") or DEFAULT_COMPLETED_AWARD_STATUSES)
            ],
            "scrape_limit": _normalize_positive_int(raw_config.get("scrape_limit")),
            "record_timeout_seconds": max(0.0, float(raw_config.get("record_timeout_seconds", DEFAULT_RECORD_TIMEOUT_SECONDS))),
            "playwright_ws_endpoint": raw_config.get("playwright_ws_endpoint") or os.getenv("PLAYWRIGHT_WS_ENDPOINT"),
            "headless": bool(raw_config.get("headless", True)),
            "max_requests_per_session": max(1, int(raw_config.get("max_requests_per_session", DEFAULT_MAX_REQUESTS_PER_SESSION))),
            "inter_request_delay_min_seconds": delay_min,
            "inter_request_delay_max_seconds": delay_max,
            "verbose": bool(raw_config.get("verbose", False)),
        }

        for key, value in values.items():
            if (key.endswith("_table") or key.endswith("_schema")) and value:
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


def _festival_slug_from_link(festival_link: str) -> str:
    """Extract slug from a relative URL like '/fr/awards-and-festivals/cesars'."""
    return festival_link.rstrip("/").split("/")[-1]


class MubiAirbyteSource:
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
            return True, "Postgres connection ok."
        except Exception as exc:
            return False, str(exc)
        finally:
            engine.dispose()

    def sync_to_postgres(self, raw_config: dict[str, Any]) -> dict[str, int]:
        config = ConnectorConfig.from_dict(raw_config)
        engine = create_engine(config.database_url)
        try:
            with engine.begin() as conn:
                _ensure_schema(conn, config.output_schema)
                _ensure_festival_films_table(conn, config)
                _ensure_film_awards_table(conn, config)
                processed_page_combos = _fetch_processed_page_combos(conn, config)
                processed_film_links = _fetch_processed_film_links(conn, config)
        finally:
            engine.dispose()

        festivals = asyncio.run(self._discover_festivals(config))
        if not festivals:
            print("Mubi: no festivals discovered. Check selectors or connectivity.")
            return {"festival_films": 0, "film_awards": 0}

        print(f"Mubi: discovered {len(festivals)} festivals.")

        festival_records = asyncio.run(
            self._scrape_festival_films(config, festivals, processed_page_combos)
        )

        if festival_records:
            engine = create_engine(config.database_url)
            try:
                with engine.begin() as conn:
                    _insert_festival_films(conn, config, festival_records)
                    # Refresh processed links after inserting new film records
                    processed_film_links = _fetch_processed_film_links(conn, config)
            finally:
                engine.dispose()

        award_records = asyncio.run(
            self._scrape_film_awards(config, processed_film_links)
        )

        if award_records:
            engine = create_engine(config.database_url)
            try:
                with engine.begin() as conn:
                    _insert_film_awards(conn, config, award_records)
            finally:
                engine.dispose()

        festival_inserted = len([r for r in festival_records if r["scrape_status"] == "success"])
        awards_inserted = len([r for r in award_records if r["scrape_status"] == "success"])
        print(
            f"Mubi scraping complete: "
            f"{festival_inserted} festival film records, "
            f"{awards_inserted} film award records inserted."
        )
        return {"festival_films": len(festival_records), "film_awards": len(award_records)}

    async def _discover_festivals(self, config: ConnectorConfig) -> list[dict[str, Any]]:
        """Paginate through the festivals listing until an empty page is returned."""
        from ingestion.scraping.mubi.mubi_scraper import MubiPageScraper
        from ingestion.scraping.browser import AsyncBrowserSession

        scraper = MubiPageScraper()
        festivals: list[dict[str, Any]] = []
        page_num = 1

        async with AsyncBrowserSession(
            ws_endpoint=config.playwright_ws_endpoint,
            headless=config.headless,
            verbose=config.verbose,
        ) as session:
            while True:
                url = scraper.ALL_FESTIVALS_URL.format(
                    festival_or_award=config.festival_or_award,
                    page_num=page_num,
                )
                if config.verbose:
                    print(f"[discover] Fetching festivals page {page_num}: {url}")
                try:
                    html = await session.fetch_html(url)
                    page_festivals = scraper.extract_all_festivals(html)
                except WebsiteBlockedError as exc:
                    print(f"Mubi: blocked while discovering festivals page {page_num}: {exc}")
                    break
                except Exception as exc:
                    print(f"Mubi: error on festivals page {page_num}: {exc}")
                    break

                if not page_festivals:
                    if config.verbose:
                        print(f"[discover] No festivals on page {page_num}, stopping.")
                    break

                festivals.extend(page_festivals)
                print(f"Mubi: discovered {len(page_festivals)} festivals on page {page_num} (total: {len(festivals)}).")
                page_num += 1

                delay = random.uniform(
                    config.inter_request_delay_min_seconds,
                    config.inter_request_delay_max_seconds,
                )
                await asyncio.sleep(delay)

        # Deduplicate by festival_link
        seen = set()
        unique = []
        null_link_count = 0
        for f in festivals:
            key = f.get("festival_link")
            if not key:
                null_link_count += 1
                continue
            if key not in seen:
                seen.add(key)
                unique.append(f)

        if null_link_count:
            print(
                f"Mubi: WARNING — {null_link_count}/{len(festivals)} discovered festivals "
                f"had no link extracted. The 'festival_link' CSS selector in "
                f"mubi_scraper.py may be stale and need updating."
            )

        return unique

    async def _scrape_festival_films(
        self,
        config: ConnectorConfig,
        festivals: list[dict[str, Any]],
        processed_page_combos: set[tuple],
    ) -> list[dict[str, Any]]:
        from ingestion.scraping.mubi.mubi_scraper import MubiPageScraper
        from ingestion.scraping.browser import AsyncBrowserSession

        scraper = MubiPageScraper()
        run_id = str(uuid.uuid4())

        # Build list of pending (slug, name, year, page) combos
        pending = []
        for fest in festivals:
            link = fest.get("festival_link") or ""
            if not link:
                continue
            slug = _festival_slug_from_link(link)
            name = fest.get("festival_name") or slug
            for year in range(config.start_year, config.end_year + 1):
                for page in range(1, config.max_pages_per_edition + 1):
                    if (slug, year, page) not in processed_page_combos:
                        pending.append((slug, name, year, page))

        if config.scrape_limit is not None:
            pending = pending[: config.scrape_limit]

        if not pending:
            print("Mubi festival films: nothing pending.")
            return []

        print(f"Mubi festival films: {len(pending)} (festival, year, page) combos to scrape.")

        records: list[dict[str, Any]] = []
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
            for i, (slug, name, year, page) in enumerate(pending):
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
                    "festival_name": name,
                    "year": year,
                    "page_num": page,
                }

                try:
                    task = session.fetch_html(url)
                    if config.record_timeout_seconds > 0:
                        html = await asyncio.wait_for(task, timeout=config.record_timeout_seconds)
                    else:
                        html = await task

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
                        print(f"[films] {slug} {year} p{page}: empty")
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

                except asyncio.TimeoutError:
                    record = {
                        **base,
                        "title": None, "director": None, "country": None,
                        "nominations": None, "film_link": None,
                        "scrape_status": "error",
                        "error_message": f"Timeout after {config.record_timeout_seconds:.0f}s",
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[films] {slug} {year} p{page}: timeout")

                except WebsiteBlockedError as exc:
                    record = {
                        **base,
                        "title": None, "director": None, "country": None,
                        "nominations": None, "film_link": None,
                        "scrape_status": "blocked",
                        "error_message": str(exc),
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[films] {slug} {year} p{page}: blocked — restarting session")
                    await close_session()
                    await open_session()
                    request_count = 0
                    continue

                except Exception as exc:
                    record = {
                        **base,
                        "title": None, "director": None, "country": None,
                        "nominations": None, "film_link": None,
                        "scrape_status": "error",
                        "error_message": str(exc),
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[films] {slug} {year} p{page}: error — {exc}")

                request_count += 1
                if request_count >= config.max_requests_per_session:
                    if config.verbose:
                        print(f"Restarting browser session after {request_count} requests.")
                    await close_session()
                    await open_session()
                    request_count = 0

        finally:
            await close_session()

        status_summary = {}
        for r in records:
            s = r["scrape_status"]
            status_summary[s] = status_summary.get(s, 0) + 1
        print(
            "Mubi festival films summary: "
            + ", ".join(f"{s}={n}" for s, n in status_summary.items())
        )
        return records

    async def _scrape_film_awards(
        self,
        config: ConnectorConfig,
        processed_film_links: set[str],
    ) -> list[dict[str, Any]]:
        from ingestion.scraping.mubi.mubi_scraper import MubiPageScraper
        from ingestion.scraping.browser import AsyncBrowserSession

        scraper = MubiPageScraper()
        run_id = str(uuid.uuid4())

        # Collect pending film links from mubi_festival_films
        engine = create_engine(config.database_url)
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(
                    f"select distinct film_link "
                    f"from {_relation(config.output_schema, config.festival_films_table)} "
                    f"where film_link is not null"
                )).fetchall()
        finally:
            engine.dispose()

        all_film_links = [row[0] for row in rows]
        pending_links = [link for link in all_film_links if link not in processed_film_links]

        if not pending_links:
            print("Mubi film awards: nothing pending.")
            return []

        print(f"Mubi film awards: {len(pending_links)} film links to scrape.")

        records: list[dict[str, Any]] = []
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
            for i, film_link in enumerate(pending_links):
                if i > 0:
                    delay = random.uniform(
                        config.inter_request_delay_min_seconds,
                        config.inter_request_delay_max_seconds,
                    )
                    await asyncio.sleep(delay)

                extracted_at = _now_iso()
                url = scraper.FILM_ALL_AWARDS_URL.format(film_link=film_link)
                if config.verbose:
                    print(f"[awards] {film_link}: {url}")

                try:
                    task = session.fetch_html(url)
                    if config.record_timeout_seconds > 0:
                        html = await asyncio.wait_for(task, timeout=config.record_timeout_seconds)
                    else:
                        html = await task

                    awards = scraper.extract_film_all_awards(html)

                    mubi_id = scraper.extract_film_mubi_id(html)

                    if not awards:
                        record = {
                            "run_id": run_id,
                            "extracted_at": extracted_at,
                            "film_link": film_link,
                            "mubi_id": mubi_id,
                            "festival": None, "year": None,
                            "distinction": None, "award": None,
                            "scrape_status": "no_awards",
                            "error_message": None,
                        }
                        record["record_hash"] = _hash_record(record)
                        records.append(record)
                        print(f"[awards] {film_link}: no awards (mubi_id={mubi_id})")
                    else:
                        for award in awards:
                            record = {
                                "run_id": run_id,
                                "extracted_at": extracted_at,
                                "film_link": film_link,
                                "mubi_id": mubi_id,
                                "festival": award.get("festival"),
                                "year": award.get("year"),
                                "distinction": award.get("distinction"),
                                "award": award.get("award"),
                                "scrape_status": "success",
                                "error_message": None,
                            }
                            record["record_hash"] = _hash_record(record)
                            records.append(record)
                        print(f"[awards] {film_link}: {len(awards)} awards (mubi_id={mubi_id})")

                except asyncio.TimeoutError:
                    record = {
                        "run_id": run_id, "extracted_at": extracted_at, "film_link": film_link,
                        "mubi_id": None, "festival": None, "year": None,
                        "distinction": None, "award": None,
                        "scrape_status": "error",
                        "error_message": f"Timeout after {config.record_timeout_seconds:.0f}s",
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[awards] {film_link}: timeout")

                except WebsiteBlockedError as exc:
                    record = {
                        "run_id": run_id, "extracted_at": extracted_at, "film_link": film_link,
                        "mubi_id": None, "festival": None, "year": None,
                        "distinction": None, "award": None,
                        "scrape_status": "blocked",
                        "error_message": str(exc),
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[awards] {film_link}: blocked — restarting session")
                    await close_session()
                    await open_session()
                    request_count = 0
                    continue

                except Exception as exc:
                    record = {
                        "run_id": run_id, "extracted_at": extracted_at, "film_link": film_link,
                        "mubi_id": None, "festival": None, "year": None,
                        "distinction": None, "award": None,
                        "scrape_status": "error",
                        "error_message": str(exc),
                    }
                    record["record_hash"] = _hash_record(record)
                    records.append(record)
                    print(f"[awards] {film_link}: error — {exc}")

                request_count += 1
                if request_count >= config.max_requests_per_session:
                    if config.verbose:
                        print(f"Restarting browser session after {request_count} requests.")
                    await close_session()
                    await open_session()
                    request_count = 0

        finally:
            await close_session()

        status_summary = {}
        for r in records:
            s = r["scrape_status"]
            status_summary[s] = status_summary.get(s, 0) + 1
        print(
            "Mubi film awards summary: "
            + ", ".join(f"{s}={n}" for s, n in status_summary.items())
        )
        return records


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


def _fetch_processed_page_combos(conn, config: ConnectorConfig) -> set[tuple]:
    if not _table_exists(conn, config.output_schema, config.festival_films_table):
        return set()
    rows = conn.execute(text(
        f"select distinct festival_slug, year, page_num "
        f"from {_relation(config.output_schema, config.festival_films_table)} "
        f"where lower(coalesce(scrape_status, '')) = any(:statuses)"
    ), {"statuses": config.completed_festival_statuses}).fetchall()
    return {(row[0], row[1], row[2]) for row in rows}


def _fetch_processed_film_links(conn, config: ConnectorConfig) -> set[str]:
    if not _table_exists(conn, config.output_schema, config.film_awards_table):
        return set()
    rows = conn.execute(text(
        f"select distinct film_link "
        f"from {_relation(config.output_schema, config.film_awards_table)} "
        f"where lower(coalesce(scrape_status, '')) = any(:statuses)"
    ), {"statuses": config.completed_award_statuses}).fetchall()
    return {row[0] for row in rows if row[0]}


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
