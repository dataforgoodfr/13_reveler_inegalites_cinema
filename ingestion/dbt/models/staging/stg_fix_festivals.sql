{{
  config(materialized = 'view')
}}

SELECT
    CAST("ID" AS INTEGER) AS id,
    TRIM("NAME") AS name,
    TRIM("DESCRIPTION") AS description,
    TRIM("IMAGEBASE64") AS imagebase64,
    CAST("COUNTRY_ID" AS INTEGER) AS country_id,
    -- METADATA
    TO_DATE("UPDATED_DATE", 'DD/MM/YYYY') AS updated_date,
    TRIM("UPDATED_BY") AS updated_by,
    TRIM(_airbyte_raw_id) AS airbyte_raw_id,
    CAST(_airbyte_generation_id AS INTEGER) AS airbyte_generation_id,
    CAST(_airbyte_extracted_at AS TIMESTAMP) AS airbyte_extraction_date,
    CAST(_airbyte_meta AS JSON) AS airbyte_meta
FROM {{ source('raw', 'festivals') }}
WHERE "UPDATED_BY" IS NOT NULL
    AND "UPDATED_DATE" IS NOT NULL
    AND "ID" <> '9999999999999'