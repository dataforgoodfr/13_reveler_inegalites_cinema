Created by: Hugo Laurens, Joel Teixeira

Last reviewed: 2026-05-05

Status: draft

# Processus proposé de mise à jour des données (version validation métier)

## 1. Pourquoi ce changement

Aujourd'hui, les corrections de données (ex: nouveaux titres CNC, correction d'un genre ou d'une date de naissance) peuvent nécessiter des manipulations techniques et manuelles.

Objectif: permettre aux équipes non techniques de proposer des mises à jour de manière simple, traçable, et répétable chaque année, sans perdre l'historique des données brutes.

## 2. Principe général (simple)

Le nouveau processus repose sur 3 briques:

1. Google Sheets: point d'entrée des mises à jour métier (saisie par les équipes non-data).
2. Airbyte: ingestion automatique des Google Sheets vers la base de données (zone brute), avec un onglet unique pour `AGREEMENT CNC` et un onglet par entité pour `Modification data`.
3. dbt: application des règles métier pour produire des données "corrigées" prêtes pour Metabase et le site web.

Important: les données brutes sont conservées. Les corrections sont appliquées en couche "curated" (pas d'écrasement direct de la source brute).

## 3. Parcours utilisateur attendu

### User Story A (fichier CNC annuel)

1. Bob reçoit le fichier `agreement CNC 2026.csv`.
2. Bob copie les données dans le Google Sheet `AGREEMENT CNC`, dans l'onglet unique du fichier, en ajoutant les nouvelles lignes en bas du tableau.
3. Airbyte synchronise cet onglet unique vers la base (zone raw).
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

## 4. Architecture technique cible

```mermaid
flowchart LR
    SCRAP[Scraping Algorithms] --> AB[Airbyte]
    GSCNC[Google Sheets - AGREEMENT CNC\nonglet unique] --> AB
    GSMOD[Google Sheets - Modification data] --> AB
    AB --> UPD[Updates / Modifications Tables]
    AB --> RAW
    subgraph PG[PostgreSQL Database]
        RAW
        UPD
        CUR[Curated Tables]
    end

    RAW --> DBT[dbt Transformations]
    UPD --> DBT
    DBT --> CUR
    CUR --> META[Metabase]
    CUR --> API[Backend API]
    CUR --> FE[Frontend Webapp]
```

![Schéma architecture Airbyte dbt](./archi_ingestion.png)

## 4.1 Lecture rapide du diagramme

1. Le point d'entrée métier est double: `AGREEMENT CNC` pour les nouvelles lignes CNC et `Modification data` pour les corrections ponctuelles.
2. Airbyte joue ici uniquement le rôle de passerelle d'ingestion vers PostgreSQL: il charge à la fois la zone brute (`RAW`) et les tables de modifications (`UPD`).
3. dbt lit ensuite ces deux couches pour produire une couche `CUR` qui concentre les règles de consolidation et de correction.
4. Les usages finaux partent tous de `CUR`: Metabase, l'API backend et la webapp consultent la même version consolidée des données.
5. Le diagramme montre donc un principe important: on ne corrige pas la source brute directement; on conserve l'historique et on applique les règles dans la couche curated.


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

1. Validation du nom unique de l'onglet CNC, des onglets de `Modification data`, et du format exact des colonnes.
2. Validation des rôles d'accès Google Sheets (qui peut éditer, qui peut seulement voir).
3. Validation des délais de prise en compte (ex: toutes les nuits, ou plusieurs fois par jour).
4. Validation des règles métier prioritaires (ex: si plusieurs corrections existent pour la même cellule).

## 7.1 Points de vigilance techniques et fonctionnels

1. Le diagramme fait converger plusieurs sources vers Airbyte; cela suppose des schémas de colonnes stables, sinon la synchronisation et les modèles dbt casseront au premier changement de feuille.
2. `UPD` est volontairement séparé de `RAW`; il faut garder cette frontière pour conserver la traçabilité des demandes et éviter des écrasements silencieux.
3. La couche `CUR` devient un point d'autorité unique pour trois consommateurs différents; toute règle de correction ambiguë ou non déterministe y aura un impact immédiat sur Metabase, l'API et le frontend.
4. Le diagramme ne montre pas de mécanisme d'orchestration, de fréquence de sync ni de contrôle qualité; sans cela, le délai entre saisie métier et publication restera difficile à garantir.
5. Le bloc `Scraping Algorithms` apparaît comme une source vers Airbyte; si cette partie est conservée dans la cible, il faut expliciter quel type de données est produit par ces scrapers, dans quelles tables, et avec quelles clés de rapprochement avec le flux CNC.

## 8. Règle métier clé à communiquer

Pour les mises à jour CNC, la clé de correspondance est `visa_number`.
Le titre (`original_name`) est un attribut modifiable, pas une clé d'identification.
