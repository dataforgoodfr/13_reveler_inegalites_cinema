**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author         | Observations                                |
|------------|----------------|---------------------------------------------|
| 2026-05-07 | Joel Teixeira  | Ajout du bloc de metadonnees et normalisation |

# Scraping Allocine

Job de scraping standalone pour le sous-graphe cible `Scraping flow`.

Objectif: remplacer le handoff CSV historique dans `database/data/allocine/` par un flux brut stocké en base nommé `allocine_data`.

## Ce que fait la source

1. Lit par défaut les films candidats depuis `ab_raw.id_matching`.
2. Crée automatiquement la table mémoire de sortie si elle n'existe pas encore.
3. Lit les lignes déjà réussies dans `ab_raw.allocine_data` pour ignorer les enregistrements déjà traités.
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
  "postgres_host": "localhost",
  "postgres_port": 5432,
  "postgres_db": "reveler_inegalites_cinema",
  "postgres_user": "pipeline_user",
  "postgres_password": "secret",
  "postgres_sslmode": "disable",
  "input_schema": "ab_raw",
  "input_table": "id_matching",
  "output_schema": "ab_raw",
  "output_table": "allocine_data",
  "input_id_column": "film_id",
  "input_visa_column": "visa_number",
  "input_title_column": "original_name",
  "input_year_column": "cnc_agrement_year",
  "playwright_ws_endpoint": "ws://browserless:3000?token=..."
}
```

Si `database_url` est fourni, il remplace les champs Postgres individuels.

Fichiers fournis dans le repo:

1. `config.template.json`: squelette de configuration source
2. `catalog.template.json`: squelette de catalogue compatible Airbyte, conservé pour compatibilité CLI
3. `build_local_image.sh`: build local de l'image Docker
4. `run_local_spec.sh`: test `spec`
5. `run_local_check.sh`: test `check`
6. `run_local_read.sh`: test `read`
7. `../../docker-compose.yml`: stack locale `source_allocine` + `browserless` + `dbt`
8. `../../prefect/flows.py`: flow Prefect versionné pour l'orchestration

## Initialisation de la table de sortie

Au premier `sync` ou `read`, le job crée automatiquement la table configurée par `output_schema` + `output_table` si elle n'existe pas encore.

Exemple par défaut:

1. schéma: `ab_raw`
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
bash ingestion/scraping/allocine/run_local_check.sh reveler/source-allocine:dev ingestion/scraping/allocine/config.template.json
bash ingestion/scraping/allocine/run_local_read.sh reveler/source-allocine:dev ingestion/scraping/allocine/config.template.json ingestion/scraping/allocine/catalog.template.json
```

Via `docker compose` depuis `ingestion/`:

```bash
docker compose --profile scraping build source_allocine
docker compose --profile scraping run --rm source_allocine spec
docker compose --profile scraping run --rm source_allocine check --config /workspace/source_allocine/config.template.json
docker compose --profile scraping run --rm source_allocine read --config /workspace/source_allocine/config.template.json --catalog /workspace/source_allocine/catalog.template.json
docker compose --profile scraping run --rm source_allocine sync --config /workspace/source_allocine/config.template.json
```

## Positionnement dans l'architecture

Dans la stratégie retenue:

1. Airbyte ne pilote pas ce job;
2. Airbyte reste réservé aux Google Sheets source vers `ab_raw`;
3. Prefect orchestre `dbt` puis `source_allocine sync`;
4. `read` et `catalog.template.json` sont conservés surtout pour compatibilité technique et tests locaux.

## Limites importantes

1. Le mode opératoire principal est `sync`, pas l'enregistrement dans une UI Airbyte.
2. Le bootstrap crée seulement la table mémoire de sortie. Il ne crée jamais la table d'entrée.
3. Si votre destination Airbyte n'expose que des tables `_airbyte_raw_*`, il faut ajouter une couche de compatibilité avant d'utiliser la logique de skip incrémental.
4. Les seeders historiques consomment encore des CSV aujourd'hui. Ce connecteur couvre seulement la partie scraping.
5. Le repo contient maintenant des modèles dbt de base pour ce flux: `stg_allocine_data` et `int_allocine_data_latest_by_source_record`.
6. Le service `browserless/chrome` du compose local est une commodité de dev; il peut être remplacé par un endpoint Browserless/Chrome distant.
7. Le flow Prefect versionné est le point d'entrée recommandé pour ce scraping en environnement local ou serveur.

## Referenced by

- [database/data/allocine/README.md](../../../database/data/allocine/README.md)
