**Owner:** Data Team DataForGood

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author                | Observations                                 |
|------------|-----------------------|----------------------------------------------|
| 2026-05-07 | Data Team DataForGood | Ajout du bloc de metadonnees et normalisation |

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
* `docker` et `docker-compose` (voir [documentation d'installation](docs/repo-setup.md))

## Documentation

Points d'entrée principaux:

1. [frontend/README.md](frontend/README.md): application Next.js, commandes locales, structure frontend.
2. [backend/README.md](backend/README.md): API FastAPI, routes, variables d'environnement, acces base.
3. [database/README.md](database/README.md): modèles SQLAlchemy, migrations Alembic, seeds et données historiques.
4. [ingestion/README.md](ingestion/README.md): statut rapide du workspace Airbyte/dbt et commandes dbt courantes.
5. [ml-image/README.md](ml-image/README.md): code de machine learning pour l'analyse automatique des différentes images (frames) de bande-annonces, modèles utilisés, installation et execution.
6. [docs/repo-documentation-guidelines.md](docs/repo-documentation-guidelines.md): directives pour la documentation projet, structure recommandée, cycle de vie des documents.
7. [AGENTS.md](AGENTS.md): guide de travail du repository, bonnes pratiques et documents à lire en priorité.

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
