# Debug local dbt (sans container)

## Metadata du document

**Responsable:** Joel Teixeira

**Derniere revision:** 2026-05-22

**Statut:** actif

### Historique du document

| #   | Date       | Auteur         | Observations                                                          |
| --- | ---------- | -------------- | --------------------------------------------------------------------- |
| 1   | 2026-05-22 | Joel Teixeira | Guide dev pour lancer `dbt test` hors container                      |

## Objectif

Executer `dbt test` en local, sans container, sur Windows via WSL2.

## Prerequis

1. WSL2 actif (Ubuntu/Debian).
2. Python 3.10+ dans WSL2.
3. Fichier `ingestion/.env` present avec les variables dbt.

## Quick start WSL2

```bash
cd ingestion/dbt
python3 -m venv .venv-dbt
source .venv-dbt/bin/activate
python -m pip install --upgrade pip
pip install "dbt-core>=1.8,<2" "dbt-postgres>=1.8,<2"

# charge les variables depuis ingestion/.env
set -a
source ../.env
set +a

dbt --version
dbt debug --profile ric --project-dir . --profiles-dir profiles
dbt test --profile ric --project-dir . --profiles-dir profiles
```

## Si ca bloque

```bash
# corrige les fins de ligne Windows si besoin
sed -i 's/\r$//' ../.env

# si la base tourne cote Windows, verifier POSTGRES_HOST
# localhost peut ne pas marcher depuis WSL2
```


## TIP
N'hésite pas a utiliser copilot pour depanner si ça bloque encore