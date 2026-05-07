**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author         | Observations                                                                 |
|------------|----------------|------------------------------------------------------------------------------|
| 2025       | Francois       | Implementation initiale du code de base de donnees pendant la saison 13 D4G |
| 2026-05-07 | Joel Teixeira  | Revue, documentation et normalisation des metadonnees                        |

# Base de données

Ce dossier regroupe la configuration PostgreSQL locale, les modèles SQLAlchemy, les migrations Alembic, les scripts de seed et les données historiques utilisées par le projet RIC.

## Role du dossier

`database/` décrit et alimente les tables applicatives `ric_*` consommées par le backend FastAPI. Il ne contient pas la nouvelle couche Airbyte/dbt, qui vit dans `ingestion/`.

Le flux actuel reste principalement manuel:

1. les données source ou scrapées sont stockées dans `database/data/`;
2. les scripts `database/seed/seed_*.py` lisent ces fichiers;
3. les scripts créent ou mettent à jour les tables `ric_*` via SQLAlchemy;
4. le backend lit ensuite ces tables avec ses repositories.

## Structure

```text
database/
|-- alembic/                  # environnement Alembic et migrations versionnées
|-- data/                     # données source, scrapers historiques, CSV intermédiaires
|-- models/                   # modèles SQLAlchemy des tables applicatives ric_*
|-- seed/                     # scripts d'insertion ou mise a jour en base
|-- database.py               # engine SQLAlchemy, SessionLocal, Base et get_db
|-- alembic.ini               # configuration Alembic
`-- Dockerfile                # image PostgreSQL locale basee sur postgres:16-alpine
```

## Configuration SQLAlchemy

`database.py` charge `DATABASE_URL` et `DATABASE_SCHEMA` depuis l'environnement avec `python-dotenv`, crée l'engine SQLAlchemy, expose `SessionLocal` et déclare `Base`. `DATABASE_SCHEMA` vaut `public` par défaut.

Le backend utilise `get_db()` comme dépendance FastAPI pour ouvrir et fermer une session par requête.

Prerequis:

```bash
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ric_db
export DATABASE_SCHEMA=public
```

En local avec `docker-compose.yaml`, la base exposee par defaut est:

1. host: `localhost`
2. port: `5432`
3. database: `ric_db`
4. user: `postgres`
5. password: `postgres`

## Modeles SQLAlchemy

Les modèles dans `database/models/` représentent les tables applicatives:

1. `ric_films`: films, données CNC, identifiants externes Allocine/MUBI, métadonnées principales.
2. `ric_countries`: pays.
3. `ric_genres` et `ric_films_genres`: genres et table d'association film/genre.
4. `ric_credit_holders`: personnes ou societes creditees.
5. `ric_roles`: rôles métier, rôles Allocine et libellés inclusifs.
6. `ric_film_credits`: association film/rôle/personne ou société.
7. `ric_film_country_budget_allocations`: repartition de budget par pays.
8. `ric_festivals`, `ric_festival_awards`, `ric_award_nominations`: festivals, prix et nominations.
9. `ric_posters`, `ric_poster_characters`: affiches et predictions de personnages sur affiches.
10. `ric_trailers`, `ric_trailer_characters`: bandes-annonces et predictions de personnages sur trailers.

## Migrations Alembic

`database/alembic/versions/` contient les migrations qui créent et font évoluer les tables `ric_*`.

Commandes usuelles depuis la racine du repo:

```bash
poetry run alembic -c database/alembic.ini upgrade head
poetry run alembic -c database/alembic.ini revision --autogenerate -m "description"
```

Alembic importe `database.models` dans `database/alembic/env.py`, donc les nouveaux modèles doivent être exportés/importables depuis ce package pour être pris en compte par l'autogénération.

## Donnees et extractions

`database/data/` contient les sources historiques et scripts de collecte:

1. `cnc/`: fichier Excel CNC versionné et script d'extraction `extract_cnc_data_from_excel.py`.
2. `allocine/`: matcher, enricher, parser BeautifulSoup et CLI `allocine_runner.py`.
3. `mubi/`: classes de scraping MUBI et export `films_all_awards.csv`.
4. `machine_learning_predictions/`: CSV de predictions poster/trailer produits par la pipeline ML.
5. `sample/`: données de sample et seed minimal.
6. `scraping_browser.py`: session Playwright asynchrone connectée à un Chromium distant via `PLAYWRIGHT_WS_ENDPOINT`.

Voir aussi:

1. [database/data/README.md](data/README.md)
2. [database/data/allocine/README.md](data/allocine/README.md)
3. [database/data/mubi/README.md](data/mubi/README.md)

## Scripts de seed

Les scripts dans `database/seed/` alimentent les tables applicatives depuis les fichiers versionnés ou générés:

1. `seed_cnc_movies.py`: lit le fichier Excel CNC nettoyé et crée les films, allocations budgétaires et certains crédits diffuseurs.
2. `seed_allocine_movies_details.py`: lit `database/data/allocine/allocine_matches_enriched.csv`, met à jour les films et crée genres, trailers, posters et crédits Allocine.
3. `seed_film_awards.py`: lit `database/data/mubi/films_all_awards.csv`, matche les films et crée festivals, prix et nominations.
4. `seed_poster_predictions.py`: lit `database/data/machine_learning_predictions/poster_predictions.csv` et recrée les personnages d'affiches.
5. `seed_trailer_predictions.py`: lit `database/data/machine_learning_predictions/trailer_predictions.csv` et recrée les personnages de trailers.

Exemples:

```bash
poetry run python -m database.seed.seed_cnc_movies
poetry run python -m database.seed.seed_allocine_movies_details
poetry run python -m database.seed.seed_film_awards
poetry run python -m database.seed.seed_poster_predictions
poetry run python -m database.seed.seed_trailer_predictions
```

Attention: certains seeders mettent à jour ou suppriment/recréent des données sur leur périmètre. Vérifier la base cible via `DATABASE_URL` avant exécution.

## Limites actuelles

1. La chaîne d'alimentation reste manuelle et basée sur des CSV intermédiaires.
2. Les scrapers Allocine/MUBI sont encore dans `database/data/`, même si la cible documentée prévoit une intégration future avec Airbyte ou une orchestration dédiée.
3. Le backend lit encore les tables `ric_*` directement, pas des marts dbt curated.
4. Les notebooks ne sont pas testes automatiquement.
5. Les données versionnées incluent des exports intermédiaires qui peuvent devenir obsolètes.

## Referenced by

- [README.md](../README.md)
