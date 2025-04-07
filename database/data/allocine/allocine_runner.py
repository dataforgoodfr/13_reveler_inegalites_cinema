import argparse
import asyncio

from database.data.allocine.allocine_film_matcher import AllocineFilmMatcher
from database.data.allocine.allocine_film_enricher import AllocineFilmEnricher

CSV_PATH = "allocine_matches.csv"

async def run_allocine_tools(run_matcher: bool, run_enricher: bool, csv_path: str):
    """
    Run the AllocineFilmMatcher and/or AllocineFilmEnricher.
    :param run_matcher: If True, run the AllocineFilmMatcher.
    :param run_enricher: If True, run the AllocineFilmEnricher.
    :param csv_path: Path to the CSV file.
    """
    if run_matcher:
        print("🔍 Running AllocineFilmMatcher...")
        matcher = AllocineFilmMatcher(csv_path)
        await matcher.run()
        print("✅ Matching complete.")

    if run_enricher:
        print("✨ Running AllocineFilmEnricher...")
        enricher = AllocineFilmEnricher(csv_path)
        await enricher.enrich_csv()
        print("✅ Enrichment complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Allociné Matcher and/or Enricher.")
    parser.add_argument("--matcher", action="store_true", help="Run AllocineFilmMatcher")
    parser.add_argument("--enricher", action="store_true", help="Run AllocineFilmEnricher")
    parser.add_argument("--csv", type=str, default=CSV_PATH, help="Path to CSV file")

    args = parser.parse_args()

    if not args.matcher and not args.enricher:
        parser.error("You must specify at least one of --matcher or --enricher")

    asyncio.run(run_allocine_tools(args.matcher, args.enricher, args.csv))
