import csv
import os

from sqlalchemy import select
from sqlalchemy.orm import Session
from tqdm import tqdm

from database.data.allocine.allocine_scraper import AllocineScraper
from database.data.scraping_browser import AsyncBrowserSession
from database.database import SessionLocal
from database.models import Film


class AllocineFilmMatcher:
    """
    AllocineFilmMatcher is a class that matches films from a database with their corresponding
    entries on Allociné, a French movie database. It uses the AllocineScraper to fetch data
    from Allociné and saves the results to a CSV file.
    """

    CSV_HEADERS = [
        "film_id",
        "visa_number",
        "original_name",
        "cnc_agrement_year",
        "allocine_id",
        "allocine_title",
        "allocine_url",
    ]
    BACKUP_ENRICHED_CSV_PATH = "database/data/allocine/allocine_matches_enriched.csv"

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.scraper = AllocineScraper()
        self.db: Session = SessionLocal()
        self.backup_rows_by_visa = self._load_backup_rows_by_visa()

    def _load_backup_rows_by_visa(self) -> dict:
        if not os.path.exists(self.BACKUP_ENRICHED_CSV_PATH):
            return {}

        with open(
            self.BACKUP_ENRICHED_CSV_PATH, mode="r", encoding="utf-8"
        ) as backup_file:
            reader = csv.DictReader(backup_file)
            return {row["visa_number"]: row for row in reader if row.get("visa_number")}

    async def find_allocine_film_by_name(self, name: str, year: str) -> dict:
        url_name = self.scraper._reformat_str_for_url(f"{name} {year}")
        filters = {"film_title_url_styled": url_name}
        search_url = self.scraper.SEARCH_URL.format(**filters)

        async with AsyncBrowserSession() as session:
            html = await session.fetch_html(search_url)

        return self.scraper.extract_searched_first_film(html)

    async def run(self):
        films = self.db.execute(select(Film)).scalars().all()

        # Load already-processed film names
        existing_visas = set()
        file_exists = os.path.exists(self.csv_path)

        if file_exists:
            with open(self.csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_visas = {row["visa_number"] for row in reader}

        # Append mode
        with open(self.csv_path, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write header if file is new
            if not file_exists or os.stat(self.csv_path).st_size == 0:
                writer.writerow(self.CSV_HEADERS)

            for film in tqdm(films, desc="Searching Allociné"):
                original_name = film.original_name
                cnc_agrement_year = film.cnc_agrement_year
                visa_number = film.visa_number

                if visa_number in existing_visas:
                    continue

                backup_row = self.backup_rows_by_visa.get(visa_number)
                if backup_row:
                    writer.writerow(
                        [
                            film.id,
                            visa_number,
                            original_name,
                            cnc_agrement_year,
                            backup_row.get("allocine_id", "Not found"),
                            backup_row.get("allocine_title", "Not found"),
                            backup_row.get("allocine_url", "Not found"),
                        ]
                    )
                    csvfile.flush()
                    existing_visas.add(visa_number)
                    continue

                try:
                    allocine_film = await self.find_allocine_film_by_name(
                        original_name, cnc_agrement_year
                    )
                    if allocine_film:
                        writer.writerow(
                            [
                                film.id,
                                visa_number,
                                original_name,
                                cnc_agrement_year,
                                allocine_film["id"],
                                allocine_film["title"],
                                f"https://www.allocine.fr{allocine_film['link']}",
                            ]
                        )
                    else:
                        writer.writerow(
                            [
                                film.id,
                                visa_number,
                                original_name,
                                cnc_agrement_year,
                                "Not found",
                                "Not found",
                                "Not found",
                            ]
                        )
                    csvfile.flush()  # Ensure data is written immediately
                    existing_visas.add(visa_number)
                except Exception as e:
                    print(f"❌ Error processing '{original_name}': {e}")
                    writer.writerow(
                        [
                            film.id,
                            visa_number,
                            original_name,
                            cnc_agrement_year,
                            "Error",
                            "Error",
                            str(e),
                        ]
                    )

        print("✅ Done! Results saved to", self.csv_path)
