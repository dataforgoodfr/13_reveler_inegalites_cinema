# Scraping Allocine

Ces scripts cherchent les films dans Allocine, recuperent leurs pages, puis transforment le HTML en donnees CSV exploitables par les seeders.

## Algorithme

1. [allocine_film_matcher.py](allocine_film_matcher.py) lit le mart dbt `marts.mart_cnc_films_for_scraping` via SQLAlchemy.
2. Il ne traite que les lignes ou `should_scrape_allocine = true`.
3. Attention: ce mart est actuellement partiel. Sa logique de fusion CNC Airbyte + historique n'est pas implémentée et `should_scrape_allocine` reste temporaire.
4. Pour chaque film, il construit une recherche Allocine avec le titre original consolide et l'annee d'agrement CNC.
5. [scraping_browser.py](../scraping_browser.py) ouvre la page avec Playwright, attend, scrolle, puis retourne le HTML.
6. [allocine_scraper.py](allocine_scraper.py) parse le premier resultat film et extrait `allocine_id`, titre et URL.
7. Le matcher ajoute le resultat dans `allocine_matches.csv`.
8. [allocine_film_enricher.py](allocine_film_enricher.py) relit ce CSV et visite deux pages par film:
   - fiche film: visa, affiche, date de sortie, duree, genres, trailer;
   - page casting: realisation, acteurs, scenario, production, equipe, musique, distribution, societes.
9. L'enricher ecrit un CSV suffixe `_enriched.csv`.

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

Prerequis supplementaire: le schema `marts` et la table `marts.mart_cnc_films_for_scraping` doivent exister et etre lisibles par le role utilise dans `DATABASE_URL`.

## Limites connues

- Le matcher garde le premier resultat Allocine trouve; un controle manuel peut etre necessaire.
- Le matcher depend maintenant du mart dbt; un `dbt build` doit avoir ete execute avant le scraping.
- Le mart dbt est partiel: il ne doit pas encore etre considere comme source fiable pour un scraping complet.
- Les selecteurs CSS dependent du HTML Allocine.
- L'enricher ignore l'enrichissement quand le numero de visa Allocine contredit le visa CNC.
