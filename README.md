# Data For Good #13 - Révéler les Inégalités dans le Cinéma (RIC)

L'objectif de ce projet est de créer une application web qui informera le grand public et les institutions sur les inégalités de genre et raciales dans le cinéma français.

Techniquement, l'application sera composée de :
* une application front-end Next.js accessible à tous pour afficher des graphiques sur les inégalités de genre et raciales  
* un backend FastAPI en Python qui fournira une API permettant au frontend d'accéder aux données à afficher dans les graphiques  
* une base de données PostgreSQL pour stocker les données pertinentes  
  * Pour interagir avec la base de données avec python, nous utiliserons un ORM (Object-relational mapping) - sqlalchemy
  * Pour suivre l'évolution de la base de données, nous utiliserons un outil de migration de donnée - alembic
* plusieurs scripts Python :
  * Pour scraper des données à partir de différentes sources externes et les ajouter à la base de données  
  * Pour exécuter des scripts de machine learning sur des sources médiatiques afin de générer des KPI supplémentaires pertinents sur les films


# Stack technique
* Frontend: Next.js
* Backend: FastAPI
* Database: PostgreSQL
* ORM: [SQLAlchemy](https://www.sqlalchemy.org/) (psycopg as adapter)
* Outil de migration de db: [Alembic](https://github.com/sqlalchemy/alembic)

## Prérequis
* `git`
* `docker` et `docker-compose` (voir [documentation d'installation](docs/setup.md))

## Documentation

Points d'entree principaux:

1. [frontend/README.md](frontend/README.md): application Next.js, commandes locales, structure frontend.
2. [backend/README.md](backend/README.md): API FastAPI, routes, variables d'environnement, acces base.
3. [database/README.md](database/README.md): modeles SQLAlchemy, migrations Alembic, seeds et donnees historiques.
4. [ingestion/README.md](ingestion/README.md): statut rapide du workspace Airbyte/dbt et commandes dbt courantes.
5. [docs/runbooks/infra-setup-dbt-core-airbyte-remote-postgres.md](docs/runbooks/infra-setup-dbt-core-airbyte-remote-postgres.md): setup operationnel Airbyte OSS, dbt Core et PostgreSQL.
6. [docs/specifications/specification-airbyte-dbt-mises-a-jour-donnees.md](docs/specifications/specification-airbyte-dbt-mises-a-jour-donnees.md): contrats cible Google Sheets, Airbyte, dbt et criteres d'acceptation.
7. [docs/architecture/plan-automatisation-pipeline-ingestion.md](docs/architecture/plan-automatisation-pipeline-ingestion.md): etat actuel, ecarts et roadmap de migration vers une ingestion automatisee.


# Contribution

## Utiliser un venv python

    python3 -m venv .venv

    source .venv/bin/activate

## Utiliser Poetry

Installer les dépendances:

    poetry install

Ajouter une dépendance:

    poetry add pandas

Mettre à jour les dépendances:

    poetry update

## Lancer les precommit-hook localement

[Installer les precommit](https://pre-commit.com/)

    pre-commit run --all-files

## Utiliser Tox pour tester votre code

    tox -vv
