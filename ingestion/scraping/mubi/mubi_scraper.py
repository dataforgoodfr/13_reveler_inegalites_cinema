import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class MubiPageScraper:
    BASE_URL = "https://mubi.com"
    ALL_FESTIVALS_URL = f"{BASE_URL}/fr/awards-and-festivals?type={{festival_or_award}}&page={{page_num}}"
    FESTIVAL_EDITION_ALL_FILMS_URL = f"{BASE_URL}/fr/awards-and-festivals/{{festival}}?page={{page_num}}&year={{year}}"
    FILM_ALL_AWARDS_URL = f"{BASE_URL}{{film_link}}/awards"
    # Awards page addressed by the numeric Mubi film id. Mubi redirects this to
    # the localized slug URL, so it resolves even though we only know the id
    # (e.g. from the CNC id_matching sheet). Kept on the /fr/ locale so the
    # awards' full_display_text matches the French distinctions parsed by
    # _parse_reward (Lauréat / Nommé / ...).
    FILM_ALL_AWARDS_BY_ID_URL = f"{BASE_URL}/fr/films/{{mubi_id}}/awards"

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
        # title is the only <h3> inside a movie <li>; matching the tag rather than
        # a hashed css-* class avoids breaking when Mubi rotates the class names.
        "title": "h3",
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
                "link": self._normalize_film_link(link["href"]) if link else None,
            })
        return movies

    @staticmethod
    def _normalize_film_link(href: Optional[str]) -> Optional[str]:
        """Strip the locale prefix from a film link, keeping '/films/{slug}'.

        Mubi serves the same film under varying locale segments
        (e.g. '/fr/fr/films/echo-1999' vs '/fr/us/films/echo-1999'), which
        creates spurious distinct links for one film. We store the canonical
        '/films/{slug}' form. Mubi redirects this path to its localized URL, so
        it still resolves correctly for FILM_ALL_AWARDS_URL. Links without a
        '/films/' segment are returned unchanged.
        """
        if not href:
            return href
        marker = "/films/"
        idx = href.find(marker)
        if idx == -1:
            return href
        return href[idx:]

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
        film = self._next_page_props(html).get("film") or {}
        film_id = film.get("id")
        try:
            return int(film_id) if film_id is not None else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _next_page_props(html: str) -> Dict:
        """Return props.pageProps from the embedded Next.js __NEXT_DATA__ payload.

        Returns an empty dict when the payload is absent or unparseable, so
        callers can treat a missing payload the same as missing fields.
        """
        soup = BeautifulSoup(html, "html.parser")
        script = soup.select_one("script#__NEXT_DATA__")
        if not (script and script.string):
            return {}
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            return {}
        page_props = data.get("props", {}).get("pageProps", {})
        return page_props if isinstance(page_props, dict) else {}

    def extract_film_identity(self, html: str) -> Dict[str, Optional[object]]:
        """Canonical (mubi_id, film_link, mubi_slug) for the film page.

        film_link is the locale-stripped '/films/{slug}' form (same convention
        as _normalize_film_link) derived from film.web_url, so awards rows join
        cleanly with festival-film rows downstream.
        """
        film = self._next_page_props(html).get("film") or {}
        mubi_id = film.get("id")
        try:
            mubi_id = int(mubi_id) if mubi_id is not None else None
        except (ValueError, TypeError):
            mubi_id = None
        web_url = film.get("web_url")
        film_link = self._normalize_film_link(web_url) if web_url else None
        slug = film.get("slug")
        if not slug and film_link:
            slug = film_link.rstrip("/").split("/")[-1]
        return {"mubi_id": mubi_id, "film_link": film_link, "mubi_slug": slug}

    def extract_film_awards_structured(self, html: str) -> List[Dict[str, Optional[str]]]:
        """Awards from the structured pageProps.awards array of a film page.

        Each entry carries the industry event's name, slug and type, plus a
        localized 'full_display_text' (e.g. '2024 | Lauréat : Prix du scénario')
        which we parse with the same _parse_reward used for the HTML scrape, so
        the (year, distinction, award) fields stay identical to the prior
        festival-crawl output. event_slug / event_type are extra fields the CNC
        flow uses to drive the festival-edition scrape; they are ignored by the
        film-awards output mapping.
        """
        awards_raw = self._next_page_props(html).get("awards")
        if not isinstance(awards_raw, list):
            return []
        awards = []
        for entry in awards_raw:
            if not isinstance(entry, dict):
                continue
            event = entry.get("industry_event") or {}
            year, distinction, award_name = self._parse_reward(entry.get("full_display_text"))
            # Fall back to the structured fields when full_display_text is absent.
            if year is None and entry.get("year") is not None:
                year = str(entry.get("year"))
            if award_name is None:
                award_name = entry.get("display_text")
            awards.append({
                "festival": event.get("name"),
                "year": year,
                "distinction": distinction,
                "award": award_name,
                "event_slug": event.get("slug"),
                "event_type": event.get("type"),
            })
        return awards

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
