with ranked as (
    select
        *,
        row_number() over (
            partition by visa_number
            order by _airbyte_extracted_at desc, _airbyte_generation_id desc, _airbyte_raw_id desc
        ) as row_num
    from {{ ref('stg_films') }}
)

select
    _airbyte_raw_id,
    _airbyte_extracted_at,
    _airbyte_generation_id,
    _airbyte_meta,
    visa_number,
    original_name,
    cnc_agrement_year,
    cnc_rank,
    budget,
    asr,
    genre_raw,
    directors_raw,
    producers_raw,
    nationality_raw,
    broadcasters_free_raw,
    broadcasters_paid_raw,
    eof,
    sofica_funding,
    parity_bonus,
    regional_funding,
    tax_credit
from ranked
where row_num = 1
