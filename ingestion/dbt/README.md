# dbt

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-08

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations           |
| --- | ---------- | ------------- | ---------------------- |
| 1   | 2026-05-07 | Joel Teixeira | Initial implementation |

Ce dossier contient le projet dbt du module ingestion.

Objectif:

1. transformer les tables brutes du schéma `raw`;
2. séparer les traitements avant scraping et après scraping via les tags `phase1` et `phase2`;
3. préparer progressivement la future couche publiée `fnl`.

## Structure

1. `dbt_project.yml`: configuration du projet, matérialisations et schémas cibles.
2. `models/staging/`: vues de normalisation des sources brutes.
3. `models/intermediate/`: vues de consolidation et de latest par clé métier.
4. `models/fnl/`: couche finale cible, encore vide à ce stade.
5. `profiles/`: profil dbt versionné utilisé par `prefect-worker`.
6. `macros/`: macros partagées, notamment pour la gestion des schémas.
7. `seeds/`: jeux de données statiques éventuels.
8. `tests/`: tests dbt spécifiques au projet.

## Schémas et matérialisations

Configuration actuelle du projet:

1. `staging` est matérialisé en `view` dans le schéma `staging`.
2. `intermediate` est matérialisé en `view` dans le schéma `intermediate`.
3. `fnl` est matérialisé en `table` dans le schéma `fnl`.

## Sources brutes déclarées

Sources versionnées dans `models/sources.yml`:

1. `raw.agreement_cnc`: chargement Airbyte du Google Sheet `AGREEMENT CNC`.
2. `raw.allocine_data`: sortie brute du scraping Allociné.

## Modèles préparés

### Phase 1

1. `stg_agreement_cnc`
   Description: normalise et type les colonnes de `raw.agreement_cnc`.
   Tags: `phase1`.
   Tests déclarés: `visa_number` non nul.

2. `int_agreement_cnc_latest_by_visa`
   Description: conserve la dernière version de chaque film par `visa_number` à partir des métadonnées d'extraction.
   Tags: `phase1`.
   Tests déclarés: `visa_number` non nul et unique.

### Phase 2

1. `stg_allocine_data`
   Description: normalise les données brutes écrites par le scraping Allociné dans `raw.allocine_data`.
   Tags: `phase2`.
   Tests déclarés: `source_record_id` non nul, `extracted_at` non nul.

2. `int_allocine_data_latest_by_source_record`
   Description: conserve la dernière version de chaque enregistrement scrapé par `source_record_id`.
   Tags: `phase2`.
   Tests déclarés: `source_record_id` non nul et unique.

## Découpage d'exécution

1. `dbt build --select tag:phase1` prépare les données nécessaires avant scraping.
2. `dbt build --select tag:phase2` consolide les résultats après scraping.
3. aucun modèle `fnl` n'est encore prêt dans le repo; cette couche reste à construire.

## Exécution locale

Depuis `ingestion/`:

```bash
docker compose exec prefect-worker dbt debug --profile ric --project-dir /app/ingestion/dbt
docker compose exec prefect-worker dbt build --select tag:phase1 --profile ric --project-dir /app/ingestion/dbt
docker compose exec prefect-worker dbt build --select tag:phase2 --profile ric --project-dir /app/ingestion/dbt
```

Le runtime nominal est `prefect-worker`, avec le profil versionné `profiles/profiles.yml`.

## Points d'attention

1. `phase1` ne doit pas dépendre des résultats du scraping Allociné.
2. `phase2` suppose que `raw.allocine_data` a déjà été alimentée.
3. le profil dbt utilise actuellement `dbt_user` en dur et lit son mot de passe depuis `DBT_USER_POSTGRES_PASSWORD`.
4. le schéma `fnl` existe dans la configuration, mais aucun modèle final n'y est encore matérialisé.

## Referenced by

- [ingestion/README.md](../README.md)
