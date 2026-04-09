# Scraping Allocine

Ces scripts cherchent les films dans Allocine, recuperent leurs pages, puis transforment le HTML en donnees CSV exploitables par les seeders.

## Algorithme

1. [allocine_film_matcher.py](allocine_film_matcher.py) lit les films en base via SQLAlchemy.
2. Pour chaque film, il construit une recherche Allocine avec le titre original et l'annee d'agrement CNC.
3. [scraping_browser.py](../scraping_browser.py) ouvre la page avec Playwright, attend, scrolle, puis retourne le HTML.
4. [allocine_scraper.py](allocine_scraper.py) parse le premier resultat film et extrait `allocine_id`, titre et URL.
5. Le matcher ajoute le resultat dans `allocine_matches.csv`.
6. [allocine_film_enricher.py](allocine_film_enricher.py) relit ce CSV et visite deux pages par film:
   - fiche film: visa, affiche, date de sortie, duree, genres, trailer;
   - page casting: realisation, acteurs, scenario, production, equipe, musique, distribution, societes.
7. L'enricher ecrit un CSV suffixe `_enriched.csv`.

## Fichiers

- [allocine_runner.py](allocine_runner.py): point d'entree CLI.
- [allocine_film_matcher.py](allocine_film_matcher.py): matching film CNC -> resultat Allocine.
- [allocine_film_enricher.py](allocine_film_enricher.py): enrichissement depuis les pages Allocine.
- [allocine_scraper.py](allocine_scraper.py): selecteurs CSS et fonctions de parsing BeautifulSoup.
- [allocine_matches_enriched.csv](allocine_matches_enriched.csv): export enrichi versionne dans ce repo.

## Lancer

Depuis la racine du repo:

```bash
poetry run python -m database.data.allocine.allocine_runner --matcher --csv database/data/allocine/allocine_matches.csv
poetry run python -m database.data.allocine.allocine_runner --enricher --csv database/data/allocine/allocine_matches.csv
```

Prerequis: base PostgreSQL accessible, backend configure, Chromium distant lance, variable `PLAYWRIGHT_WS_ENDPOINT` definie.

## Limites connues

- Le matcher garde le premier resultat Allocine trouve; un controle manuel peut etre necessaire.
- Les selecteurs CSS dependent du HTML Allocine.
- L'enricher ignore l'enrichissement quand le numero de visa Allocine contredit le visa CNC.
