Owner: Joel Teixeira

Last reviewed: 2026-05-05

Status: Etat actuel du projet + draft d'architecture pour airbyte et dbt.



# Schéma ingestion, seeds, Airbyte et dbt

Ce schéma montre les relations entre scripts de seed, tables PostgreSQL, connecteurs Airbyte et modèles dbt.

Important:

1. `ingestion/airbyte/` ne contient aujourd'hui qu'un `.gitkeep`; les connecteurs Airbyte sont documentés comme configuration externe, pas encore versionnés dans le repo.

## Diagramme de flux global actuel

```mermaid
flowchart LR

    XLSX_C5050[dataset5050_cnc_films_agrees_2003_2024.xlsx]
    %% Seed and scraper jobs
    SEED_CNC[seed_cnc_movies.py]

    subgraph ALLOCINE_MODULE[Allocine module]
        direction TB
        ALLOCINE((Allocine pages))
        ALLOCINE_RUNNER[allocine_runner.py]
        ALLOCINE_SCRAPER[allocine_scraper.py]
        ALLOCINE_MATCH[allocine_film_matcher.py]
        ALLOCINE_ENRICH[allocine_film_enricher.py]
        SEED_ALLOCINE[seed_allocine_movies_details.py]
        ALLOCINE_MATCH_CSV[allocine_matches.csv]
        ALLOCINE_ENRICHED_CSV[allocine_matches_enriched.csv]
    end

    subgraph MUBI_MODULE[MUBI module]
        direction TB
        MUBI((MUBI pages))
        MUBI_AWARDS_CSV[films_all_awards.csv]
        MUBI_PAGE_SCRAPER[mubi_page_scraper.py]
        MUBI_FESTIVAL_SCRAPER[mubi_all_festival_films_to_csv.py]
        MUBI_AWARDS_SCRAPER[mubi_all_film_awards_to_csv.py]
        SEED_MUBI[seed_film_awards.py]
        MUBI_FESTIVAL_CSV[festival_films.csv / festivals_all_films.csv]
    end


    subgraph APP_DB[Application tables ric_*]
        direction LR
        RIC_FILMS[(ric_films)]
        RIC_COUNTRIES[(ric_countries)]
        RIC_BUDGET[(ric_film_country_budget_allocations)]
        RIC_ROLES[(ric_roles)]
        RIC_CREDIT_HOLDERS[(ric_credit_holders)]
        RIC_FILM_CREDITS[(ric_film_credits)]
        RIC_GENRES[(ric_genres)]
        RIC_FILMS_GENRES[(ric_films_genres)]
        RIC_POSTERS[(ric_posters)]
        RIC_TRAILERS[(ric_trailers)]
        RIC_FESTIVALS[(ric_festivals)]
        RIC_FESTIVAL_AWARDS[(ric_festival_awards)]
        RIC_AWARD_NOMINATIONS[(ric_award_nominations)]
        RIC_POSTER_CHARS[(ric_poster_characters)]
        RIC_TRAILER_CHARS[(ric_trailer_characters)]
    end
    
    subgraph ML[ML module]
        direction TB
        ML_MAIN[ml-image/main.py]
        ML_TRAILER_CSV[trailer_predictions.csv]
        ML_POSTER_CSV[poster_predictions.csv]
        SEED_POSTER[seed_poster_predictions.py]
        SEED_TRAILER[seed_trailer_predictions.py]
    end

    %% MUBI scraping and awards seed
    MUBI_FESTIVAL_SCRAPER --> MUBI_PAGE_SCRAPER
    MUBI_AWARDS_SCRAPER --> MUBI_PAGE_SCRAPER
    MUBI --> MUBI_FESTIVAL_SCRAPER --> MUBI_FESTIVAL_CSV
    MUBI_FESTIVAL_CSV --> MUBI_AWARDS_SCRAPER
    MUBI --> MUBI_AWARDS_SCRAPER --> MUBI_AWARDS_CSV
    MUBI_AWARDS_CSV --> SEED_MUBI
    SEED_MUBI --> RIC_FILMS
    SEED_MUBI --> RIC_COUNTRIES
    SEED_MUBI --> RIC_BUDGET
    RIC_ROLES --> SEED_MUBI
    SEED_MUBI --> RIC_CREDIT_HOLDERS
    SEED_MUBI --> RIC_FILM_CREDITS
    SEED_MUBI --> RIC_FESTIVALS
    SEED_MUBI --> RIC_FESTIVAL_AWARDS
    SEED_MUBI --> RIC_AWARD_NOMINATIONS

    %% ML prediction seeds
    ML_POSTER_CSV --> SEED_POSTER
    RIC_FILMS --> SEED_POSTER
    RIC_POSTERS --> SEED_POSTER
    SEED_POSTER --> RIC_POSTER_CHARS

    ML_TRAILER_CSV --> SEED_TRAILER
    RIC_FILMS --> SEED_TRAILER
    RIC_TRAILERS --> SEED_TRAILER
    SEED_TRAILER --> RIC_TRAILER_CHARS

    %% CNC consolidated seed
    XLSX_C5050 --> SEED_CNC
    SEED_CNC --> RIC_FILMS
    SEED_CNC --> RIC_COUNTRIES
    SEED_CNC --> RIC_BUDGET
    SEED_CNC --> RIC_ROLES
    SEED_CNC --> RIC_CREDIT_HOLDERS
    SEED_CNC --> RIC_FILM_CREDITS

    %% Allocine scraping and seed
    ALLOCINE_RUNNER --> ALLOCINE_MATCH
    ALLOCINE_RUNNER --> ALLOCINE_ENRICH
    ALLOCINE_MATCH --> ALLOCINE_SCRAPER
    ALLOCINE_ENRICH --> ALLOCINE_SCRAPER
    RIC_FILMS --> ALLOCINE_MATCH
    ALLOCINE --> ALLOCINE_MATCH
    ALLOCINE_MATCH --> ALLOCINE_MATCH_CSV
    ALLOCINE_MATCH_CSV --> ALLOCINE_ENRICH
    ALLOCINE --> ALLOCINE_ENRICH
    ALLOCINE_ENRICH --> ALLOCINE_ENRICHED_CSV
    ALLOCINE_ENRICHED_CSV --> SEED_ALLOCINE
    SEED_ALLOCINE --> RIC_FILMS
    SEED_ALLOCINE --> RIC_POSTERS
    SEED_ALLOCINE --> RIC_TRAILERS
    SEED_ALLOCINE --> RIC_GENRES
    SEED_ALLOCINE --> RIC_FILMS_GENRES
    SEED_ALLOCINE --> RIC_ROLES
    SEED_ALLOCINE --> RIC_CREDIT_HOLDERS
    SEED_ALLOCINE --> RIC_FILM_CREDITS




    classDef pythonScript fill:#fde047,stroke:#a16207,color:#111827;
    class SEED_CNC,ALLOCINE_RUNNER,ALLOCINE_SCRAPER,ALLOCINE_MATCH,ALLOCINE_ENRICH,SEED_ALLOCINE,MUBI_PAGE_SCRAPER,MUBI_FESTIVAL_SCRAPER,MUBI_AWARDS_SCRAPER,SEED_MUBI,SEED_POSTER,SEED_TRAILER,ML_MAIN pythonScript;

    classDef csvFile fill:#bbf7d0,stroke:#15803d,color:#111827;
    class MUBI_AWARDS_CSV,ML_POSTER_CSV,ML_TRAILER_CSV,ALLOCINE_MATCH_CSV,ALLOCINE_ENRICHED_CSV,MUBI_FESTIVAL_CSV,XLSX_C5050 csvFile;
    
    classDef regenerableFile stroke-dasharray: 5 4;
    class MUBI_AWARDS_CSV,ML_POSTER_CSV,ML_TRAILER_CSV,ALLOCINE_MATCH_CSV,ALLOCINE_ENRICHED_CSV,MUBI_FESTIVAL_CSV regenerableFile;
    
    classDef internetPage fill:#bfdbfe,stroke:#1d4ed8,color:#111827;
    class ALLOCINE,MUBI internetPage;
    
```

## Diagramme de flux focalisé sur Airbyte et dbt

```mermaid
flowchart LR

    %% External sources
    subgraph EXTERNAL_SOURCES[External sources]
        direction TB
        GS_CNC[Google Sheet AGREEMENT CNC]
        GS_MOD[Google Sheet Modification data]
        GS_ID_MATCHING[Google Sheet Film ID matching]
    end

    subgraph INGESTION[Ingestion module]
        direction TB
        %% Airbyte
        SRC_GS_CNC[src_gsheet_agreement_cnc<br/>external config]
        SRC_GS_MOD[src_gsheet_modification_data<br/>external config]
        SRC_GS_ID_MATCHING[src_gsheet_film_id_matching<br/>external config]

        %% Raw and dbt
        AB_AGREEMENT[(ab_raw.agreement_cnc)]
        AB_MOD[(ab_raw.modification_data)]
        AB_ID_MATCHING[(ab_raw.film_id_matching)]

        STG_CNC(stg_agreement_cnc)
        STG_MOD(stg_modification_data)
        STG_ID_MATCHING(stg_film_id_matching)

        %% Airbyte/DBT flow
        GS_CNC --> SRC_GS_CNC --> AB_AGREEMENT --> STG_CNC
        GS_MOD --> SRC_GS_MOD --> AB_MOD --> STG_MOD
        GS_ID_MATCHING --> SRC_GS_ID_MATCHING --> AB_ID_MATCHING --> STG_ID_MATCHING
    end

    classDef googleSheet fill:#bbf7d0,stroke:#15803d,color:#111827;
    class GS_CNC,GS_MOD,GS_ID_MATCHING googleSheet;
    
    classDef dbtModel fill:#fed7aa,stroke:#f97316,color:#111827;
    class STG_CNC,STG_MOD,STG_ID_MATCHING dbtModel;

    classDef airbyteNode fill:#f5d0fe,stroke:#c026d3,color:#111827;
    class SRC_GS_CNC,SRC_GS_MOD,SRC_GS_ID_MATCHING airbyteNode;

```
## Lecture rapide

1. Le diagramme global montre une chaîne de dépendances centrée sur `ric_films`: le seed CNC crée l'inventaire de base, puis les briques Allocine, MUBI et ML ajoutent chacune leur enrichissement sur des tables `ric_*` déjà peuplées.
2. Le flux Allocine est en deux temps: matching vers `allocine_matches.csv`, enrichissement vers `allocine_matches_enriched.csv`, puis injection finale dans `ric_films`, `ric_posters`, `ric_trailers`, `ric_genres`, `ric_films_genres`, `ric_credit_holders` et `ric_film_credits`.
3. Le flux MUBI part des pages web, passe par des CSV intermédiaires, puis alimente surtout les dimensions festivals, prix, nominations et une partie des crédits, avec possibilité de créer un film minimal si aucun film applicatif ne matche.
4. Le flux ML ne remonte pas directement depuis `ml-image/main.py` vers la base: dans l'état actuel documenté, les seeds lisent surtout les CSV de prédictions déjà disponibles et recréent `ric_poster_characters` et `ric_trailer_characters`.
5. Le diagramme Airbyte/dbt isole une autre couche: Google Sheets alimente `ab_raw`, puis dbt normalise chaque source via `stg_agreement_cnc`, `stg_modification_data` et `stg_film_id_matching` avant toute consolidation métier.
6. Ce second diagramme décrit donc une cible d'ingestion et de préparation, pas encore le chaînage complet vers les seeds applicatifs visibles dans le diagramme global.
7. Le point de jonction cible entre les deux mondes reste la consolidation CNC par `visa_number`: une fois publiée par dbt, elle doit redevenir l'entrée fiable du seed CNC puis des scrapers.
8. Les fichiers statiques actuellement versionnés sont:
   - `database/data/cnc/dataset5050_cnc_films_agrees_2003_2024.xlsx`
   - `database/data/mubi/films_all_awards.csv`
   - `database/data/machine_learning_predictions/poster_predictions.csv`
   - `database/data/machine_learning_predictions/trailer_predictions.csv`

## Points de vigilance

1. Le diagramme Airbyte/dbt ne montre aujourd'hui que les modèles de staging; la fusion réelle entre historique CNC, nouvelles charges Airbyte et éventuelles corrections métier n'apparaît pas encore dans le schéma ni dans le code versionné.
2. La dépendance globale à `ric_films` impose un ordre strict: seed CNC d'abord, enrichissement Allocine ensuite, seed MUBI et seeds ML seulement quand les médias et films existent déjà.
3. Le handoff par CSV reste un point fragile pour Allocine, MUBI et ML: ces fichiers intermédiaires peuvent devenir obsolètes, être régénérés partiellement, ou diverger de la base si aucune orchestration ne fige l'ordre d'exécution.
4. `ingestion/airbyte/` ne versionne toujours pas les connecteurs ni les connexions; le diagramme de cible repose donc sur une configuration externe qui peut dériver du repo.
5. Le Google Sheet `Film ID matching` apparaît dans le schéma Airbyte/dbt, mais son usage aval n'est pas encore raccordé explicitement au matching applicatif dans le diagramme global.
6. `ml-image/main.py` n'est pas, à lui seul, la garantie de production des CSV de prédictions affichés dans le schéma; il faut documenter ou automatiser clairement la génération de ces artefacts pour éviter une confusion entre inputs existants et sorties réelles.
7. Les rôles et crédits sont alimentés par plusieurs flux (`seed_cnc_movies.py`, `seed_allocine_movies_details.py`, `seed_film_awards.py`); sans règles de précédence explicites, le risque est d'écraser ou dupliquer des informations métier.
