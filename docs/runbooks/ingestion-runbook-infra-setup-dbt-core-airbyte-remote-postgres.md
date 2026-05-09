# Setup infra reproductible - Airbyte OSS + dbt Core + Prefect avec Postgres distant

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-09

**Statut:** actif

### Historique du document

| #   | Date       | Auteur         | Observations                                            |
| --- | ---------- | -------------- | ------------------------------------------------------- |
| 1   | 2026-05-07 | Joel Teixeira  | Initial implementation                                  |

## 1. Objectif

Ce runbook décrit un parcours simple pour installer et exécuter la pipeline d'ingestion locale avec:

1. Airbyte OSS (`abctl`)
2. dbt Core (dans `prefect-worker`)
3. Prefect (UI + orchestration)
4. PostgreSQL distant (app + DB Prefect dédiée)

Objectif: avoir un setup reproductible, rapide à démarrer et facile à vérifier.

## 2. Topologie standard

Topologie cible en local:

1. Airbyte tourne localement via `abctl`.
2. `ingestion/docker-compose.yml` démarre:
   - `prefect-server`
   - `prefect-worker`
   - `browserless`
3. `prefect-worker` exécute:
   - `dbt` (phase 1, puis phase 2 optionnelle)
   - scraping Allociné via `ingestion/scraping/allocine/main.py`
4. PostgreSQL distant héberge:
   - la base applicative (`raw`, `staging`, `intermediate`, `fnl`)
   - la base dédiée `prefect`

Conventions utilisateurs:

1. `airbyte_user` pour la zone `raw`
2. `dbt_user` pour le runtime dbt + scraping
3. `prefect_user` pour la base `prefect`

## 3. Répertoire de travail

Depuis la racine du repo:

```bash
cd ingestion
```

Sauf mention contraire, toutes les commandes de ce runbook sont lancées depuis `ingestion/`.

## 4. Installation

### 4.1 Prérequis et vérification

Prérequis minimaux:

1. Docker + Docker Compose plugin
2. `curl`
3. `python3`
4. accès au serveur Postgres cible

Check rapide:

```bash
docker compose version
```

### 4.2 Contrat de variables d'environnement

Créer le fichier local:

```bash
cp .env.example .env
```

Variables indispensables à renseigner:

1. `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_SSLMODE`
2. `DBT_USER_POSTGRES_PASSWORD`
3. `PREFECT_API_DATABASE_CONNECTION_URL`
4. `AIRBYTE_HOST`, `AIRBYTE_PORT`, `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`
5. `AIRBYTE_DESTINATION_POSTGRES_PASSWORD`
6. `PREFECT_PORT` et `BROWSERLESS_PORT` si vous voulez des ports hôtes non défaut

Charger les variables dans le shell (optionnel):

```bash
set -a
source .env
set +a
```

### 4.3 Préparation utilisateurs et privilèges Postgres

À exécuter une fois par environnement (compte DBA):

```sql
CREATE USER airbyte_user WITH PASSWORD '<replace>';
CREATE USER dbt_user WITH PASSWORD '<replace>';

GRANT CONNECT ON DATABASE reveler_inegalites_cinema TO airbyte_user;
GRANT CREATE, TEMPORARY ON DATABASE reveler_inegalites_cinema TO airbyte_user;
GRANT CONNECT ON DATABASE reveler_inegalites_cinema TO dbt_user;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS fnl;

ALTER SCHEMA raw OWNER TO airbyte_user;
ALTER SCHEMA staging OWNER TO dbt_user;
ALTER SCHEMA intermediate OWNER TO dbt_user;
ALTER SCHEMA fnl OWNER TO dbt_user;

GRANT USAGE, CREATE ON SCHEMA raw TO airbyte_user;
GRANT USAGE, CREATE ON SCHEMA raw TO dbt_user;
GRANT USAGE, CREATE ON SCHEMA staging TO dbt_user;
GRANT USAGE, CREATE ON SCHEMA intermediate TO dbt_user;
GRANT USAGE, CREATE ON SCHEMA fnl TO dbt_user;
```

Base Prefect dédiée:

```sql
CREATE USER prefect_user WITH PASSWORD '<replace>';
CREATE DATABASE prefect OWNER prefect_user;
GRANT CONNECT ON DATABASE prefect TO prefect_user;
```

Exemple `.env`:

```bash
PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://prefect_user:<replace>@<db-host>:<db-port>/prefect
```

### 4.4 Setup, configuration et bootstrap Airbyte

Installer `abctl`:

```bash
curl -LsfS https://get.airbyte.com | bash
abctl version
```

Installer Airbyte local:

```bash
abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT"
abctl local status
abctl local credentials
```

Préparer le bootstrap versionné:

1. déposer un unique fichier JSON de service account dans `ingestion/airbyte/json_credentials/`
2. renseigner les `spreadsheet_id` dans `ingestion/airbyte/sources/*.json`
3. vérifier les variables Airbyte/Postgres dans `.env`

Appliquer le bootstrap:

```bash
python3 airbyte/bootstrap.py apply --dry-run
python3 airbyte/bootstrap.py apply
```

### 4.5 Déploiement Docker Compose (dbt, scraping, Prefect)

Démarrer la stack ingestion:

```bash
docker compose up -d
docker compose logs -f prefect-server prefect-worker browserless
```

Comportement attendu:

1. `prefect-server` sert l'UI/API sur `http://localhost:$PREFECT_PORT`
2. `prefect-worker` crée le work pool `ingestion-pool`
3. `prefect-worker` publie le deployment du flow principal
4. `browserless` est utilisé par le scraping Allociné

## 5. Vérifications

Checklist courte:

1. `abctl local status` est OK
2. `docker compose config --quiet` passe
3. `docker compose logs -f prefect-server prefect-worker browserless` ne montre pas d'erreur bloquante
4. l'UI Prefect est accessible: `http://localhost:$PREFECT_PORT`
5. après bootstrap Airbyte, source + destination + connexion sont visibles dans Airbyte
6. `docker compose exec prefect-worker dbt debug --profile ric --project-dir /app/ingestion/dbt` passe

Contrôle SQL minimal après sync Airbyte:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'raw'
ORDER BY table_name;
```

## 6. Utilisation

### Lancer la pipeline depuis l'UI Prefect

Préparer:

1. Airbyte local actif
2. stack Docker ingestion démarrée
3. bootstrap Airbyte appliqué

Parcours UI:

1. ouvrir `http://localhost:$PREFECT_PORT`
2. aller dans Deployments
3. ouvrir le deployment `lancer-ingestion-donnees`
4. cliquer sur `Run`
5. suivre le run du flow `Lancer l'ingestion complete`

Les sous-flows visibles pendant l'exécution:

1. `Synchroniser les sources` (optionnel)
2. `Preparer les donnees`
3. `Recuperer les donnees Allocine`
4. `Finaliser les donnees` (optionnel)

Option CLI (debug):

```bash
docker compose exec prefect-worker python3 /app/ingestion/prefect/flows.py main-ingestion
```

Avec sync Airbyte explicite:

```bash
docker compose exec prefect-worker python3 /app/ingestion/prefect/flows.py main-ingestion \
  --run-airbyte-sync \
  --airbyte-connection-name "src_gsheet_agreement_cnc -> dst_pg_raw"
```

## 7. FAQ

### 7.1 Je change d'environnement (test/prod), que modifier ?

Mettre à jour dans `.env`:

1. `POSTGRES_*`
2. `DBT_USER_POSTGRES_PASSWORD`
3. `AIRBYTE_DESTINATION_POSTGRES_PASSWORD`
4. `PREFECT_API_DATABASE_CONNECTION_URL`

Puis relancer:

```bash
python3 airbyte/bootstrap.py apply
docker compose up -d
```

### 7.2 Airbyte ne démarre pas (port déjà pris)

Choisir un autre port dans `.env` (ex: `AIRBYTE_PORT=8001`) puis relancer `abctl local install`.

### 7.3 Prefect ne se connecte pas à sa base

Vérifier:

1. `PREFECT_API_DATABASE_CONNECTION_URL`
2. existence de la base `prefect`
3. droits de `prefect_user`

## 8. Références

1. démarrage rapide Airbyte OSS: [https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart](https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart)
2. Airbyte `abctl`: [https://docs.airbyte.com/platform/deploying-airbyte/abctl](https://docs.airbyte.com/platform/deploying-airbyte/abctl)
3. destination Postgres Airbyte: [https://docs.airbyte.com/integrations/destinations/postgres](https://docs.airbyte.com/integrations/destinations/postgres)
4. installation dbt Core: [https://docs.getdbt.com/docs/local/install-dbt](https://docs.getdbt.com/docs/local/install-dbt)
5. profils dbt: [https://docs.getdbt.com/docs/local/profiles.yml](https://docs.getdbt.com/docs/local/profiles.yml)
6. setup Postgres dbt: [https://docs.getdbt.com/docs/local/connect-data-platform/postgres-setup](https://docs.getdbt.com/docs/local/connect-data-platform/postgres-setup)
7. serveur Prefect auto-hébergé: [https://docs.prefect.io/](https://docs.prefect.io/)

## 9. Referenced by

- [README.md](../../README.md)
- [ingestion/README.md](../../ingestion/README.md)
