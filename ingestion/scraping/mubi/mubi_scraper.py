import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class MubiPageScraper:
    BASE_URL = "https://mubi.com"
    ALL_FESTIVALS_URL = f"{BASE_URL}/fr/awards-and-festivals?type={{festival_or_award}}&page={{page_num}}"
    FESTIVAL_EDITION_ALL_FILMS_URL = f"{BASE_URL}/fr/awards-and-festivals/{{festival}}?page={{page_num}}&year={{year}}"
    FILM_ALL_AWARDS_URL = f"{BASE_URL}{{film_link}}/awards"

    # Warning: hashed CSS class selectors (css-*) are rotated by Mubi and may need updating.
    # festival_link uses a structural href pattern instead of a class to be more resilient.
    ALL_FESTIVALS_SELECTORS = {
        "festival": "li.css-1bmn10l",
        "festival_link": "a[href*='/awards-and-festivals/']",
        "festival_name": "div.css-1o91brm",
    }

    FESTIVAL_EDITION_ALL_FILMS_SELECTORS = {
        "movie": "li.css-l31k08",
        "nominations": "div.css-gyp8mm",
        "title": "h3.css-1hr6q83",
        "director": "span.css-1vg6q84",
        "country": "span.css-ahepiu",
        "link": "a.css-122y91a",
    }

    FILM_ALL_AWARDS_SELECTORS = {
        "award": "div.css-epmkt5",
        "festival": "a.css-pgwez",
        "reward": "div.css-16kkjs",
    }

    def extract_all_festivals(self, html: str) -> List[Dict[str, Optional[str]]]:
        soup = BeautifulSoup(html, "html.parser")
        festival_elements = soup.select(self.ALL_FESTIVALS_SELECTORS["festival"])
        festivals = []
        for festival in festival_elements:
            festival_link = festival.select_one(self.ALL_FESTIVALS_SELECTORS["festival_link"])
            festival_name = festival.select_one(self.ALL_FESTIVALS_SELECTORS["festival_name"])
            festivals.append({
                "festival_link": festival_link["href"] if festival_link else None,
                "festival_name": festival_name.get_text(strip=True) if festival_name else None,
            })
        return festivals

    def extract_festival_edition_all_films(self, html: str) -> List[Dict[str, Optional[str]]]:
        soup = BeautifulSoup(html, "html.parser")
        movie_elements = soup.select(self.FESTIVAL_EDITION_ALL_FILMS_SELECTORS["movie"])
        movies = []
        for movie in movie_elements:
            title = movie.select_one(self.FESTIVAL_EDITION_ALL_FILMS_SELECTORS["title"])
            director = movie.select_one(self.FESTIVAL_EDITION_ALL_FILMS_SELECTORS["director"])
            country = movie.select_one(self.FESTIVAL_EDITION_ALL_FILMS_SELECTORS["country"])
            nominations = movie.select_one(self.FESTIVAL_EDITION_ALL_FILMS_SELECTORS["nominations"])
            link = movie.select_one(self.FESTIVAL_EDITION_ALL_FILMS_SELECTORS["link"])
            movies.append({
                "title": title.get_text(strip=True) if title else None,
                "director": director.get_text(strip=True) if director else None,
                "country": country.get_text(strip=True) if country else None,
                "nominations": nominations.get_text(strip=True) if nominations else None,
                "link": link["href"] if link else None,
            })
        return movies

    def extract_film_all_awards(self, html: str) -> List[Dict[str, Optional[str]]]:
        soup = BeautifulSoup(html, "html.parser")
        award_elements = soup.select(self.FILM_ALL_AWARDS_SELECTORS["award"])
        awards = []
        for award in award_elements:
            festival = award.select_one(self.FILM_ALL_AWARDS_SELECTORS["festival"])
            reward = award.select_one(self.FILM_ALL_AWARDS_SELECTORS["reward"])
            festival_name = festival.get_text(strip=True) if festival else None
            reward_text = reward.get_text(strip=True) if reward else None
            year, distinction, award_name = self._parse_reward(reward_text)
            awards.append({
                "festival": festival_name,
                "year": year,
                "distinction": distinction,
                "award": award_name,
            })
        return awards

    def extract_film_mubi_id(self, html: str) -> Optional[int]:
        """Extract numeric Mubi film ID from the page's Next.js __NEXT_DATA__ payload."""
        soup = BeautifulSoup(html, "html.parser")
        script = soup.select_one("script#__NEXT_DATA__")
        if script and script.string:
            try:
                data = json.loads(script.string)
                film_id = (
                    data.get("props", {})
                        .get("pageProps", {})
                        .get("film", {})
                        .get("id")
                )
                if film_id is not None:
                    return int(film_id)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        return None

    def _parse_reward(self, reward: str):
        """Parse reward text like '2023 | Lauréat : Prix d'interprétation masculine'."""
        year = distinction = award = None
        if reward and "|" in reward:
            parts = reward.split("|")
            year = parts[0].strip()
            if ":" in parts[1]:
                subparts = parts[1].split(":")
                distinction = subparts[0].strip()
                award = subparts[1].strip()
            else:
                award = parts[1].strip()
        else:
            award = reward.strip() if reward else None
        return year, distinction, award
