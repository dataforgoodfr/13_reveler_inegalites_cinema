import csv
import asyncio
import random
from pathlib import Path
from typing import Set, Tuple
from database.data.mubi.mubi_page_scraper import MubiPageScraper
from database.data.scraping_browser import AsyncBrowserSession
from playwright.async_api import Error as PlaywrightError


class MubiAllFestivalFilmsToCsv:
    """
    Scrape all films from a festival edition and save them to a CSV file.
    """

    def __init__(self, csv_file: str, festival: str, start_year: int = 2010, end_year: int = 2024, max_pages: int = 4):
        self.csv_path = Path(csv_file)
        self.festival = festival
        self.start_year = start_year
        self.end_year = end_year
        self.page_range = list(range(1, max_pages + 1)) 
        self.scraper = MubiPageScraper()
        self.fieldnames = ["festival", "year", "page_num", "title", "director", "country", "nominations", "link"]

    async def run(self, max_requests_per_session: int = 5):
        request_count = 0
        # Load already scraped (year, page_num) pairs
        scraped_pairs = self._load_existing_pairs()

        self._init_csv_file()

        try:
            async with AsyncBrowserSession() as session:
                for year in range(self.start_year, self.end_year + 1):
                    for page_num in self.page_range:
                        pair = (year, page_num)
                        if pair in scraped_pairs:
                            print(f"⏩ Skipping already scraped year={year}, page={page_num}")
                            continue

                        await self._scrape_and_append(session, year, page_num)

                        request_count += 1
                        if request_count >= max_requests_per_session:
                            print(f"🔁 Restarting browser session after {request_count} requests.")
                            await session.__aexit__(None, None, None)
                            session = await AsyncBrowserSession().__aenter__()  # restart session
                            request_count = 0

                        delay = random.uniform(3, 5)
                        print(f"⏳ Waiting {delay:.2f} seconds...")
                        await asyncio.sleep(delay)

        except PlaywrightError as e:
            print(f"🔥 Browser session crashed: {e}")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")

    async def _scrape_and_append(self, session, year: int, page_num: int):
        filters = {
            "festival": self.festival,
            "year": str(year),
            "page_num": str(page_num)
        }

        url = self.scraper.FESTIVAL_EDITION_ALL_FILMS_URL.format(**filters)

        try:
            html = await session.fetch_html(url)
            films = self.scraper.extract_festival_edition_all_films(html)

            if not films:
                print(f"❌ No films found at {year} page {page_num}.")
                return
            for film in films:
                film["festival"] = self.festival
                film["year"] = year
                film["page_num"] = page_num

            with open(self.csv_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerows(films)

            print(f"✅ Saved {len(films)} films from {self.festival} {year}, page {page_num}")

        except PlaywrightError as e:
            print(f"⚠️ Session error at {year} page {page_num}: {e}")
        except Exception as e:
            print(f"❌ Failed at {year} page {page_num}: {e}")

    def _init_csv_file(self):
        if not self.csv_path.exists():
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def _load_existing_pairs(self) -> Set[Tuple[int, int]]:
        pairs = set()
        if not self.csv_path.exists():
             return set()

        with open(self.csv_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if row.get("festival") != self.festival:
                        continue  # ignore rows from other festivals
                    year = int(row["year"])
                    page_num = int(row["page_num"])
                    pairs.add((year, page_num))
                except Exception:
                    continue
        return pairs
