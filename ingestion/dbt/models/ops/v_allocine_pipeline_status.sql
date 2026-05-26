{{
  config(
    materialized = 'view',
    tags = ['phase2']
  )
}}

SELECT
    CAST(extracted_ts AS DATE) AS extracted_date,
    EXTRACT(HOUR FROM extracted_ts)::INTEGER AS extracted_hour,
    extracted_ts,
    run_id,
    cnc_visa,
    source_record_id,
    scrapping_status,
    match_strategy,
    record_hash,
    error_message
FROM {{ ref('stg_allocine_data') }}
