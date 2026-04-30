select
    id as film_id,
    nullif(regexp_replace(trim(visa_number), '[^0-9A-Za-z]', '', 'g'), '') as visa_number,
    original_name,
    release_date,
    duration_minutes,
    budget,
    parity_bonus,
    eof,
    sofica_funding,
    tax_credit,
    regional_funding,
    cnc_rank,
    allocine_id,
    cnc_agrement_year,
    asr,
    mubi_id,
    budget_category,
    genre_categories,
    broadcasters,
    is_french_financed
from {{ source('app_raw', 'ric_films') }}
where visa_number is not null
