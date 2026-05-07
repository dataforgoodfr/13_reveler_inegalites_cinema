with ranked as (
    select
        *,
        row_number() over (
            partition by source_record_id
            order by extracted_at desc, run_id desc
        ) as row_num
    from {{ ref('stg_allocine_data') }}
)

select
    run_id,
    extracted_at,
    source_record_id,
    visa_number,
    original_name,
    cnc_agrement_year,
    match_strategy,
    search_url,
    source_url,
    allocine_id,
    allocine_title,
    allocine_url,
    allocine_visa_number,
    release_date_raw,
    release_date,
    duration_raw,
    duration_minutes,
    genres,
    trailer_url,
    direction,
    casting,
    screenwriters,
    production,
    technical_team,
    soundtrack,
    distribution,
    companies,
    scrape_status,
    error_message,
    record_hash
from ranked
where row_num = 1
