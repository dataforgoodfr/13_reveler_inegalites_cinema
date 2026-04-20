with agreement_cnc as (
    select *
    from {{ ref('int_agreement_cnc_latest_by_visa') }}
),

historical_films as (
    select *
    from {{ ref('stg_raw_ric_films') }}
),

merged as (
    select
        historical_films.film_id,
        coalesce(agreement_cnc.visa_number, historical_films.visa_number) as visa_number,
        coalesce(agreement_cnc.original_name, historical_films.original_name) as original_name,
        agreement_cnc.original_name as original_name_from_agreement_cnc,
        historical_films.original_name as original_name_from_raw_films,
        coalesce(agreement_cnc.cnc_agrement_year, historical_films.cnc_agrement_year) as cnc_agrement_year,
        agreement_cnc.cnc_agrement_year as cnc_agrement_year_from_agreement_cnc,
        historical_films.cnc_agrement_year as cnc_agrement_year_from_raw_films,
        coalesce(agreement_cnc.cnc_rank, historical_films.cnc_rank) as cnc_rank,
        coalesce(agreement_cnc.budget, historical_films.budget) as budget,
        coalesce(agreement_cnc.asr, historical_films.asr) as asr,
        coalesce(agreement_cnc.eof, historical_films.eof) as eof,
        coalesce(agreement_cnc.parity_bonus, historical_films.parity_bonus) as parity_bonus,
        coalesce(agreement_cnc.sofica_funding, historical_films.sofica_funding) as sofica_funding,
        coalesce(agreement_cnc.tax_credit, historical_films.tax_credit) as tax_credit,
        coalesce(agreement_cnc.regional_funding, historical_films.regional_funding) as regional_funding,
        agreement_cnc.genre_raw as genre_from_agreement_cnc,
        agreement_cnc.directors_raw,
        agreement_cnc.producers_raw,
        agreement_cnc.nationality_raw,
        agreement_cnc.broadcasters_free_raw,
        agreement_cnc.broadcasters_paid_raw,
        historical_films.allocine_id,
        historical_films.mubi_id,
        historical_films.release_date,
        historical_films.duration_minutes,
        historical_films.budget_category,
        historical_films.genre_categories,
        historical_films.broadcasters,
        historical_films.is_french_financed,
        agreement_cnc._airbyte_extracted_at as agreement_cnc_extracted_at,
        agreement_cnc._airbyte_generation_id as agreement_cnc_generation_id,
        agreement_cnc._airbyte_raw_id as agreement_cnc_airbyte_raw_id,
        agreement_cnc.visa_number is not null as exists_in_agreement_cnc,
        historical_films.film_id is not null as exists_in_raw_films,
        historical_films.film_id is null as is_new_film,
        (
            agreement_cnc.visa_number is not null
            and historical_films.film_id is not null
            and (
                agreement_cnc.original_name is distinct from historical_films.original_name
                or agreement_cnc.cnc_agrement_year is distinct from historical_films.cnc_agrement_year
                or agreement_cnc.cnc_rank is distinct from historical_films.cnc_rank
                or agreement_cnc.budget is distinct from historical_films.budget
                or agreement_cnc.asr is distinct from historical_films.asr
                or agreement_cnc.eof is distinct from historical_films.eof
                or agreement_cnc.parity_bonus is distinct from historical_films.parity_bonus
                or agreement_cnc.sofica_funding is distinct from historical_films.sofica_funding
                or agreement_cnc.tax_credit is distinct from historical_films.tax_credit
                or agreement_cnc.regional_funding is distinct from historical_films.regional_funding
            )
        ) as has_cnc_payload_change,
        case
            when historical_films.film_id is null then true
            when historical_films.allocine_id is null then true
            when agreement_cnc.visa_number is not null and (
                agreement_cnc.original_name is distinct from historical_films.original_name
                or agreement_cnc.cnc_agrement_year is distinct from historical_films.cnc_agrement_year
            ) then true
            else false
        end as should_scrape_allocine
    from historical_films
    full outer join agreement_cnc
        on historical_films.visa_number = agreement_cnc.visa_number
)

select
    film_id,
    visa_number,
    original_name,
    original_name_from_agreement_cnc,
    original_name_from_raw_films,
    cnc_agrement_year,
    cnc_agrement_year_from_agreement_cnc,
    cnc_agrement_year_from_raw_films,
    cnc_rank,
    budget,
    asr,
    eof,
    parity_bonus,
    sofica_funding,
    tax_credit,
    regional_funding,
    genre_from_agreement_cnc,
    directors_raw,
    producers_raw,
    nationality_raw,
    broadcasters_free_raw,
    broadcasters_paid_raw,
    allocine_id,
    mubi_id,
    release_date,
    duration_minutes,
    budget_category,
    genre_categories,
    broadcasters,
    is_french_financed,
    agreement_cnc_extracted_at,
    agreement_cnc_generation_id,
    agreement_cnc_airbyte_raw_id,
    exists_in_agreement_cnc,
    exists_in_raw_films,
    is_new_film,
    has_cnc_payload_change,
    should_scrape_allocine
from merged
where visa_number is not null
