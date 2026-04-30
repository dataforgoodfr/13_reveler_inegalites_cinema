# Ingestion

Ce dossier regroupe les assets d'ingestion et de transformation de donnees, separes du code applicatif principal.

Ce README sert de point d'entree rapide: statut courant, structure et commandes usuelles. Pour le setup complet, les contrats cible ou la roadmap, voir les liens en fin de document.

## Etat actuel

Le flux dbt des agrements CNC est partiellement structure, mais le mart final n'est pas encore implemente. Hypotheses actuelles:

1. L'ingestion Airbyte depuis Google Sheets est deja configuree.
2. Le Google Sheet `AGREEMENT CNC` arrive dans `ab_raw.agreement_cnc`.
3. Le jeu de donnees historique applicatif des films est disponible dans `raw.ric_films`.

Modeles implementes:

1. `stg_agreement_cnc`: normalisation et typage de `ab_raw.agreement_cnc`.
2. `stg_raw_ric_films`: projection de la table historique existante des films.
3. `int_agreement_cnc_latest_by_visa`: derniere ligne Agreement CNC par `visa_number`.
4. `mart_cnc_films_for_scraping`: modele placeholder uniquement. Il lit actuellement `stg_raw_ric_films` et utilise une logique temporaire pour `should_scrape_allocine`; il ne fusionne pas encore les lignes CNC Airbyte avec les films historiques.

Comportement cible encore a implementer dans le mart final:

1. `is_new_film`
2. `has_cnc_payload_change`
3. `should_scrape_allocine`

## Demarrage

Depuis la racine du repository, entrer dans ce workspace avant de lancer les commandes de setup:

```bash
cd ingestion
```

## Structure

- `airbyte/`: configuration et assets lies a Airbyte
- `dbt/`: projet dbt Core

Dans `dbt/models/`:

1. `staging/`: normalisation des sources
2. `intermediate/`: consolidation de la derniere version par cle
3. `marts/`: datasets publies cibles pour l'orchestration et le scraping; le mart CNC est actuellement partiel

## Runbook

Voir le [runbook de setup infra](../docs/runbooks/infra-setup-dbt-core-airbyte-remote-postgres.md) pour les etapes de configuration et le troubleshooting.

## Lancer les modeles

Depuis `ingestion/`:

```bash
set -a
source .env
set +a

dbt build --profile ric --project-dir dbt --select +mart_cnc_films_for_scraping
```

Cette commande construit les modeles staging, intermediate et le mart placeholder actuel. Ne pas considerer `mart_cnc_films_for_scraping` comme pret pour la production tant que la logique de fusion n'est pas terminee.

## Documentation detaillee

1. [Runbook infra](../docs/runbooks/infra-setup-dbt-core-airbyte-remote-postgres.md): installation et exploitation locale Airbyte/dbt/PostgreSQL.
2. [Specification Airbyte/dbt](../docs/specifications/specification-airbyte-dbt-mises-a-jour-donnees.md): contrats cible et criteres d'acceptation.
3. [Plan d'automatisation](../docs/architecture/plan-automatisation-pipeline-ingestion.md): etat actuel, ecarts et roadmap de migration.
