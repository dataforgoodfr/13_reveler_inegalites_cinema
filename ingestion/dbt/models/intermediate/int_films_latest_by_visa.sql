with ranked as (
    select
        *,
        row_number() over (
            partition by cnc_visa
            order by airbyte_extraction_date desc, airbyte_generation_id desc, airbyte_raw_id desc
        ) as row_num
    from {{ ref('stg_films') }}
)

select
    movie_id,
    cnc_visa,
    cnc_name,
    genre,
    cnc_agreement_year,
    budget,
    director,
    filmography_rank,
    producer,
    paid_broadcaster,
    free_broadcaster,
    country_budget_allocation,
    has_eof,
    has_parity_bonus,
    has_asr,
    has_sofica,
    has_tax_credit,
    has_regional_funding,
    updated_date,
    updated_by,
    airbyte_raw_id,
    airbyte_generation_id,
    airbyte_extraction_date,
    airbyte_meta
from ranked
where row_num = 1
