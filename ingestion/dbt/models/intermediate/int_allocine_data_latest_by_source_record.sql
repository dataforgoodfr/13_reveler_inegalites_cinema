with ranked as (
    select
        *,
        row_number() over (
            partition by source_record_id
            order by extracted_ts desc, run_id desc
        ) as row_num
    from {{ ref('stg_allocine_data') }}
)

select
    run_id,
    extracted_ts,
    source_record_id,
    cnc_visa,
    cnc_name,
    cnc_agreement_year,
    match_strategy,
    search_url,
    source_url,
    allocine_id,
    allocine_name,
    allocine_url,
    allocine_visa,
    release_date,
    duration_mn,
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
    scrapping_status,
    error_message,
    record_hash
from ranked
where row_num = 1
