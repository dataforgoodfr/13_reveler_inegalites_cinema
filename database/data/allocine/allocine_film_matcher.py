import csv
import os
from tqdm import tqdm
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.database import SessionLocal
from database.data.allocine.allocine_scraper import AllocineScraper
from database.data.scraping_browser import AsyncBrowserSession

MART_CNC_FILMS_FOR_SCRAPING_QUERY = text(
    """
    select
        film_id,
        visa_number,
        original_name,
        cnc_agrement_year
    from marts.mart_cnc_films_for_scraping
    where should_scrape_allocine is true
    order by cnc_agrement_year nulls last, visa_number
    """
)

class AllocineFilmMatcher:
    """
    AllocineFilmMatcher is a class that matches films from a database with their corresponding
    entries on Allociné, a French movie database. It uses the AllocineScraper to fetch data
    from Allociné and saves the results to a CSV file.
    """
    CSV_HEADERS = ["film_id", "visa_number", "original_name", "cnc_agrement_year", "allocine_id", "allocine_title", "allocine_url"]

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.scraper = AllocineScraper()
        self.db: Session = SessionLocal()

    def get_films_to_match(self) -> list[dict]:
        return list(self.db.execute(MART_CNC_FILMS_FOR_SCRAPING_QUERY).mappings())

    def _format_error_message(self, error: Exception, max_length: int = 500) -> str:
        message = " ".join(str(error).split())
        if len(message) > max_length:
            return f"{message[:max_length - 3]}..."
        return message

    async def find_allocine_film_by_name(self, name: str, year: str) -> dict:
        url_name = self.scraper._reformat_str_for_url(f"{name} {year}")
        filters = {"film_title_url_styled": url_name}
        search_url = self.scraper.SEARCH_URL.format(**filters)

        async with AsyncBrowserSession() as session:
            html = await session.fetch_html(search_url)

        return self.scraper.extract_searched_first_film(html)

    async def run(self):
        films = self.get_films_to_match()

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
                film_id = film["film_id"]
                original_name = film["original_name"]
                cnc_agrement_year = film["cnc_agrement_year"]
                visa_number = film["visa_number"]

                if visa_number in existing_visas:
                    continue

                try:
                    allocine_film = await self.find_allocine_film_by_name(original_name, cnc_agrement_year)
                    if allocine_film:
                        writer.writerow([
                            film_id,
                            visa_number,
                            original_name,
                            cnc_agrement_year,
                            allocine_film["id"],
                            allocine_film["title"],
                            f"https://www.allocine.fr{allocine_film['link']}"
                        ])
                    else:
                        writer.writerow([
                            film_id,
                            visa_number,
                            original_name,
                            cnc_agrement_year,
                            "Not found",
                            "Not found",
                            "Not found"
                        ])
                    csvfile.flush()  # Ensure data is written immediately
                    existing_visas.add(visa_number)
                except Exception as e:
                    print(f"❌ Error processing '{original_name}': {e}")
                    writer.writerow([
                        film_id,
                        visa_number,
                        original_name,
                        cnc_agrement_year,
                        "Error",
                        "Error",
                        self._format_error_message(e),
                    ])

        print("✅ Done! Results saved to", self.csv_path)
