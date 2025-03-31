import os
import pathlib
import re
import sys
import json
import asyncio
from urllib.parse import quote
import urllib

import argparse
import pandas as pd
import requests
from loguru import logger
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from SPARQLWrapper import SPARQLWrapper, JSON
import tqdm


class WikidataQuery:
    def __init__(self, endpoint_url: str = "https://query.wikidata.org/sparql"):
        self.endpoint_url = endpoint_url

    @staticmethod
    def format_metacritic(title: str) -> str:
        """Format the title for the Metacritic search URL."""
        title = title.replace(" ", "-").lower()
        title = title.replace(",", "")
        # Remove quotes
        title = re.sub(r'["“”]', '', title)
        title = title.split(":")[0]
        title = title.lower()
        return f"movie/{title}"

    def make_query_by_metacritic(self, metacritic_value: str) -> str:
        """Use the Metacritic value to query Wikidata."""
        return f"""
        SELECT DISTINCT ?item ?itemLabel ?titre ?identifiant_AlloCiné_titre WHERE {{
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[FR]". }}
          {{
            SELECT DISTINCT ?item WHERE {{
              ?item p:P1712 ?statement0.
              ?statement0 ps:P1712 "{metacritic_value}".
            }}
            LIMIT 100
          }}
          OPTIONAL {{ ?item wdt:P1265 ?identifiant_AlloCiné_titre. }}
        }}
        """

    def make_query_by_visa(self, p2755_value: str) -> str:
        """Use the VISA value to query Wikidata."""
        return f"""
        SELECT DISTINCT ?item ?itemLabel ?titre ?identifiant_AlloCiné_titre WHERE {{
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[FR]". }}
          {{
            SELECT DISTINCT ?item WHERE {{
              ?item p:P2755 ?statement0.
              ?statement0 ps:P2755 "{p2755_value}".
            }}
            LIMIT 100
          }}
          OPTIONAL {{ ?item wdt:P1265 ?identifiant_AlloCiné_titre. }}
        }}
        """

    def get_results(self, query: str) -> dict:
        """Get results from the SPARQL endpoint."""
        user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
        sparql = SPARQLWrapper(self.endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    def get_allocine_url(self, results: dict) -> str | None:
        """Get the Allocine URL from the results."""
        try:
            allocine_id = results["results"]["bindings"][0]["identifiant_AlloCiné_titre"]["value"]
        except (IndexError, KeyError):
            return None
        url = f"https://www.allocine.fr/film/fichefilm_gen_cfilm={allocine_id}.html"
        return url

    def get_url_from_wikidata(self, row: pd.Series) -> str | None:
        query = self.make_query_by_visa(row["VISA"])
        results = self.get_results(query)
        url = self.get_allocine_url(results)
        # Try to get the URL using Metacritic if the VISA query fails
        if not url:
            metacritic = self.format_metacritic(row["TITRE"])
            query = self.make_query_by_metacritic(metacritic)
            try:
                results = self.get_results(query)
            except (urllib.error.URLError,
                    SPARQLWrapper.SPARQLExceptions.QueryBadFormed):
                return None
            url = self.get_allocine_url(results)
        return url


class MediaDownloader:
    @staticmethod
    def download_image(url: str, output_path: str) -> str:
        response = requests.get(url, stream=True)
        with open(output_path, 'wb') as f:
            for chunk in response:
                f.write(chunk)
        return output_path


class AllocineScraper:
    def __init__(self, download: bool = False):
        self.download = download

    def get_data_from_url(
        self, url: str, output_poster: str = 'downloaded_poster'
    ) -> dict[str, str]:
        os.makedirs("example", exist_ok=True)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract poster
        poster_url = ""
        poster_tag = soup.find('meta', property='og:image')
        if poster_tag is not None:
            poster_url = poster_tag['content']
            if self.download:
                poster_path = MediaDownloader.download_image(
                    poster_url, os.path.join('example', f'{output_poster}.jpg'))

        # Extract trailer info
        video_path = ""
        quality = ""
        figure_tag = soup.find('figure', class_='player')
        if figure_tag:
            data_model = json.loads(figure_tag['data-model'])
            video_sources = data_model.get('videos', [{}])[
                0].get('sources', {})
            # quality sorted by preference
            for q in ["medium", "high", "low", "standard"]:
                if q in video_sources:
                    video_path = video_sources[q]
                    quality = q
                    break

        return {"poster_path": poster_url,
                "trailer_path": video_path,
                "quality": quality}


class AllocineSearch:
    base_url = "https://www.allocine.fr"

    def format_query(self, title: str) -> str:
        """Formats the title for the Allocine search URL.
        """
        title = title.replace(" - ", "+").lower()
        title = title.replace(" ", "+")
        return f"{self.base_url}/rechercher/?q={quote(title)}"

    async def search_movie_url(self, title: str, page) -> list[str]:
        await page.goto(self.format_query(title))
        links = await page.query_selector_all('a.meta-title-link')
        return [
            self.base_url + await link.get_attribute('href')
            for link in links
            if "film/fichefilm_gen_cfilm=" in await link.get_attribute('href')
        ]

    async def fetch_allocine_urls(
        self, df: pd.DataFrame, year: str, output_dir: pathlib.Path
    ) -> None:
        """Fetches Allocine URLs for movies in the given DataFrame (typically
        1 year of CNC movies).
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            for idx, row in tqdm.tqdm(df.iterrows(), total=len(df)):
                title = row["TITRE"]
                logger.info(f"Searching for {title}...")
                urls = await self.search_movie_url(title, page)
                if len(urls) == 0:
                    logger.warning(f"Could not find URL for {title}")
                    continue
                if len(urls) > 1:
                    logger.warning(
                        f"Multiple URLs found for {title}: {urls}. Keeping the "
                        "first one")
                df.loc[idx, "allocine_url"] = urls[0]
            await browser.close()
        output_file = output_dir / f"allocine_url_{year}.csv"
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, encoding="utf-8-sig", index=False)
        logger.success(f"Saved results in {output_file}")


def main(start: int,
         end: int,
         output_dir: pathlib.Path,
         path_to_cnc_xlsx: pathlib.Path) -> None:
    """Main function to scrape Allocine URLs and posters."""
    wikidata = WikidataQuery()
    scraper = AllocineScraper()
    searcher = AllocineSearch()

    cnc_xls = pd.ExcelFile(path_to_cnc_xlsx)

    missing_url = 0

    pd_dict = {}

    for year in range(start, end + 1):
        logger.info(f"Processing year {year}...")
        df = pd.read_excel(cnc_xls, sheet_name=str(year), header=4)

        asyncio.run(searcher.fetch_allocine_urls(
            df, str(year), output_dir=output_dir))

        for idx, row in tqdm.tqdm(df.iterrows(), total=len(df)):
            url = row.get("allocine_url")
            if pd.isna(url):
                url = wikidata.get_url_from_wikidata(row)
                if url is None:
                    logger.warning(
                        f"URL is empty for {row.TITRE} (idx {idx}). Skipping.")
                    missing_url += 1
                    continue
                df.loc[idx, "allocine_url"] = url
                logger.success(
                    f"Retrieved URL for {row.TITRE}!")
            data = scraper.get_data_from_url(url=url)
            df.loc[idx, ["poster_path", "trailer_path", "quality"]] = [
                data.get("poster_path", ""),
                data.get("trailer_path", ""),
                data.get("quality", "")]
        df["year"] = year
        pd_dict[year] = df

        df.to_csv(
            output_dir / f"allocine_url_{year}_TESST.csv", encoding="utf-8-sig", index=False)

    df_all = pd.concat(pd_dict.values(), ignore_index=True)
    output_path = output_dir / f"allocine_url_{start}-{end}.csv"
    df_all.to_csv(output_path, encoding="utf-8-sig", index=False)

    logger.success(f"Saved results in {output_path}")
    logger.info(f"fiche film URL still missing for {missing_url} movies")


if __name__ == "__main__":
    aparser = argparse.ArgumentParser(
        description="Allocine URL and poster scraper")
    aparser.add_argument("--years",
                         type=int,
                         nargs='+',
                         default=[2003, 2023],
                         help="Years to scrape Allocine URLs and posters")
    aparser.add_argument("--path-to-cnc-xlsx",
                         type=pathlib.Path,
                         default=pathlib.Path("/workspace/d4g/cnc.xlsx"),
                         help="Path to CNC xlsx file")
    aparser.add_argument("--output-dir",
                         type=pathlib.Path,
                         default=pathlib.Path("/workspace/d4g/"),
                         help="Output directory for scraped data")
    args = aparser.parse_args()

    START = args.years[0]
    END = args.years[1]
    if START > END:
        raise ValueError("Start year must be less than or equal to end year")

    main(start=START, end=END, output_dir=args.output_dir,
         path_to_cnc_xlsx=args.path_to_cnc_xlsx)
