# Scraping MUBI

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-08

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations           |
| --- | ---------- | ------------- | ---------------------- |
| 1   | 2026-05-07 | Joel Teixeira | Initial implementation |

Ces scripts collectent les films listes sur des pages de festivals MUBI, puis recuperent les prix et nominations visibles sur les pages awards de chaque film.

## Algorithme

1. [mubi_all_festival_films_to_csv.py](mubi_all_festival_films_to_csv.py) parcourt un festival, une plage d'annees et plusieurs pages.
2. [scraping_browser.py](../scraping_browser.py) ouvre chaque page MUBI avec Playwright, attend, scrolle, puis retourne le HTML rendu.
3. [mubi_page_scraper.py](mubi_page_scraper.py) parse la liste de films: titre, realisateur, pays, nominations et lien MUBI.
4. Les lignes sont ajoutees dans un CSV de films de festival.
5. [mubi_all_film_awards_to_csv.py](mubi_all_film_awards_to_csv.py) relit ce CSV, visite `/{film}/awards`, parse toutes les recompenses, puis ecrit un CSV d'awards.
6. Un fichier `processed_links.txt` peut memoriser les films deja enrichis.

## Fichiers

- [mubi_page_scraper.py](mubi_page_scraper.py): URLs, selecteurs CSS et parsing BeautifulSoup.
- [mubi_all_festival_films_to_csv.py](mubi_all_festival_films_to_csv.py): collecte paginee des films d'un festival.
- [mubi_all_film_awards_to_csv.py](mubi_all_film_awards_to_csv.py): enrichissement des films avec awards/nominations.
- [films_all_awards.csv](films_all_awards.csv): export d'awards versionne dans ce repo.
- [mubi_scraping_sandbox.ipynb](mubi_scraping_sandbox.ipynb): notebook d'experimentation.

## Lancer

Les fichiers actuels exposent des classes asynchrones. Ils ne declarent pas de CLI.

Exemple minimal depuis la racine du repo:

```bash
poetry run python - <<'PY'
import asyncio
from database.data.mubi.mubi_all_festival_films_to_csv import MubiAllFestivalFilmsToCsv

asyncio.run(
    MubiAllFestivalFilmsToCsv(
        csv_file="database/data/mubi/festival_films.csv",
        festival="cesars",
        start_year=2024,
        end_year=2024,
        max_pages=2,
    ).run()
)
PY
```

Prerequis: Chromium distant lance et variable `PLAYWRIGHT_WS_ENDPOINT` definie.

## Limites connues

- Les selecteurs CSS MUBI sont des classes generees; ils peuvent changer.
- Le script redemarre regulierement la session navigateur pour limiter les blocages.
- La collecte d'awards est volontairement bornee par `max_total_requests` par defaut.

## Referenced by

- [database/README.md](../../README.md)
- [database/data/README.md](../README.md)
