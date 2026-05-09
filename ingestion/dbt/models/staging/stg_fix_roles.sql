{{
  config(materialized = 'view')
}}

SELECT
    CAST("ID" AS INTEGER) AS id,
    TRIM("NAME") AS name,
    CAST("IS_KEY_ROLE" AS BOOLEAN) AS is_key_role,
    TRIM("ALLOCINE_NAME") AS allocine_name,
    TRIM("INCLUSIVE_NAME") AS inclusive_name,
    -- METADATA
    TO_DATE("UPDATED_DATE", 'DD/MM/YYYY') AS updated_date,
    TRIM("UPDATED_BY") AS updated_by,
    TRIM(_airbyte_raw_id) AS airbyte_raw_id,
    CAST(_airbyte_generation_id AS INTEGER) AS airbyte_generation_id,
    CAST(_airbyte_extracted_at AS TIMESTAMP) AS airbyte_extraction_date,
    CAST(_airbyte_meta AS JSON) AS airbyte_meta
FROM {{ source('raw', 'roles') }}
WHERE "UPDATED_BY" IS NOT NULL
    AND "UPDATED_DATE" IS NOT NULL
    AND "ID" <> '9999999999999'