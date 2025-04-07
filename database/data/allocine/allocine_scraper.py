from bs4 import BeautifulSoup
import re
import json

class AllocineScraper:
    BASE_URL    = "https://www.allocine.fr"
    SEARCH_URL  = f"{BASE_URL}/rechercher/?q={{film_title_url_styled}}"
    FILM_URL    = f"{BASE_URL}/film/fichefilm_gen_cfilm={{allocine_film_id}}.html"
    FILM_CASTING_URL = f"{BASE_URL}/film/fichefilm-{{allocine_film_id}}/casting/"

    DEFAULT_SEARCH_FILTERS = { "film_title_url_styled" : "the+substance" }
    DEFAULT_FILM_FILTERS = { "allocine_film_id" : "314885" }

    SEARCH_SELECTORS = {
        "films": "a.meta-title-link"
    }

    FILM_SELECTORS = {
        "poster_url": "div.entity-card img.thumbnail-img",
        "release_date": "div.meta-body-info a.date.blue-link",
        "duration": "div.meta-body-item.meta-body-info",
        "genres": "div.meta-body-info a.dark-grey-link"
    }

    FILM_CASTING_SELECTORS = {
        "directors_section": "section.casting-director",
        "actors_section": "section.casting-actor",
        "other_roles_sections": "div.casting-list-gql",
        "section_title": "h2.titlebar-title",
        "directors_and_actors_names": "a.meta-title-link",
        "other_roles_credit": "div.md-table-row",
        "screenwriter_credit_role": "a.item.link-light",
        "screenwriter_credit_name": "span.item.link-empty",
        "distributor_credit_role": "span.item.light",
        "distributor_credit_name": "span.item.isnt-clickable",
        "credit_role": "span.item.light",
        "credit_name": "a.item.link",
    }

    def extract_searched_first_film(self, html: str) -> list[dict]:
        """
        Extracts a list of films from the search results HTML page.

        Args:
            html (str): Raw HTML content of the search results page.

        Returns:
            list[dict]: A list of dictionaries with allocine film title, id, and link.
        """
        soup = BeautifulSoup(html, "html.parser")
        film_elements = soup.select(self.SEARCH_SELECTORS["films"])
        films = []

        for film in film_elements:
            link = film["href"]
            match = re.search(r'/(\w+)/(\w+)_gen_c(\w+)=([0-9]+)\.html', link)
            if match:
                content_type = match.group(2)  # e.g. fichefilm or fichearticle
                if content_type != "fichefilm":
                    continue
                allocine_film_id = int(match.group(4))
                films.append({
                    'title': film.get_text(strip=True),
                    'id': allocine_film_id,
                    'link': link
                })

        return films[0] if films else None

    def extract_film_details(self, html: str):
        """
        Extracts film details from an Allociné film page.

        Args:
            html (str): Raw HTML content of the festival edition page.

        Returns:
            List[Dict[str, Optional[str]]]: A list of dictionaries with film details such as
            poster_url, release_date, duration, genres, trailer_url.
        """
        soup = BeautifulSoup(html, "html.parser")
        poster_url = soup.select_one(self.FILM_SELECTORS["poster_url"])
        release_date = soup.select_one(self.FILM_SELECTORS["release_date"])
        raw_duration = soup.select_one(self.FILM_SELECTORS["duration"])
        genres = soup.select(self.FILM_SELECTORS["genres"])
        allocine_visa_div = soup.find('div', class_='item', text=lambda t: t and 'N° de Visa' in t)
        
        # Specific retrieval for allocine visa number
        allocine_visa_div = soup.find('div', class_='item', text=lambda t: t and 'N° de Visa' in t)
        if not allocine_visa_div:
            # Fallback if text is nested, like in your case
            allocine_visa_div = next(
                div for div in soup.find_all('div', class_='item')
                if div.find('span', class_='what light') and 'N° de Visa' in div.find('span', class_='what light').text
            )

        # Specific retrieval for the trailer URL
        figure_tag = soup.find('figure', class_='player')
        if figure_tag and 'data-model' in figure_tag.attrs:
            data_model = json.loads(figure_tag['data-model'])
            video_sources = data_model['videos'][0].get('sources', {})
            preferred_order = ['standard', 'medium', 'high', 'low']
            trailer_url = next((video_sources[q] for q in preferred_order if q in video_sources), None)
        else:
            trailer_url = None

        # Specific retrieval for the duration
        if raw_duration:
            parts = raw_duration.get_text(strip=True).split('|')
            if len(parts) == 3:
                duration = parts[1].replace(' ', '')
            else:
                duration = None
        else:
            duration = None

        film_details = {
            "allocine_visa_number": allocine_visa_div.find('span', class_='that').text.strip() if allocine_visa_div else None,
            "poster_url": poster_url["src"] if poster_url else None,
            "release_date": release_date.get_text(strip=True) if release_date else None,
            "duration": duration,
            "genres": [genre.get_text(strip=True) for genre in genres] if genres else None,
            "trailer_url": trailer_url
        }

        return film_details

    def extract_film_casting(self, html: str) -> dict:
        """
        Extracts casting info from an Allociné film page.

        Returns:
            Dict[str, Any]: {
                "directors": [str],
                "actors": [str],
                "Scénaristes": [{"role": str, "name": str}],
                ...
            }
        """
        soup = BeautifulSoup(html, "html.parser")
        selectors = self.FILM_CASTING_SELECTORS

        # Fixed sections
        known_sections = ['Scénaristes', 'Production', 'Equipe technique', 'Soundtrack', 'Distribution', 'Sociétés']

        result = {
            "Direction": [],
            "Casting": [],
            **{section: [] for section in known_sections}
        }

        # Directors
        director_section = soup.select_one(selectors["directors_section"])
        if director_section:
            director_names = director_section.select(selectors["directors_and_actors_names"])
            result["Direction"] = [el.get_text(strip=True) for el in director_names]

        # Actors
        actor_section = soup.select_one(selectors["actors_section"])
        if actor_section:
            actor_names = actor_section.select(selectors["directors_and_actors_names"])
            result["Casting"] = [el.get_text(strip=True) for el in actor_names]

        # Other roles (writers, composers, editors, etc.)
        other_sections = soup.select(selectors["other_roles_sections"])
        for section in other_sections:
            title_el = section.select_one(selectors["section_title"])
            section_title = title_el.get_text(strip=True) if title_el else None

            if section_title not in known_sections:
                continue  # Skip anything not in our fixed list

            credits = []
            credit_blocks = section.select(selectors["other_roles_credit"])
            for credit in credit_blocks:
                role = name = None

                # Try screenwriter selectors
                screenwriter_role_el = credit.select_one(selectors.get("screenwriter_credit_role", ""))
                screenwriter_name_el = credit.select_one(selectors.get("screenwriter_credit_name", ""))
                if screenwriter_role_el and screenwriter_name_el:
                    role = screenwriter_role_el.get_text(strip=True)
                    name = screenwriter_name_el.get_text(strip=True)

                # Try distributor selectors if not found yet
                if not (role and name):
                    distributor_role_el = credit.select_one(selectors.get("distributor_credit_role", ""))
                    distributor_name_el = credit.select_one(selectors.get("distributor_credit_name", ""))
                    if distributor_role_el and distributor_name_el:
                        role = distributor_role_el.get_text(strip=True)
                        name = distributor_name_el.get_text(strip=True)

                # Fallback to default selectors
                if not (role and name):
                    # Fall back to default selectors
                    role_el = credit.select_one(selectors.get("credit_role", ""))
                    name_el = credit.select_one(selectors.get("credit_name", ""))
                    role = role_el.get_text(strip=True) if role_el else None
                    name = name_el.get_text(strip=True) if name_el else None

                if role and name:
                    credits.append({"role": role, "name": name})

            result[section_title] = credits

        return result


    def _reformat_str_for_url(self, title: str) -> str:
        """Reformats a string for use in a URL.
        """
        title = title.replace(" - ", "+").lower()
        title = title.replace(" ", "+")
        return title