Last reviewed: 2026-02-27
Status: draft

# Processus proposé de mise à jour des données (version validation métier)

## 1. Pourquoi ce changement

Aujourd'hui, les corrections de données (ex: nouveaux titres CNC, correction d'un genre ou d'une date de naissance) peuvent nécessiter des manipulations techniques et manuelles.

Objectif: permettre aux équipes non techniques de proposer des mises à jour de manière simple, traçable, et répétable chaque année, sans perdre l'historique des données brutes.

## 2. Principe général (simple)

Le nouveau processus repose sur 3 briques:

1. Google Sheets: point d'entrée des mises à jour métier (saisie par les équipes non-data).
2. Airbyte: ingestion automatique des onglets Google Sheets vers la base de données (zone brute).
3. dbt: application des règles métier pour produire des données "corrigées" prêtes pour Metabase et le site web.

Important: les données brutes sont conservées. Les corrections sont appliquées en couche "curated" (pas d'écrasement direct de la source brute).

## 3. Parcours utilisateur attendu

### User Story A (fichier CNC annuel)

1. Bob reçoit le fichier `agreement CNC 2026.csv`.
2. Bob copie les données dans le Google Sheet `AGREEMENT CNC`, onglet `2026`.
3. Airbyte synchronise l'onglet vers la base (zone raw).
4. dbt applique les règles de consolidation avec les données existantes (clé de jointure: `visa_number`).
5. Les nouveaux titres corrigés sont visibles dans Metabase et dans l'application web.

### User Story B (correction ponctuelle sur une entité)

1. Bob ouvre le Google Sheet `Modification data`.
2. Bob va dans l'onglet de l'entité concernée (ex: `CreditHolder`).
3. Bob ajoute une ligne:
   - `id`
   - `column_name`
   - `new_value`
   - `modification_date`
   - `requested_by`
   - `reason` (optionnel)
4. Airbyte ingère la ligne.
5. dbt applique la correction sur la couche finale exposée aux outils de consultation.

## 4. Brouillon de schéma à dessiner (version non technique)

Tu peux dessiner le schéma en 5 blocs:

1. **Sources métier (Google Sheets)**
   - `AGREEMENT CNC` (1 onglet par année)
   - `Modification data` (1 onglet par entité)
2. **Ingestion (Airbyte)**
   - Synchronisation planifiée vers tables raw
3. **Transformation (dbt)**
   - Normalisation
   - Contrôles qualité
   - Application des corrections
4. **Données publiées**
   - Tables/vues "curated"
5. **Consommateurs**
   - Metabase
   - API backend
   - Front webapp

Flèches à indiquer:
`Google Sheets -> Airbyte -> Raw -> dbt -> Curated -> Metabase/API/Frontend`

<pre> ```mermaid flowchart LR GS[Google Sheets] --> AB[Airbyte] AB --> RAW[Raw Tables] RAW --> DBT[dbt Transformations] DBT --> CUR[Curated Tables] CUR --> META[Metabase] CUR --> API[Backend API] CUR --> FE[Frontend Webapp] ``` </pre>


## 5. Bénéfices attendus

1. Processus répétable d'année en année.
2. Moins de dépendance aux interventions techniques manuelles.
3. Traçabilité de qui a demandé quoi et quand.
4. Conservation de l'historique (audit).
5. Réduction du risque d'erreurs de mise à jour directe.

## 6. Ce que ce processus ne fait pas (et c'est volontaire)

1. Il ne modifie pas automatiquement les fichiers source externes.
2. Il ne supprime pas les données brutes historiques.
3. Il n'autorise pas n'importe quelle colonne à être modifiée sans règles.

## 7. Points de validation à faire côté métier

1. Validation des noms d'onglets et du format exact des colonnes.
2. Validation des rôles d'accès Google Sheets (qui peut éditer, qui peut seulement voir).
3. Validation des délais de prise en compte (ex: toutes les nuits, ou plusieurs fois par jour).
4. Validation des règles métier prioritaires (ex: si plusieurs corrections existent pour la même cellule).

## 8. Règle métier clé à communiquer

Pour les mises à jour CNC, la clé de correspondance est `visa_number`.
Le titre (`original_name`) est un attribut modifiable, pas une clé d'identification.

