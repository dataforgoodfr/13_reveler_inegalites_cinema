"""
Backfill missing `title` values in raw.mubi_festival_films.

Context
-------
Mubi rotated its hashed CSS classes, so the old title selector
`h3.css-1hr6q83` stopped matching and every scraped row landed with
`title = NULL` (director / country / film_link were captured fine).
The selector is now fixed in mubi_scraper.py, but the connector treats
already-scraped (festival_slug, year, page_num) combos as "processed" and
will not revisit them, so existing rows are never repaired.

This script repairs them in place:
  1. Find every (festival_slug, year, page_num) combo that has success rows
     with a NULL title.
  2. Re-fetch that festival edition page and re-extract the films (now with
     the corrected title selector).
  3. Match re-scraped films to existing rows POSITIONALLY (page order is
     stable and rows were inserted in extraction order) and UPDATE each row by
     its ctid.

A combo can have been scraped by several runs (retries / overlapping Prefect
runs appended duplicate copies). We only target the rows of the LATEST
successful run per combo -- the same set the staging dbt view keeps after
deduplication -- so the re-scraped film list (one entry per film) lines up
1:1 with the rows we update. Rows from older duplicate runs are left with
their NULL titles; the dbt view discards them anyway.

Only rows whose title is currently NULL are touched. Rows are matched by
`ctid` so each UPDATE hits exactly one row. film_link / director / country are
verified against the re-scraped film as a sanity check before updating;
mismatches are logged and skipped (never blindly overwritten).

Usage
-----
    # dry run — scrape + match + report, no writes
    python -m ingestion.scraping.mubi.backfill_missing_titles --dry-run

    # apply updates
    python -m ingestion.scraping.mubi.backfill_missing_titles

    # limit to N combos (debug)
    python -m ingestion.scraping.mubi.backfill_missing_titles --limit 5

Connection comes from the same env vars the connector uses:
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_SSLMODE, and either
DATABASE_URL or (POSTGRES_USER + password). Defaults match config.json
(dbt_user / DBT_USER_POSTGRES_PASSWORD).
"""

import argparse
import asyncio
import os
import random
import sys
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

from ingestion.scraping.browser import AsyncBrowserSession, WebsiteBlockedError
from ingestion.scraping.mubi.mubi_scraper import MubiPageScraper

OUTPUT_SCHEMA = os.getenv("MUBI_OUTPUT_SCHEMA", "raw")
TABLE = os.getenv("MUBI_FESTIVAL_FILMS_TABLE", "mubi_festival_films")
RELATION = f'"{OUTPUT_SCHEMA}"."{TABLE}"'

DELAY_MIN = float(os.getenv("MUBI_DELAY_MIN", "1.0"))
DELAY_MAX = float(os.getenv("MUBI_DELAY_MAX", "3.0"))
MAX_REQUESTS_PER_SESSION = int(os.getenv("MUBI_MAX_REQUESTS_PER_SESSION", "6"))
RECORD_TIMEOUT_SECONDS = float(os.getenv("MUBI_RECORD_TIMEOUT_SECONDS", "60"))


def _build_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    host = os.getenv("POSTGRES_HOST")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER", "dbt_user")
    password = os.getenv("DBT_USER_POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD")
    sslmode = os.getenv("POSTGRES_SSLMODE", "disable")
    missing = [n for n, v in (("POSTGRES_HOST", host), ("POSTGRES_DB", db), ("password", password)) if not v]
    if missing:
        sys.exit(f"Missing connection settings: {', '.join(missing)} (or set DATABASE_URL).")
    return (
        f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(db)}?sslmode={sslmode}"
    )


def _film_slug(film_link):
    """Last path segment of a film link, ignoring the locale prefix.

    '/fr/us/films/echo-1999' -> 'echo-1999'. Used to match films across scrapes
    whose locale segment differs. Mirrors mubi_slug in the staging dbt model.
    """
    if not film_link:
        return None
    return film_link.rstrip("/").split("/")[-1]


def fetch_combos(conn, limit=None):
    """Return (slug, year, page_num) combos that have success rows with NULL title."""
    sql = (
        f"select distinct festival_slug, year, page_num from {RELATION} "
        f"where scrape_status = 'success' and title is null "
        f"and festival_slug is not null and year is not null and page_num is not null "
        f"order by festival_slug, year, page_num"
    )
    if limit:
        sql += f" limit {int(limit)}"
    return [(r[0], r[1], r[2]) for r in conn.execute(text(sql)).fetchall()]


def fetch_null_title_rows(conn, slug, year, page):
    """
    NULL-title success rows for a combo from the LATEST successful run only,
    in stable page (ctid) order.

    Scoping to the latest run mirrors the staging dbt view's dedup: a combo may
    have several runs' worth of (duplicated) rows, but only the latest run's
    rows survive deduplication, and only that run matches the re-scraped page's
    film count 1:1. Older runs' rows are intentionally left untouched.
    """
    rows = conn.execute(
        text(
            f"with ranked as ( "
            f"  select ctid, film_link, director, country, title, "
            f"         dense_rank() over ( "
            f"           partition by festival_slug, year, page_num "
            f"           order by extracted_at desc, run_id desc) as run_rank "
            f"  from {RELATION} "
            f"  where scrape_status = 'success' and film_link is not null "
            f"    and festival_slug = :slug and year = :year and page_num = :page "
            f") "
            f"select ctid, film_link, director, country from ranked "
            f"where run_rank = 1 and title is null "
            f"order by ctid"
        ),
        {"slug": slug, "year": year, "page": page},
    ).fetchall()
    return [{"ctid": r[0], "film_link": r[1], "director": r[2], "country": r[3]} for r in rows]


def update_title_by_ctid(conn, ctid, title):
    conn.execute(
        text(f"update {RELATION} set title = :title where ctid = :ctid and title is null"),
        {"title": title, "ctid": ctid},
    )


async def backfill(database_url, dry_run, limit, verbose):
    scraper = MubiPageScraper()
    engine = create_engine(database_url)

    with engine.connect() as conn:
        combos = fetch_combos(conn, limit=limit)

    if not combos:
        print("Nothing to backfill: no success rows with NULL title.")
        engine.dispose()
        return

    print(f"Backfill: {len(combos)} (festival, year, page) combos to re-scrape.")
    if dry_run:
        print("DRY RUN — no rows will be updated.\n")

    ws_endpoint = os.getenv("PLAYWRIGHT_WS_ENDPOINT")
    totals = {"updated": 0, "mismatch": 0, "missing_title": 0, "count_mismatch": 0, "scrape_failed": 0}
    request_count = 0

    session_cm = AsyncBrowserSession(ws_endpoint=ws_endpoint, headless=True, verbose=verbose)
    session = await session_cm.__aenter__()
    try:
        for i, (slug, year, page) in enumerate(combos):
            if i > 0:
                await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            url = scraper.FESTIVAL_EDITION_ALL_FILMS_URL.format(festival=slug, page_num=page, year=year)
            try:
                task = session.fetch_html(url)
                html = await asyncio.wait_for(task, timeout=RECORD_TIMEOUT_SECONDS)
                films = scraper.extract_festival_edition_all_films(html)
            except WebsiteBlockedError as exc:
                print(f"[{slug} {year} p{page}] blocked: {exc} — restarting session")
                totals["scrape_failed"] += 1
                await session_cm.__aexit__(None, None, None)
                session_cm = AsyncBrowserSession(ws_endpoint=ws_endpoint, headless=True, verbose=verbose)
                session = await session_cm.__aenter__()
                request_count = 0
                continue
            except Exception as exc:
                print(f"[{slug} {year} p{page}] scrape error: {exc}")
                totals["scrape_failed"] += 1
                continue

            with engine.begin() as conn:
                db_rows = fetch_null_title_rows(conn, slug, year, page)

                if len(films) != len(db_rows):
                    # Page layout changed since the original scrape; positional
                    # matching is unsafe. Skip and report rather than risk
                    # assigning the wrong title.
                    print(
                        f"[{slug} {year} p{page}] count mismatch: "
                        f"scraped {len(films)} films vs {len(db_rows)} NULL-title rows — skipped"
                    )
                    totals["count_mismatch"] += 1
                    continue

                combo_updated = 0
                for film, row in zip(films, db_rows, strict=True):
                    title = film.get("title")
                    if not title:
                        totals["missing_title"] += 1
                        continue

                    # Sanity check that the positional match is the same film.
                    # Compare the film SLUG (last path segment) rather than the
                    # full link: Mubi serves a locale segment that can differ
                    # between scrapes (e.g. /fr/fr/films/echo vs /fr/us/films/echo)
                    # for the same film, so full-link equality gives false
                    # mismatches. Director/country corroborate the match.
                    if (
                        _film_slug(film.get("link")) != _film_slug(row["film_link"])
                        or (film.get("director") or None) != row["director"]
                        or (film.get("country") or None) != row["country"]
                    ):
                        print(
                            f"[{slug} {year} p{page}] mismatch for ctid {row['ctid']}: "
                            f"scraped link={film.get('link')} dir={film.get('director')} "
                            f"vs db link={row['film_link']} dir={row['director']} — skipped"
                        )
                        totals["mismatch"] += 1
                        continue

                    if not dry_run:
                        update_title_by_ctid(conn, row["ctid"], title)
                    combo_updated += 1
                    totals["updated"] += 1

                print(f"[{slug} {year} p{page}] {combo_updated}/{len(db_rows)} titles "
                      f"{'would be ' if dry_run else ''}updated")

            request_count += 1
            if request_count >= MAX_REQUESTS_PER_SESSION:
                await session_cm.__aexit__(None, None, None)
                session_cm = AsyncBrowserSession(ws_endpoint=ws_endpoint, headless=True, verbose=verbose)
                session = await session_cm.__aenter__()
                request_count = 0
    finally:
        await session_cm.__aexit__(None, None, None)
        engine.dispose()

    print(
        "\nBackfill summary: "
        f"{'(dry run) ' if dry_run else ''}"
        f"updated={totals['updated']}, "
        f"mismatch_skipped={totals['mismatch']}, "
        f"count_mismatch_combos={totals['count_mismatch']}, "
        f"still_missing_title={totals['missing_title']}, "
        f"scrape_failed_combos={totals['scrape_failed']}"
    )


def main():
    parser = argparse.ArgumentParser(description="Backfill missing titles in raw.mubi_festival_films.")
    parser.add_argument("--dry-run", action="store_true", help="Scrape and match but do not write.")
    parser.add_argument("--limit", type=int, default=None, help="Limit to N combos (debug).")
    parser.add_argument("--verbose", action="store_true", help="Verbose browser logging.")
    args = parser.parse_args()

    database_url = _build_database_url()
    asyncio.run(backfill(database_url, dry_run=args.dry_run, limit=args.limit, verbose=args.verbose))


if __name__ == "__main__":
    main()
