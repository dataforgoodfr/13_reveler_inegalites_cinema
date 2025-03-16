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
* Database: postegresql
* ORM: [SQLAlchemy](https://www.sqlalchemy.org/) (psycopg as adapter)
* Outil de migration de db: [Alembic](https://github.com/sqlalchemy/alembic)

## Prérequis
* `git`
* `docker` et `docker-compose` (voir [documentation d'installation](docs/setup.md))


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
