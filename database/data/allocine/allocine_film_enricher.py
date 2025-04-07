import csv
import os
import json
import shutil
from typing import Optional, Dict
from tqdm import tqdm

from database.data.allocine.allocine_scraper import AllocineScraper
from database.data.scraping_browser import AsyncBrowserSession


class AllocineFilmEnricher:
    """
    AllocineFilmEnricher is a class that enriches a CSV file containing film data with additional
    information from Allociné, a French movie database. It uses the AllocineScraper to fetch data
    (film details and casting) from Allociné and updates the CSV file with the enriched data.
    """
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
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

    async def enrich_csv(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found at {self.csv_path}")

        temp_path = self.csv_path.replace(".csv", "_enriched.csv")
        print(f"🔧 Enriching CSV file: {self.csv_path} -> {temp_path}")

        with open(self.csv_path, mode="r", encoding="utf-8") as f_in:
            reader = list(csv.DictReader(f_in))
            original_fieldnames = reader[0].keys()
            print(f"Original fieldnames: {original_fieldnames}")

        enrichment_check_fields = ["description", "release_date", "Direction", "Casting"]
        added_fields = set()

        with open(temp_path, mode="w", newline="", encoding="utf-8") as f_out:
            writer = None

            for row in tqdm(reader, desc="🔧 Enriching Allociné rows"):
                try:
                    allocine_id_raw = row.get("allocine_id")
                    try:
                        allocine_id = int(allocine_id_raw)
                        if allocine_id <= 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        if writer is None:
                            all_fields = list(original_fieldnames)
                            writer = csv.DictWriter(f_out, fieldnames=all_fields)
                            writer.writeheader()
                        writer.writerow(row)
                        continue

                    already_enriched = all(
                        field in row and row[field] not in (None, "", "[]", "{}", "null")
                        for field in enrichment_check_fields
                    )

                    if not already_enriched:
                        details = await self.fetch_film_details(allocine_id)
                        casting = await self.fetch_film_casting(allocine_id)
                        combined_data = {**details, **casting}

                        for key, value in combined_data.items():
                            if isinstance(value, (dict, list)):
                                row[key] = json.dumps(value, ensure_ascii=False)
                            else:
                                row[key] = value

                        added_fields.update(combined_data.keys())

                except Exception as e:
                    print(f"❌ Error enriching film ID {row.get('allocine_id')}: {e}")

                if writer is None:
                    # Dynamically define headers on first iteration
                    all_fields = list(original_fieldnames) + [f for f in added_fields if f not in original_fieldnames]
                    writer = csv.DictWriter(f_out, fieldnames=all_fields)
                    writer.writeheader()

                writer.writerow(row)

        # Overwrite original file only after successful completion
        shutil.move(temp_path, self.csv_path)
        print(f"✅ CSV successfully enriched and saved to: {self.csv_path}")
