{{
  config(materialized = 'view')
}}

SELECT
    CAST("ID" AS INTEGER) AS id,
    CAST("FILM_ID" AS INTEGER) AS film_id,
    CAST("CREDIT_HOLDER_ID" AS INTEGER) AS credit_holder_id,
    CAST("AWARD_ID" AS INTEGER) AS award_id,
    TO_DATE("DATE", 'DD/MM/YYYY') AS nomination_date,
    CAST("IS_WINNER" AS BOOLEAN) AS is_winner,
    -- METADATA
    TO_DATE("UPDATED_DATE", 'DD/MM/YYYY') AS updated_date,
    TRIM("UPDATED_BY") AS updated_by,
    TRIM(_airbyte_raw_id) AS airbyte_raw_id,
    CAST(_airbyte_generation_id AS INTEGER) AS airbyte_generation_id,
    CAST(_airbyte_extracted_at AS TIMESTAMP) AS airbyte_extraction_date,
    CAST(_airbyte_meta AS JSON) AS airbyte_meta
FROM {{ source('raw', 'award_nominations') }}
WHERE "UPDATED_BY" IS NOT NULL
    AND "UPDATED_DATE" IS NOT NULL
    AND "ID" <> '9999999999999'