# Scraping Allocine

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-08

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations           |
| --- | ---------- | ------------- | ---------------------- |
| 1   | 2026-05-07 | Joel Teixeira | Initial implementation |

Job de scraping standalone pour le sous-graphe cible `Scraping flow`.

Objectif: remplacer le handoff CSV historique dans `database/data/allocine/` par un flux brut stocké en base nommé `allocine_data`.

## Ce que fait la source

1. Lit actuellement les films candidats depuis `raw.id_matching`.
2. Crée automatiquement la table mémoire de sortie si elle n'existe pas encore.
3. Lit les lignes déjà réussies dans `raw.allocine_data` pour ignorer les enregistrements déjà traités.
4. Réutilise le parseur HTML Allociné historique et la session navigateur Playwright:
   - `database/data/allocine/allocine_scraper.py`
   - `database/data/scraping_browser.py`
5. Ecrit un enregistrement normalisé par film dans la table `allocine_data`.

## Contrat de sortie

Champs principaux:

1. identité source: `source_record_id`, `visa_number`, `original_name`, `cnc_agrement_year`
2. métadonnées Allociné: `allocine_id`, `allocine_title`, `allocine_url`, `allocine_visa_number`
3. charge utile enrichie: `release_date`, `duration_minutes`, `genres`, `trailer_url`, `direction`, `casting`, `screenwriters`, `production`, `technical_team`, `soundtrack`, `distribution`, `companies`
4. observabilité: `run_id`, `extracted_at`, `search_url`, `source_url`, `scrape_status`, `error_message`, `record_hash`

## Configuration

Exemple minimal:

```json
{
  "postgres_host": "${POSTGRES_HOST:-localhost}",
  "postgres_port": "${POSTGRES_PORT:-5432}",
  "postgres_db": "${POSTGRES_DB:-reveler_inegalites_cinema}",
  "postgres_user": "dbt_user",
  "postgres_password": "${DBT_USER_POSTGRES_PASSWORD:-secret}",
  "postgres_sslmode": "${POSTGRES_SSLMODE:-disable}",
  "input_schema": "raw",
  "input_table": "id_matching",
  "output_schema": "raw",
  "output_table": "allocine_data",
  "input_id_column": "VISA",
  "input_visa_column": "VISA",
  "input_title_column": "TITRE",
  "input_year_column": null,
  "input_allocine_id_column": "ID_ALLOCINE",
  "input_allocine_url_column": null,
  "scrape_limit": 10,
  "playwright_ws_endpoint": "${PLAYWRIGHT_WS_ENDPOINT:-ws://browserless:3000}"
}
```

Si `database_url` est fourni, il remplace les champs Postgres individuels.

Le fichier `config.json` du dossier est le fichier de configuration runtime utilise par les commandes locales et Docker. Il est versionne dans ce repo.

Les valeurs au format `${ENV_VAR:-default}` du `config.json` sont résolues depuis l'environnement du runtime.

Dans l'environnement Airbyte actuel, la table source par défaut est `raw.id_matching` et reprend les noms de colonnes bruts du sheet (`VISA`, `TITRE`, `ID_ALLOCINE`). Les champs absents comme l'année CNC ou l'URL Allociné peuvent être laissés à `null`.

La configuration applique actuellement `scrape_limit: 10`, ce qui borne les runs de debug et évite un scraping trop large par défaut. Ajuster cette valeur, la mettre à `null` ou la supprimer pour changer le volume traité.

Fichiers fournis dans le repo:

1. `config.json`: configuration runtime
2. `catalog.template.json`: squelette de catalogue compatible Airbyte, conservé pour compatibilité CLI
3. `build_local_image.sh`: build local de l'image Docker
4. `run_local_spec.sh`: test `spec`
5. `run_local_check.sh`: test `check`
6. `run_local_read.sh`: test `read`
7. `../../docker-compose.yml`: stack locale `prefect-server` + `prefect-worker` + `browserless`
8. `../../prefect/flows.py`: flow Prefect versionné pour l'orchestration

## Initialisation de la table de sortie

Au premier `sync` ou `read`, le job crée automatiquement la table configurée par `output_schema` + `output_table` si elle n'existe pas encore.

Exemple par défaut:

1. schéma: `raw`
2. table: `allocine_data`

Cette table sert de mémoire d'exécution pour la logique de skip incrémental.

Index créés au bootstrap:

1. `source_record_id`
2. `scrape_status`
3. `extracted_at`

## Commands

Depuis la racine du repo:

```bash
python3 ingestion/scraping/allocine/main.py spec
python3 ingestion/scraping/allocine/main.py check --config /tmp/allocine-config.json
python3 ingestion/scraping/allocine/main.py discover --config /tmp/allocine-config.json
python3 ingestion/scraping/allocine/main.py read --config /tmp/allocine-config.json --catalog /tmp/allocine-catalog.json
python3 ingestion/scraping/allocine/main.py sync --config /tmp/allocine-config.json
```

Via Docker:

```bash
bash ingestion/scraping/allocine/build_local_image.sh
bash ingestion/scraping/allocine/run_local_spec.sh
bash ingestion/scraping/allocine/run_local_check.sh reveler/source-allocine:dev ingestion/scraping/allocine/config.json
bash ingestion/scraping/allocine/run_local_read.sh reveler/source-allocine:dev ingestion/scraping/allocine/config.json ingestion/scraping/allocine/catalog.template.json
```

Via `docker compose exec` depuis `ingestion/`:

```bash
docker compose exec prefect-worker python3 /app/ingestion/scraping/allocine/main.py spec
docker compose exec prefect-worker python3 /app/ingestion/scraping/allocine/main.py check --config /app/ingestion/scraping/allocine/config.json
docker compose exec prefect-worker python3 /app/ingestion/scraping/allocine/main.py read --config /app/ingestion/scraping/allocine/config.json --catalog /app/ingestion/scraping/allocine/catalog.template.json
docker compose exec prefect-worker python3 /app/ingestion/scraping/allocine/main.py sync --config /app/ingestion/scraping/allocine/config.json
```

## Positionnement dans l'architecture

Dans la stratégie retenue:

1. Airbyte ne pilote pas ce job;
2. Airbyte reste réservé aux Google Sheets source vers `raw`;
3. Prefect orchestre `dbt phase 1` puis ce job de scraping depuis `prefect-worker`;
4. `read` et `catalog.template.json` sont conservés surtout pour compatibilité technique et tests locaux.

Séparation assumée:

1. la phase `dbt` avant scraping est finalisée côté Prefect;
2. la phase `dbt` après scraping existe déjà comme flow Prefect préparatoire, mais pas encore comme traitement réel;
3. un flow `airbyte sync` préparatoire existe aussi dans Prefect;
4. ce job couvre uniquement la partie scraping Allocine.

## Limites importantes

1. Le mode opératoire principal est `sync`, pas l'enregistrement dans une UI Airbyte.
2. Le bootstrap crée seulement la table mémoire de sortie. Il ne crée jamais la table d'entrée.
3. Si votre destination Airbyte n'expose que des tables `_airbyte_raw_*`, il faut ajouter une couche de compatibilité avant d'utiliser la logique de skip incrémental.
4. Les seeders historiques consomment encore des CSV aujourd'hui. Ce connecteur couvre seulement la partie scraping.
5. Le repo contient maintenant des modèles dbt de base pour ce flux: `stg_allocine_data` et `int_allocine_data_latest_by_source_record`.
6. le port hôte de `browserless/chrome` est piloté par `BROWSERLESS_PORT` dans `.env`;
7. le service `browserless/chrome` du compose local est une commodité de dev; il peut être remplacé par un endpoint Browserless/Chrome distant.
8. Le flow Prefect versionné est le point d'entrée recommandé pour ce scraping en environnement local ou serveur.
9. En cas de blocage anti-bot ou de rate limiting côté site, le scraper enregistre désormais `scrape_status = blocked` avec un message d'erreur explicite.

## Referenced by

- [database/data/allocine/README.md](../../../database/data/allocine/README.md)
