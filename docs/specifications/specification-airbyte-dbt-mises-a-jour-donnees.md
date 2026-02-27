Last reviewed: 2026-02-27
Status: draft

# Spécification technique - Airbyte + dbt pour mises à jour CNC et corrections métier

## 1. Contexte et objectifs

Mettre en place un pipeline pérenne pour:

1. intégrer les nouveaux jeux de données CNC annuels via Google Sheets;
2. appliquer des corrections ciblées métier sur plusieurs entités (ex: `CreditHolder`);
3. préserver l'historique brut;
4. exposer une couche "curated" unique pour Metabase + backend + frontend.

## 2. Périmètre (V1)

Inclus:

1. Source Google Sheets `AGREEMENT CNC` (onglets annuels).
2. Source Google Sheets `Modification data` (1 onglet par entité).
3. Ingestion Airbyte vers PostgreSQL raw.
4. Transformation dbt en couches `raw -> staging -> marts`.
5. Exposition de tables/vues finales et intégration backend SQLAlchemy.
6. Encapsulation des scripts de scraping existants dans des connecteurs Airbyte custom.


## 3. Architecture cible

## 3.1 Flux global

1. Bob alimente Google Sheets.
2. Airbyte synchronise vers schéma raw (`ab_raw` ou équivalent).
3. dbt construit:
   - `stg_*`: normalisation des types et colonnes,
   - `int_*`: consolidation intermédiaire (latest, dedup, validation),
   - `mart_*`: tables/vues publiées.
4. API FastAPI + Metabase lisent `mart_*` uniquement.

## 3.2 Couches de données

1. `raw`:
   - append-only, issu d'Airbyte;
   - conservation complète pour audit.
2. `staging`:
   - cast des types;
   - renommage canonique;
   - normalisation des valeurs.
3. `marts/curated`:
   - application des corrections;
   - logique de priorité métier;
   - consommation BI/API.

## 4. Contrats de données

## 4.1 Google Sheet `AGREEMENT CNC`

Règles:

1. 1 onglet par année (`2024`, `2025`, `2026`, etc.).
2. `visa_number` obligatoire et non nul.
3. Les colonnes du contrat doivent rester stables.

Colonnes minimales V1 [TODO: A COMPLETER]:

1. `visa_number` (string)
2. `original_name` (string)
3. `cnc_agrement_year` (integer)
4. autres colonnes CNC utiles au reporting (selon dictionnaire validé)

Clé fonctionnelle:

1. `visa_number` (join avec `ric_films.visa_number`).

## 4.2 Google Sheet `Modification data`

Organisation:

1. 1 onglet par entité (`CreditHolder`, `Film`, etc.).
2. Schéma commun par onglet.

Colonnes V1:

1. `id` (obligatoire)
2. `column_name` (obligatoire)
3. `new_value` (obligatoire)
4. `modification_date` (obligatoire, ISO `YYYY-MM-DD`)
5. `requested_by` (obligatoire)
6. `reason` (optionnel)

Note sur `status`:

1. non requis en V1 pour garder un process simple;
2. règle de résolution: "dernière modification valide gagne" (sur `modification_date`);
3. possibilité d'ajouter `status` en V2 si workflow d'approbation formel.

## 5. Logique métier de transformation (dbt)

## 5.1 User Story A - Titres CNC corrigés

1. `stg_agreement_cnc_all_years`:
   - union de tous les onglets annuels;
   - ajout de `sheet_year`, `ingested_at`.
2. `int_agreement_cnc_latest_by_visa`:
   - déduplication par `visa_number` (dernière version).
3. `mart_films_curated`:
   - left join `ric_films` + `int_agreement_cnc_latest_by_visa`;
   - `original_name_curated = coalesce(cnc.original_name, films.original_name)`;
   - conservation des deux colonnes:
     - valeur source (`original_name_source`)
     - valeur corrigée (`original_name_curated`).
     [TODO: ça peut etre sympa de presenter les deux valeurs cote a cote dans Metabase pour faciliter la validation métier et la traçabilité des corrections, ou meme dans le front si le collectif trouve pertinent @NicolasRevel]

## 5.2 User Story B - Corrections multi-entités

1. `stg_modifications_all_entities`:
   - union de tous les onglets, ajout `entity = nom_onglet`.
2. `int_modifications_validated`:
   - filtre des colonnes autorisées (whitelist);
   - cast par type cible;
   - rejet des lignes invalides vers table d'erreurs.
3. `int_modifications_latest`:
   - dernière correction par (`entity`, `id`, `column_name`).
4. application dans marts par entité:
   - `mart_credit_holders_curated`
   - `mart_films_curated`
   - etc.

Pattern SQL recommandé:

1. pivot des corrections par entité;
2. `coalesce(correction_casted, valeur_source)` pour chaque colonne autorisée.

## 5.3 Expertise métier et règles de champ (exemples)

`CreditHolder`:

1. `gender`: valeurs acceptées `male`, `female`, `unknown`.
2. `birthdate`: date valide, non future.

`Film`:

1. `original_name`: non vide après trim.
2. `release_date`: date valide, plage réaliste.

Règle générale:

1. seules les colonnes explicitement autorisées par entité peuvent être corrigées;
2. toute autre ligne est rejetée et tracée.

TODO: valider ces règles avec les équipes métier et ajuster selon les besoins spécifiques de chaque entité.

## 6. Tests dbt à implémenter

## 6.1 Tests sources / ingestion

1. fraîcheur des sources (`source freshness`) par flux critique;
2. non-null sur colonnes clés (`visa_number`, `id`, `column_name`, `new_value`, `modification_date`, `requested_by`);
3. volumétrie anormale (alerting sur chute/pic). ????

## 6.2 Tests de qualité staging

1. types conformes après cast;
2. format date ISO pour `modification_date`;
3. trimming des chaînes et normalisation de casse.

## 6.3 Tests d'intégrité métier

1. `visa_number` de corrections CNC trouvable dans `ric_films` (ou flag exception);
2. (`entity`, `column_name`) présent dans whitelist;
3. (`entity`, `id`) existant dans la table de référence;
4. unicité de la version active dans `int_modifications_latest`.

## 6.4 Tests sur marts / exposition

1. unicité des clés métier (`film_id`, `credit_holder_id`, etc.);
2. non-null des colonnes obligatoires publiées;
3. test de non-régression du nombre de lignes vs source métier;
4. test de cohérence "source vs curated" (delta explicable).

## 7. Gestion des erreurs et observabilité (Optionnel V1, mais sympa pour alerter en cas de problèmes)

1. Table `mart_data_corrections_rejected` avec motif de rejet:
   - colonne non autorisée,
   - id introuvable,
   - type invalide,
   - format invalide.
2. Dashboard qualité:
   - volume de corrections ingérées,
   - volume de rejets,
   - top motifs de rejet.
3. Alerting:
   - échec sync Airbyte,
   - échec dbt run/test,
   - dépassement seuil de rejets.

## 8. Impacts backend (FastAPI + SQLAlchemy)

Créer/mettre à jour les modèles SQLAlchemy nécessaires pour consommer la couche curated:

1. modèles pour tables/vues `mart_*` exposées (au minimum films et credit holders);
2. repositories lisant `mart_*` au lieu des tables source quand pertinent;
3. adaptation des use cases (`GetFilmDetails`, `SearchFilms`, etc.) pour privilégier les champs curated;
4. maintenir la rétrocompatibilité API (même contrat de réponse).

## 9. Airbyte custom connectors pour scraping (OPTIONNEL V1)

Objectif: intégrer les scripts existants (Allociné, MUBI, autres) dans Airbyte.

Approche:

1. encapsuler chaque scraper dans un connecteur source custom (Python CDK Airbyte);
2. émettre des enregistrements normalisés avec métadonnées d'extraction:
   - `extracted_at`,
   - `source_url`,
   - `run_id`,
   - `record_hash` (optionnel).
3. synchroniser vers raw, puis transformer via dbt comme les autres flux.

## 10. Sécurité, accès, et gouvernance

1. accès édition Google Sheets limité aux rôles métier autorisés;
2. droits lecture élargis si besoin;
3. compte de service dédié pour Airbyte;
4. historisation native Google Sheets conservée;
5. dictionnaire de données versionné dans le repo.

## 11. Plan d'implémentation (checklist)

## 11.1 Phase 1 - Cadrage

1. valider les schémas finaux des deux Google Sheets;
2. valider la whitelist de colonnes corrigeables par entité;
3. valider la fréquence de sync (ex: horaire).

## 11.2 Phase 2 - Ingestion

1. créer connexions Airbyte Google Sheets -> Postgres raw;
2. configurer synchro incrémentale/append quand possible;
3. tester la reprise après incident.

## 11.3 Phase 3 - dbt

1. créer modèles `stg`, `int`, `mart`;
2. ajouter tous les tests listés section 6;
3. publier documentation dbt (lineage + descriptions).

## 11.4 Phase 4 - Backend / Exposition

1. ajouter modèles SQLAlchemy `mart_*`;
2. adapter repositories/use cases;
3. valider via tests API + tests de non-régression.

## 11.5 Phase 5 - BI / Front

1. basculer Metabase sur `mart_*`;
2. valider affichage frontend via API;
3. recette métier avec jeux d'essai.

## 11.6 Phase 6 - Run

1. mettre en place monitoring et alerting;
2. documenter runbook opérationnel;
3. former les utilisateurs métier (guide de saisie).

## 12. Critères d'acceptation

1. un nouvel onglet CNC annuel se propage en production sans intervention SQL manuelle;
2. une correction métier valide dans `Modification data` est visible en sortie au prochain cycle;
3. aucune donnée brute n'est perdue;
4. les rejets sont visibles et actionnables; (OPTIONNEL V1)
5. Metabase + frontend utilisent la même couche curated.

