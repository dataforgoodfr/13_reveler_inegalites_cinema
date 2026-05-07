**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author         | Observations                                |
|------------|----------------|---------------------------------------------|
| 2026-05-07 | OpenAI Codex   | Ajout du fallback sur le CSV enrichi de backup par numero de visa |
| 2026-05-07 | Joel Teixeira  | Ajout du bloc de metadonnees et normalisation |

# Scraping Allocine

Ces scripts cherchent les films dans Allocine, recuperent leurs pages, puis transforment le HTML en donnees CSV exploitables par les seeders.

## Algorithme

1. [allocine_film_matcher.py](allocine_film_matcher.py) lit les films applicatifs en base via SQLAlchemy.
2. Il ignore les visas deja presents dans le CSV de matching pour permettre une reprise incrementale.
3. Il verifie ensuite si le numero de visa existe deja dans `allocine_matches_enriched.csv`; si oui, il reutilise les champs Allocine du backup et ne scrape pas le site.
4. Sinon, il construit une recherche Allocine avec le titre original et l'annee d'agrement CNC.
5. [scraping_browser.py](../scraping_browser.py) ouvre la page avec Playwright, attend, scrolle, puis retourne le HTML.
6. [allocine_scraper.py](allocine_scraper.py) parse le premier resultat film et extrait `allocine_id`, titre et URL.
7. Le matcher ajoute le resultat dans `allocine_matches.csv`.
8. [allocine_film_enricher.py](allocine_film_enricher.py) relit ce CSV et reutilise aussi `allocine_matches_enriched.csv` comme backup si le visa existe deja; sinon il visite deux pages par film:
   - fiche film: visa, affiche, date de sortie, duree, genres, trailer;
   - page casting: realisation, acteurs, scenario, production, equipe, musique, distribution, societes.
9. L'enricher ecrit un CSV suffixe `_enriched.csv`.
10. `seed_allocine_movies_details.py` injecte le CSV enrichi en base, met a jour `allocine_id`, la fiche film et les relations associees.

## Statut

Ce dossier decrit le flux historique manuel.

Depuis 2026-05-07, un job standalone existe aussi dans [../../../ingestion/scraping/allocine/README.md](../../../ingestion/scraping/allocine/README.md). Il reutilise le parser HTML existant, mais sort un flux `allocine_data` au lieu des CSV versionnes.

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
- Le fallback par backup suppose que `allocine_matches_enriched.csv` reste une source de reference fiable par numero de visa.
- Le matcher depend de `ric_films`: le seed CNC doit avoir ete execute avant le scraping.
- Les selecteurs CSS dependent du HTML Allocine.
- L'enricher ignore l'enrichissement quand le numero de visa Allocine contredit le visa CNC.
- Le flux cible retenu n'est plus un connecteur Airbyte: c'est un job standalone dans `ingestion/scraping/allocine/`.

## Referenced by

- [database/README.md](../../README.md)
- [database/data/README.md](../README.md)
