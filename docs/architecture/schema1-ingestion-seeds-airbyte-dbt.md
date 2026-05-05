Owner: Joel Teixeira

Last reviewed: 2026-05-05

Status: Etat actuel du projet + draft d'architecture pour airbyte et dbt.

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

## Architecture cible


```mermaid
flowchart LR

    subgraph GOOGLE_SHEETS[Google Sheets]
        direction TB
        GS_CNC[GSheet AGREEMENT CNC]
        GS_ID_MATCHING[GSheet Film ID matching]
        GS_FILM_CREDITS[GSheet Fix Film credits]
        GS_FILM_GENRES[GSheet Fix Film genres]
        GS_FILMS_COUNTRY_BUDGET_ALLOCATION[GSheet Fix Film country budget allocation]
        GS_AWARD_NOMINATIONS[GSheet Fix award nominations]
        GS_CREDIT_HOLDERS[GSheet Fix credit holders]
        GS_ROLES[GSheet Fix roles]
        GS_GENRES[GSheet Fix genres]
        GS_COUNTRIES[GSheet Fix countries]
        GS_FESTIVAL[GSheet Fix festivals]
        GS_FESTIVAL_AWARDS[GSheet Fix festival awards]
    end

    subgraph AIRBYTE_FLOW[Airbyte flow]
        direction TB
        SRC_GS_CNC[src_gsheet_agreement_cnc]
        SRC_GS_ID_MATCHING[src_gsheet_film_id_matching]

        SRC_GS_FILM_CREDITS[src_gsheet_fix_film_credits]
        SRC_GS_FILM_GENRES[src_gsheet_fix_film_genres]
        SRC_GS_FILMS_COUNTRY_BUDGET_ALLOCATION[src_gsheet_fix_film_country_budget_allocation]
        SRC_GS_AWARD_NOMINATIONS[src_gsheet_fix_award_nominations]
        SRC_GS_CREDIT_HOLDERS[src_gsheet_fix_credit_holders]
        SRC_GS_ROLES[src_gsheet_fix_roles]
        SRC_GS_GENRES[src_gsheet_fix_genres]
        SRC_GS_COUNTRIES[src_gsheet_fix_countries]
        SRC_GS_FESTIVAL[src_gsheet_fix_festivals]
        SRC_GS_FESTIVAL_AWARDS[src_gsheet_fix_festival_awards]

        AB_AGREEMENT[(ab_raw.films)]
        AB_ID_MATCHING[(ab_raw.id_matching)]

        AB_FILM_CREDITS[(ab_raw.fix_film_credits)]
        AB_FILM_GENRES[(ab_raw.fix_film_genres)]
        AB_FILMS_COUNTRY_BUDGET_ALLOCATION[(ab_raw.fix_films_country_budget_allocation)]
        AB_AWARD_NOMINATIONS[(ab_raw.fix_award_nominations)]
        AB_CREDIT_HOLDERS[(ab_raw.fix_credit_holders)]
        AB_ROLES[(ab_raw.fix_roles)]
        AB_GENRES[(ab_raw.fix_genres)]
        AB_COUNTRIES[(ab_raw.fix_countries)]
        AB_FESTIVAL[(ab_raw.fix_festivals)]
        AB_FESTIVAL_AWARDS[(ab_raw.fix_festival_awards)]

    end

    subgraph SCRAPING_FLOW[Scraping flow]
        direction TB
        SCRAPE_ALLOCINE[Allocine scraper<br/>scraping_allocine.py]
        SCRAPE_MUBI[MUBI scraper<br/>scraping_mubi.py]
        AB_ALLOCINE[(ab_raw.allocine_data)]
        AB_MUBI[(ab_raw.mubi_data)]
    end

    subgraph DBT_FLOW[dbt flow]
        direction TB
        STG_FILMS(stg_films)
        STG_FILM_CREDITS(stg_film_credits)
        STG_GENRES(stg_genres)
        STG_FILM_GENRES(stg_film_genres)
        STG_COUNTRIES(stg_countries)
        STG_BUDGET_ALLOC(stg_film_country_budget_allocation)
        STG_ROLES(stg_roles)
        STG_CREDIT_HOLDERS(stg_credit_holders)
        STG_AWARD_NOMINATIONS(stg_award_nominations)
        STG_FESTIVALS(stg_festivals)
        STG_FESTIVAL_AWARDS(stg_festival_awards)

        FNL_FILMS(fnl_films)
        FNL_GENRES(fnl_genres)
        FNL_FILM_CREDITS(fnl_film_credits)
        FNL_FILMS_GENRES(fnl_films_genres)
        FNL_COUNTRIES(fnl_countries)
        FNL_BUDGET_ALLOC(fnl_film_country_budget_allocation)
        FNL_ROLES(fnl_roles)
        FNL_CREDIT_HOLDERS(fnl_credit_holders)
        FNL_AWARD_NOMINATIONS(fnl_award_nominations)
        FNL_FESTIVALS(fnl_festivals)
        FNL_FESTIVAL_AWARDS(fnl_festival_awards)
    end

    subgraph FRONT_METABASE[Front + Metabase]
        direction TB
        FRONT_APP[Frontend app]
        METABASE_APP[Metabase]
    end


    %% Scraping flow
    AB_ID_MATCHING --> SCRAPE_ALLOCINE
    AB_ALLOCINE --> SCRAPE_ALLOCINE --> AB_ALLOCINE

    AB_ID_MATCHING --> SCRAPE_MUBI
    AB_MUBI --> SCRAPE_MUBI --> AB_MUBI


    %% Airbyte/DBT flow
    GS_CNC --> SRC_GS_CNC --> AB_AGREEMENT --> STG_FILMS --> FNL_FILMS
    GS_ID_MATCHING --> SRC_GS_ID_MATCHING --> AB_ID_MATCHING
    GS_FILM_CREDITS --> SRC_GS_FILM_CREDITS --> AB_FILM_CREDITS --> STG_FILM_CREDITS --> FNL_FILM_CREDITS
    GS_FILM_GENRES --> SRC_GS_FILM_GENRES --> AB_FILM_GENRES --> STG_FILM_GENRES --> FNL_FILMS_GENRES
    GS_FILMS_COUNTRY_BUDGET_ALLOCATION --> SRC_GS_FILMS_COUNTRY_BUDGET_ALLOCATION --> AB_FILMS_COUNTRY_BUDGET_ALLOCATION --> STG_BUDGET_ALLOC --> FNL_BUDGET_ALLOC
    GS_AWARD_NOMINATIONS --> SRC_GS_AWARD_NOMINATIONS --> AB_AWARD_NOMINATIONS --> STG_AWARD_NOMINATIONS --> FNL_AWARD_NOMINATIONS
    GS_CREDIT_HOLDERS --> SRC_GS_CREDIT_HOLDERS --> AB_CREDIT_HOLDERS --> STG_CREDIT_HOLDERS --> FNL_CREDIT_HOLDERS
    GS_ROLES --> SRC_GS_ROLES --> AB_ROLES --> STG_ROLES --> FNL_ROLES
    GS_GENRES --> SRC_GS_GENRES --> AB_GENRES --> STG_GENRES --> FNL_GENRES
    GS_COUNTRIES --> SRC_GS_COUNTRIES --> AB_COUNTRIES --> STG_COUNTRIES --> FNL_COUNTRIES
    GS_FESTIVAL --> SRC_GS_FESTIVAL --> AB_FESTIVAL --> STG_FESTIVALS --> FNL_FESTIVALS
    GS_FESTIVAL_AWARDS --> SRC_GS_FESTIVAL_AWARDS --> AB_FESTIVAL_AWARDS --> STG_FESTIVAL_AWARDS --> FNL_FESTIVAL_AWARDS

    AB_ALLOCINE --> FNL_FILMS
    AB_ALLOCINE --> FNL_GENRES
    AB_ALLOCINE --> FNL_FILM_CREDITS
    AB_ALLOCINE --> FNL_FILMS_GENRES
    AB_ALLOCINE --> FNL_COUNTRIES
    AB_ALLOCINE --> FNL_BUDGET_ALLOC
    AB_ALLOCINE --> FNL_ROLES
    AB_ALLOCINE --> FNL_CREDIT_HOLDERS
    AB_ALLOCINE --> FNL_AWARD_NOMINATIONS
    AB_ALLOCINE --> FNL_FESTIVALS
    AB_ALLOCINE --> FNL_FESTIVAL_AWARDS

    AB_MUBI --> FNL_FILMS
    AB_MUBI --> FNL_CREDIT_HOLDERS
    AB_MUBI --> FNL_AWARD_NOMINATIONS
    AB_MUBI --> FNL_FESTIVALS
    AB_MUBI --> FNL_FESTIVAL_AWARDS

    FNL_FILMS --> FRONT_METABASE
    FNL_GENRES --> FRONT_METABASE
    FNL_FILM_CREDITS --> FRONT_METABASE
    FNL_FILMS_GENRES --> FRONT_METABASE
    FNL_COUNTRIES --> FRONT_METABASE
    FNL_BUDGET_ALLOC --> FRONT_METABASE
    FNL_ROLES --> FRONT_METABASE
    FNL_CREDIT_HOLDERS --> FRONT_METABASE
    FNL_AWARD_NOMINATIONS --> FRONT_METABASE
    FNL_FESTIVALS --> FRONT_METABASE
    FNL_FESTIVAL_AWARDS --> FRONT_METABASE


    classDef googleSheet fill:#bbf7d0,stroke:#15803d,color:#111827;
    class GS_CNC,GS_ID_MATCHING,GS_FILM_CREDITS,GS_FILM_GENRES,GS_FILMS_COUNTRY_BUDGET_ALLOCATION,GS_AWARD_NOMINATIONS,GS_CREDIT_HOLDERS,GS_ROLES,GS_GENRES,GS_COUNTRIES,GS_FESTIVAL,GS_FESTIVAL_AWARDS googleSheet;

    classDef dbtModel fill:#fed7aa,stroke:#f97316,color:#111827;
    class STG_FILM_CREDITS,STG_GENRES,STG_FILM_GENRES,STG_COUNTRIES,STG_BUDGET_ALLOC,STG_ROLES,STG_CREDIT_HOLDERS,STG_AWARD_NOMINATIONS,STG_FESTIVALS,STG_FESTIVAL_AWARDS,STG_FILMS dbtModel;
    class FNL_FILMS,FNL_GENRES,FNL_FILM_CREDITS,FNL_FILMS_GENRES,FNL_COUNTRIES,FNL_BUDGET_ALLOC,FNL_ROLES,FNL_CREDIT_HOLDERS,FNL_AWARD_NOMINATIONS,FNL_FESTIVALS,FNL_FESTIVAL_AWARDS dbtModel;

    classDef airbyteNode fill:#f5d0fe,stroke:#c026d3,color:#111827;
    class SRC_GS_CNC,SRC_GS_ID_MATCHING,SRC_GS_FILM_CREDITS,SRC_GS_FILM_GENRES,SRC_GS_FILMS_COUNTRY_BUDGET_ALLOCATION,SRC_GS_AWARD_NOMINATIONS,SRC_GS_CREDIT_HOLDERS,SRC_GS_ROLES,SRC_GS_GENRES,SRC_GS_COUNTRIES,SRC_GS_FESTIVAL,SRC_GS_FESTIVAL_AWARDS airbyteNode;

    classDef pythonScript fill:#fde047,stroke:#a16207,color:#111827;
    class SCRAPE_ALLOCINE,SCRAPE_MUBI pythonScript;
```

## Lecture rapide de l'architecture cible

1. Les Google Sheets restent les points d'entrée des corrections métier, puis Airbyte les charge dans `ab_raw`.
2. dbt normalise ces tables brutes en `stg_*`, puis publie des tables finales `fnl_*` consommées par le frontend et Metabase.
3. Les scrapers sont prévus comme des exécutions Airbyte, tandis que Prefect orchestre l'ordre global des runs, les dépendances, les relances et le déclenchement bout en bout.
4. Les scrapers n'utilisent pas uniquement `id_matching`: ils lisent aussi la table dans laquelle ils écrivent déjà pour savoir ce qui a déjà été traité.
5. Pour Allociné, le scraper charge `ab_raw.allocine_data` pour récupérer les IDs déjà scrapés.
6. Il charge en parallèle `ab_raw.id_matching` pour obtenir la liste complète des IDs à traiter.
7. Il compare les deux listes et isole les IDs présents dans `id_matching` mais absents de `allocine_data`.
8. Le scraping cible ne porte donc que sur les IDs manquants, puis les nouvelles données scrapées sont ajoutées à la table existante.
9. Le même principe s'applique au flux MUBI: la table de sortie existante sert de mémoire d'exécution, et `id_matching` sert de liste de référence.

## Points de vigilance sur le scraping cible

1. La logique de comparaison suppose que les IDs portés par `id_matching`, `allocine_data` et `mubi_data` soient strictement homogènes en format et en clé métier.
2. Si la table de sortie contient des lignes partielles, en erreur ou obsolètes, le scraper peut considérer à tort un ID comme déjà traité.
3. Ajouter uniquement les IDs manquants évite de retraiter tout l'historique, mais impose une stratégie claire de rescraping quand une donnée source change ou quand un scraping précédent était incomplet.
4. La table de sortie devient à la fois un stockage de résultats et un registre d'avancement; il faut donc tracer les erreurs, dates de scraping et éventuels statuts de reprise.
5. Le découpage Airbyte exécution / Prefect orchestration doit rester net: Airbyte lance les connecteurs de scraping, mais Prefect garde la responsabilité du chaînage global, des retries inter-étapes et de la supervision.
6. Si plusieurs runs s'exécutent en parallèle, le calcul des IDs manquants peut produire des doublons d'écriture sans verrouillage ou contrainte d'unicité adaptée.
