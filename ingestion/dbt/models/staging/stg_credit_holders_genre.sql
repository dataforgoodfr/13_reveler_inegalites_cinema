{{
  config(materialized = 'view')
}}

SELECT 
    CAST(full_name AS TEXT) AS full_name,
    CAST(first_name AS TEXT) AS first_name,
    CAST(last_name AS TEXT) AS last_name,
    CAST(gender AS TEXT) AS gender,
    CAST(cnc_movie_name AS TEXT) AS cnc_movie_name,
    -- METADATA
    TRIM(_airbyte_raw_id) AS airbyte_raw_id,
    CAST(_airbyte_generation_id AS INTEGER) AS airbyte_generation_id,
    CAST(_airbyte_extracted_at AS TIMESTAMP) AS airbyte_extraction_date,
    CAST(_airbyte_meta AS JSON) AS airbyte_meta
FROM {{ source('raw', 'credit_holders_genre') }}