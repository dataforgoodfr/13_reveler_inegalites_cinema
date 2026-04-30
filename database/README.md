Owner: Joel Teixeira

Last reviewed: 2026-04-30

Status: active

History: Ce code a été implementé en 2025 pendant la saison 13 DataForGood, dans le cadre du projet RIC (Reveler les Inegalites au Cinema) par François ([fitzfoufou](https://github.com/fitzfoufou)). Il a été revu et documenté en 2026 pour faciliter la maintenance et les evolutions futures.

# Base de donnees

Ce dossier regroupe la configuration PostgreSQL locale, les modeles SQLAlchemy, les migrations Alembic, les scripts de seed et les donnees historiques utilisees par le projet RIC.

## Role du dossier

`database/` decrit et alimente les tables applicatives `ric_*` consommees par le backend FastAPI. Il ne contient pas la nouvelle couche Airbyte/dbt, qui vit dans `ingestion/`.

Le flux actuel reste principalement manuel:

1. les donnees source ou scrapees sont stockees dans `database/data/`;
2. les scripts `database/seed/seed_*.py` lisent ces fichiers;
3. les scripts creent ou mettent a jour les tables `ric_*` via SQLAlchemy;
4. le backend lit ensuite ces tables avec ses repositories.

## Structure

```text
database/
|-- alembic/                  # environnement Alembic et migrations versionnees
|-- data/                     # donnees source, scrapers historiques, CSV intermediaires
|-- models/                   # modeles SQLAlchemy des tables applicatives ric_*
|-- seed/                     # scripts d'insertion ou mise a jour en base
|-- database.py               # engine SQLAlchemy, SessionLocal, Base et get_db
|-- alembic.ini               # configuration Alembic
`-- Dockerfile                # image PostgreSQL locale basee sur postgres:16-alpine
```

## Configuration SQLAlchemy

`database.py` charge `DATABASE_URL` depuis l'environnement avec `python-dotenv`, cree l'engine SQLAlchemy, expose `SessionLocal` et declare `Base`.

Le backend utilise `get_db()` comme dependance FastAPI pour ouvrir et fermer une session par requete.

Prerequis:

```bash
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ric_db
```

En local avec `docker-compose.yaml`, la base exposee par defaut est:

1. host: `localhost`
2. port: `5432`
3. database: `ric_db`
4. user: `postgres`
5. password: `postgres`

## Modeles SQLAlchemy

Les modeles dans `database/models/` representent les tables applicatives:

1. `ric_films`: films, donnees CNC, identifiants externes Allocine/MUBI, metadonnees principales.
2. `ric_countries`: pays.
3. `ric_genres` et `ric_films_genres`: genres et table d'association film/genre.
4. `ric_credit_holders`: personnes ou societes creditees.
5. `ric_roles`: roles metier, roles Allocine et libelles inclusifs.
6. `ric_film_credits`: association film/role/personne ou societe.
7. `ric_film_country_budget_allocations`: repartition de budget par pays.
8. `ric_festivals`, `ric_festival_awards`, `ric_award_nominations`: festivals, prix et nominations.
9. `ric_posters`, `ric_poster_characters`: affiches et predictions de personnages sur affiches.
10. `ric_trailers`, `ric_trailer_characters`: bandes-annonces et predictions de personnages sur trailers.

## Migrations Alembic

`database/alembic/versions/` contient les migrations qui creent et font evoluer les tables `ric_*`.

Commandes usuelles depuis la racine du repo:

```bash
poetry run alembic -c database/alembic.ini upgrade head
poetry run alembic -c database/alembic.ini revision --autogenerate -m "description"
```

Alembic importe `database.models` dans `database/alembic/env.py`, donc les nouveaux modeles doivent etre exportes/importables depuis ce package pour etre pris en compte par l'autogeneration.

## Donnees et extractions

`database/data/` contient les sources historiques et scripts de collecte:

1. `cnc/`: fichier Excel CNC versionne et script d'extraction `extract_cnc_data_from_excel.py`.
2. `allocine/`: matcher, enricher, parser BeautifulSoup et CLI `allocine_runner.py`.
3. `mubi/`: classes de scraping MUBI et export `films_all_awards.csv`.
4. `machine_learning_predictions/`: CSV de predictions poster/trailer produits par la pipeline ML.
5. `old_db_init/`: anciens scripts SQL d'initialisation.
6. `sample/`: donnees de sample et seed minimal.
7. `scraping_browser.py`: session Playwright asynchrone connectee a un Chromium distant via `PLAYWRIGHT_WS_ENDPOINT`.

Voir aussi:

1. [database/data/README.md](data/README.md)
2. [database/data/allocine/README.md](data/allocine/README.md)
3. [database/data/mubi/README.md](data/mubi/README.md)

## Scripts de seed

Les scripts dans `database/seed/` alimentent les tables applicatives depuis les fichiers versionnes ou generes:

1. `seed_cnc_movies.py`: lit le fichier Excel CNC nettoye et cree les films, allocations budgetaires et certains credits diffuseurs.
2. `seed_allocine_movies_details.py`: lit `database/data/allocine/allocine_matches_enriched.csv`, met a jour les films et cree genres, trailers, posters et credits Allocine.
3. `seed_film_awards.py`: lit `database/data/mubi/films_all_awards.csv`, matche les films et cree festivals, prix et nominations.
4. `seed_poster_predictions.py`: lit `database/data/machine_learning_predictions/poster_predictions.csv` et recree les personnages d'affiches.
5. `seed_trailer_predictions.py`: lit `database/data/machine_learning_predictions/trailer_predictions.csv` et recree les personnages de trailers.

Exemples:

```bash
poetry run python -m database.seed.seed_cnc_movies
poetry run python -m database.seed.seed_allocine_movies_details
poetry run python -m database.seed.seed_film_awards
poetry run python -m database.seed.seed_poster_predictions
poetry run python -m database.seed.seed_trailer_predictions
```

Attention: certains seeders mettent a jour ou suppriment/recreent des donnees sur leur perimetre. Verifier la base cible via `DATABASE_URL` avant execution.

## Limites actuelles

1. La chaine d'alimentation reste manuelle et basee sur des CSV intermediaires.
2. Les scrapers Allocine/MUBI sont encore dans `database/data/`, meme si la cible documentee prevoit une integration future avec Airbyte ou une orchestration dediee.
3. Le backend lit encore les tables `ric_*` directement, pas des marts dbt curated.
4. Les notebooks ne sont pas testes automatiquement.
5. Les donnees versionnees incluent des exports intermediaires qui peuvent devenir obsoletes.
