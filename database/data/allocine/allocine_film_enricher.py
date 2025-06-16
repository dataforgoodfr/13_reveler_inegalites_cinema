import csv
import os
import json
from typing import Optional, Dict
from tqdm import tqdm

from database.data.allocine.allocine_scraper import AllocineScraper
from database.data.scraping_browser import AsyncBrowserSession


class AllocineFilmEnricher:
    """
    AllocineFilmEnricher enriches a CSV file containing film data with additional
    information from Allociné. It fetches details and casting data and writes the result
    to a new enriched file.
    """

    CSV_HEADERS = [
        "visa_number", "original_name", "cnc_directors", "cnc_agrement_year", "allocine_id", "allocine_title", "allocine_url",
        "allocine_visa_number", "poster_url", "release_date", "duration", "genres", "trailer_url", "Direction", "Casting",
        "Scénaristes", "Production", "Equipe technique", "Soundtrack", "Distribution", "Sociétés"
    ]

    def __init__(self, input_csv_path: str):
        self.input_csv_path = input_csv_path
        self.output_csv_path = input_csv_path.replace(".csv", "_enriched.csv")
        self.scraper = AllocineScraper()

    async def fetch_film_details(self, allocine_id: int) -> Optional[Dict[str, str]]:
        url = self.scraper.FILM_URL.format(allocine_film_id=allocine_id)
        async with AsyncBrowserSession() as session:
            html = await session.fetch_html(url)
        return self.scraper.extract_film_details(html)

    async def fetch_film_casting(self, allocine_id: int) -> Optional[Dict[str, str]]:
        url = self.scraper.FILM_CASTING_URL.format(allocine_film_id=allocine_id)
        async with AsyncBrowserSession() as session:
            html = await session.fetch_html(url)
        return self.scraper.extract_film_casting(html)

    async def run(self):
        if not os.path.exists(self.input_csv_path):
            raise FileNotFoundError(f"CSV file not found at {self.input_csv_path}")

        print(f"🔧 Enriching: {self.input_csv_path} -> {self.output_csv_path}")

        # Read all input rows
        with open(self.input_csv_path, mode="r", encoding="utf-8") as f_in:
            reader = list(csv.DictReader(f_in))

        existing_enriched_visas = set()
        writer_needs_header = True

        # Check if enriched file exists already and load previously enriched film_ids
        if os.path.exists(self.output_csv_path):
            with open(self.output_csv_path, mode="r", encoding="utf-8") as f_out:
                existing_reader = csv.DictReader(f_out)
                existing_enriched_visas = {row["visa_number"] for row in existing_reader}
            writer_needs_header = False  # File already has header

        with open(self.output_csv_path, mode="a", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=self.CSV_HEADERS)

            if writer_needs_header:
                writer.writeheader()

            for row in tqdm(reader, desc="🔧 Enriching Allociné rows"):
                visa_number = row.get("visa_number")
                allocine_id_raw = row.get("allocine_id")

                if visa_number in existing_enriched_visas:
                    continue

                try:
                    allocine_id = int(allocine_id_raw)
                    if allocine_id <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    writer.writerow(row)
                    continue

                try:
                    details = await self.fetch_film_details(allocine_id)

                    allocine_visa_number = int(details.get("allocine_visa_number")) if str(details.get("allocine_visa_number")).isdigit() and int(details.get("allocine_visa_number")) > 0 else -1
                    row_visa_number = int(row.get("visa_number")) if str(row.get("visa_number")).isdigit() and int(row.get("visa_number")) > 0 else -1
                    # Actually it happens for ~25 films that allocine_visa_number is different from cnc visa_number
                    if allocine_visa_number > 0 and allocine_visa_number != row_visa_number:
                        print(f"⚠️ Mismatched visa number for Allociné ID {allocine_id}: {allocine_visa_number} != {row_visa_number}")
                        writer.writerow(row)
                        continue

                    casting = await self.fetch_film_casting(allocine_id)
                    combined_data = {**details, **casting}

                    for key in combined_data:
                        value = combined_data[key]
                        row[key] = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value

                except Exception as e:
                    print(f"❌ Error enriching film ID {allocine_id}: {e}")

                writer.writerow(row)

        # Replace input only if needed
        print(f"✅ Enriched CSV saved to: {self.output_csv_path}")
