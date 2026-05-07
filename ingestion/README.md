**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author         | Observations                                |
|------------|----------------|---------------------------------------------|
| 2026-05-07 | Joel Teixeira  | Ajout du bloc de metadonnees et normalisation |

# Ingestion

Ce dossier regroupe les assets d'ingestion et de transformation de données, séparés du code applicatif principal.

Ce README sert de point d'entrée rapide: statut courant, structure et commandes usuelles. Pour le setup complet, les contrats cible ou la roadmap, voir les liens en fin de document.

## Etat actuel

Strategie retenue:

1. `Airbyte` synchronise uniquement les Google Sheets source vers `ab_raw`.
2. Pour `Modification data`, chaque onglet métier correspond à sa propre source Airbyte, sa propre connexion/sync et sa propre table brute cible.
3. `dbt` transforme les tables brutes et les sorties de scraping, puis publie les tables finales prévues par `schema1`.
4. `scraping/allocine/` exécute le scraping Allociné et écrit les données enrichies dans `ab_raw.allocine_data`.
5. `Prefect` orchestre les syncs Airbyte via API, puis les étapes `dbt` et `scraping allocine`.

Ce que cela implique:

1. le scraper Allociné n'est pas exécuté par Airbyte;
2. `Airbyte` reste cantonné aux sources standards, en particulier Google Sheets;
3. le Google Sheet `Modification data` n'est pas un flux unique: il faut un sync Airbyte distinct par onglet / table métier;
4. `dbt` ne scrape rien: il transforme seulement les tables d'entrée;
5. `Prefect` devient le point d'entrée opérationnel du flux complet, y compris pour déclencher les syncs Airbyte via API.

Modèles implémentés:

1. `stg_agreement_cnc`: normalisation et typage de `ab_raw.agreement_cnc`.
2. `stg_allocine_data`: normalisation de `ab_raw.allocine_data`.
3. `stg_raw_ric_films`: projection de la table historique existante des films.
4. `int_agreement_cnc_latest_by_visa`: derniere ligne Agreement CNC par `visa_number`.
5. `int_allocine_data_latest_by_source_record`: dernière version Allociné par enregistrement source.

Point important:

1. l'entrée canonique du scraping est `ab_raw.id_matching`;
2. la sortie canonique du scraping Allociné est `ab_raw.allocine_data`;
3. les tables finales `fnl_*` de `schema1` restent encore largement à construire.

## Roles

1. `airbyte/`: assets et conventions pour les syncs Google Sheets vers `ab_raw`.
2. `dbt/`: transformations SQL, staging, intermediate et futures tables finales `fnl_*`.
3. `scraping/allocine/`: job standalone de scraping/enrichissement Allociné.
4. `prefect/`: orchestration du pipeline d'ingestion.

## Scraping Allocine

Le job `scraping/allocine/`:

1. lit `ab_raw.id_matching`;
2. relit `ab_raw.allocine_data` pour éviter de retraiter ce qui est déjà terminé;
3. scrape seulement les IDs manquants;
4. écrit les résultats enrichis dans `ab_raw.allocine_data`;
5. est lancé directement ou via Prefect, pas via Airbyte.

## Demarrage

Depuis la racine du repository, entrer dans ce workspace avant de lancer les commandes de setup:

```bash
cd ingestion
```

## Structure

- `airbyte/`: configuration et assets lies aux syncs Google Sheets
- `dbt/`: projet dbt Core
- `scraping/`: jobs de scraping versionnes et dockerisables
- `prefect/`: flows et image d'orchestration
- `docker-compose.yml`: stack Docker locale pour `dbt`, `source_allocine`, `browserless` et `Prefect`

Dans `dbt/models/`:

1. `staging/`: normalisation des sources
2. `intermediate/`: consolidation de la dernière version par clé
3. `marts/`: futurs datasets publiés ou artefacts finaux du projet

## Runbook

Voir le [runbook de setup infra](../docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md) pour les etapes de configuration et le troubleshooting.

## Lancer les modèles

Depuis `ingestion/`:

```bash
set -a
source .env
set +a

dbt build --profile ric --project-dir dbt
```

Cette commande construit les modèles dbt versionnés du module.

## Usage Docker

Le module `ingestion/` est maintenant dockerisable côté repo.

Services fournis dans [docker-compose.yml](/root/explore/13_reveler_inegalites_cinema/ingestion/docker-compose.yml:1):

1. `dbt`: image dédiée `dbt-core` + `dbt-postgres`
2. `source_allocine`: image du job de scraping Allocine
3. `browserless`: navigateur distant optionnel pour le scraping
4. `prefect-*`: stack Prefect self-hosted pour l'orchestration locale

Exemples depuis `ingestion/`:

```bash
docker compose run --rm dbt debug --profile ric --project-dir /app/dbt
docker compose run --rm dbt build --profile ric --project-dir /app/dbt
docker compose --profile scraping run --rm source_allocine spec
docker compose --profile scraping run --rm source_allocine check --config /workspace/source_allocine/config.template.json
docker compose --profile scraping run --rm source_allocine sync --config /workspace/source_allocine/config.template.json
```

Note:

1. `Airbyte OSS` lui-même n'est pas embarqué dans ce compose.
2. Le service `browserless` est prévu pour le dev local; un endpoint externe `PLAYWRIGHT_WS_ENDPOINT` reste possible.

## Usage Prefect

La stack Prefect suit la documentation officielle Prefect self-hosted Docker Compose.

Services:

1. `prefect-postgres`
2. `prefect-redis`
3. `prefect-server`
4. `prefect-services`
5. `prefect-worker`

Exemples depuis `ingestion/`:

```bash
docker compose --profile orchestration up -d prefect-postgres prefect-redis prefect-server prefect-services prefect-worker
docker compose --profile orchestration logs -f prefect-server prefect-worker
docker compose --profile orchestration run --rm prefect-worker python3 /app/ingestion/prefect/flows.py
```

UI locale:

1. dashboard Prefect: `http://localhost:4200`
2. API Prefect: `http://localhost:4200/api`

Le flow versionné actuel est [flows.py](/root/explore/13_reveler_inegalites_cinema/ingestion/prefect/flows.py:1). Il exécute:

1. `dbt build`
2. `source_allocine sync`

## Résumé opératoire

1. Airbyte sync les Google Sheets vers `ab_raw`.
2. Pour `Modification data`, Airbyte exécute un sync séparé par onglet métier.
3. `ab_raw.id_matching` sert de table d'entrée canonique du scraping.
4. Prefect déclenche les syncs Airbyte via API.
5. Prefect lance `dbt`.
6. Prefect lance ensuite `source_allocine sync`.
7. dbt peut relire `ab_raw.allocine_data` via `stg_allocine_data` puis `int_allocine_data_latest_by_source_record`.

## Documentation détaillée

1. [Runbook infra](../docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md): installation et exploitation locale Airbyte/dbt/PostgreSQL.
2. [Specification Airbyte/dbt](../docs/specifications/ingestion-specification-airbyte-dbt-mises-a-jour-donnees.md): contrats cible et critères d'acceptation.
3. [Architecture ingestion](../docs/architecture/ingestion-architecture-airbyte-dbt-prefect-scraping.md): cible de référence, état actuel relatif et roadmap de convergence.

## Referenced by

- [README.md](../README.md)
