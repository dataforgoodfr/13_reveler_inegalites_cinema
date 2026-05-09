{{
  config(materialized = 'view')
}}

SELECT
    CAST("VISA" AS INTEGER) AS cnc_visa,
    TRIM("TITRE") AS cnc_name,
    CAST("ID_ALLOCINE" AS INTEGER) AS allocine_id,
    CAST("ID_MUBI" AS INTEGER) AS mubi_id,
    CAST("ID_TMDB" AS INTEGER) AS tmdb_id,
    -- METADATA
    TO_DATE("UPDATED_DATE", 'DD/MM/YYYY') AS updated_date,
    TRIM("UPDATED_BY") AS updated_by,
    _airbyte_raw_id AS airbyte_raw_id,
    CAST(_airbyte_generation_id AS INTEGER) AS airbyte_generation_id,
    CAST(_airbyte_extracted_at AS TIMESTAMP)  AS airbyte_extraction_date,
    CAST(_airbyte_meta AS JSON) AS airbyte_meta
FROM {{ source('raw', 'id_matching') }}
WHERE "UPDATED_BY" IS NOT NULL
    AND "UPDATED_DATE" IS NOT NULL