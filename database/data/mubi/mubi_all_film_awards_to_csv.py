import csv
import random
from pathlib import Path
from typing import Set
from database.data.mubi.mubi_page_scraper import MubiPageScraper
from database.data.scraping_browser import AsyncBrowserSession
from playwright.async_api import Error as PlaywrightError


class MubiAllFilmAwardsToCsv:
    """
    Scrape all awards for each film from a CSV file and save them to a new CSV file.
    """

    def __init__(self, input_csv: str = "festivals_all_films.csv", output_csv: str = "films_all_awards.csv", processed_log="processed_links.txt"):
        self.input_path = Path(input_csv)
        self.output_path = Path(output_csv)
        self.processed_log_path = Path(processed_log)
        self.scraper = MubiPageScraper()
        self.film_columns = ["title", "director", "country", "link"]
        self.award_columns = ["festival", "year", "distinction", "award"]
        self.output_columns = self.film_columns + self.award_columns

    async def run(self, max_requests_per_session: int = 7, max_total_requests: int = 30):
        self._init_output_file()
        processed_links = self._load_scraped_links()
        films = self._load_films_to_process()
        request_count = 0
        total_request_count = 0

        print(f"📥 Loaded {len(films)} films, {len(processed_links)} already processed")

        try:
            async with AsyncBrowserSession() as session:
                for film in films:
                    link = film["link"]
                    if link in processed_links:
                        # print(f"⏩ Skipping already processed film: {link}")
                        continue

                    url = self.scraper.FILM_ALL_AWARDS_URL.format(film_link=link)
                    html = await session.fetch_html(url)
                    awards = self.scraper.extract_film_all_awards(html)

                    if not awards:
                        print(f"⚠️ No awards found for {film['title']}")
                        continue

                    with open(self.output_path, mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=self.output_columns)
                        for award in awards:
                            row = {**film, **award}
                            writer.writerow(row)

                    print(f"✅ Wrote {len(awards)} awards for {film['title']}")
                    self._mark_as_processed(link)

                    total_request_count += 1
                    if total_request_count >= max_total_requests:
                        print(f"🏁 Reached maximum total requests ({max_total_requests}).")
                        break
                    
                    request_count += 1
                    if request_count >= max_requests_per_session:
                        print(f"🔁 Restarting browser session after {request_count} requests.")
                        await session.__aexit__(None, None, None)
                        session = await AsyncBrowserSession().__aenter__()  # restart session
                        request_count = 0
                    
                    delay = random.uniform(2, 4)
                    print(f"⏳ Waiting {delay:.2f} seconds...")

        except PlaywrightError as e:
            print(f"🔥 Browser session crashed: {e}")         

        except Exception as e:
            print(f"❌ Failed to process {film['title']} ({link}): {e}")

    def _load_scraped_links(self) -> Set[str]:
        if not self.processed_log_path.exists():
            return set()

        with open(self.processed_log_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())

    def _load_films_to_process(self) -> list:
        """Load all films from the input CSV."""
        films = []
        with open(self.input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("link"):
                    films.append({key: row.get(key, "") for key in self.film_columns})
        return films

    def _mark_as_processed(self, link: str):
        with open(self.processed_log_path, "a", encoding="utf-8") as f:
            f.write(link + "\n")

    def _init_output_file(self):
        """Ensure the output file has headers."""
        if not self.output_path.exists():
            with open(self.output_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.output_columns)
                writer.writeheader()

    