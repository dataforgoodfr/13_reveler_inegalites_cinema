with source_data as (
    select
        _airbyte_raw_id,
        _airbyte_extracted_at,
        _airbyte_generation_id,
        _airbyte_meta,
        nullif(trim("VISA"), '') as visa_number_raw,
        nullif(trim("TITRE"), '') as original_name_raw,
        nullif(trim("ANNEE"), '') as cnc_agrement_year_raw,
        nullif(trim("RANG"), '') as cnc_rank_raw,
        nullif(trim("DEVIS"), '') as budget_raw,
        nullif(trim("ASR"), '') as asr_raw,
        nullif(trim("GENRE"), '') as genre_raw,
        nullif(trim("REALISATEUR"), '') as directors_raw,
        nullif(trim("PRODUCTEURS"), '') as producers_raw,
        nullif(trim("NATIONALITE"), '') as nationality_raw,
        nullif(trim("CLAIR"), '') as broadcasters_free_raw,
        nullif(trim("PAYANT"), '') as broadcasters_paid_raw,
        nullif(trim("EOF"), '') as eof_raw,
        nullif(trim("SOFICA"), '') as sofica_funding_raw,
        nullif(trim("BONUS_PARITE"), '') as parity_bonus_raw,
        nullif(trim("AIDE_REGIONALE"), '') as regional_funding_raw,
        nullif(trim("CREDIT_D_IMPOT"), '') as tax_credit_raw
    from {{ source('raw', 'agreement_cnc') }}
),

normalized as (
    select
        _airbyte_raw_id,
        _airbyte_extracted_at,
        _airbyte_generation_id,
        _airbyte_meta,
        nullif(regexp_replace(visa_number_raw, '[^0-9A-Za-z]', '', 'g'), '') as visa_number,
        original_name_raw as original_name,
        case
            when cnc_agrement_year_raw ~ '^[0-9]+$' then cnc_agrement_year_raw::integer
            else null
        end as cnc_agrement_year,
        case
            when regexp_replace(cnc_rank_raw, '[^0-9]', '', 'g') <> ''
                then regexp_replace(cnc_rank_raw, '[^0-9]', '', 'g')::integer
            else null
        end as cnc_rank,
        case
            when regexp_replace(budget_raw, '[^0-9]', '', 'g') <> ''
                then regexp_replace(budget_raw, '[^0-9]', '', 'g')::numeric
            else null
        end as budget,
        asr_raw as asr,
        genre_raw as genre_raw,
        directors_raw,
        producers_raw,
        nationality_raw,
        broadcasters_free_raw,
        broadcasters_paid_raw,
        case
            when upper(eof_raw) in ('X', 'OUI', 'TRUE', '1', 'YES') then true
            when eof_raw is null then null
            else false
        end as eof,
        case
            when upper(sofica_funding_raw) in ('X', 'OUI', 'TRUE', '1', 'YES') then true
            when sofica_funding_raw is null then null
            else false
        end as sofica_funding,
        case
            when upper(parity_bonus_raw) in ('X', 'OUI', 'TRUE', '1', 'YES') then true
            when parity_bonus_raw is null then null
            else false
        end as parity_bonus,
        case
            when upper(regional_funding_raw) in ('X', 'OUI', 'TRUE', '1', 'YES') then true
            when regional_funding_raw is null then null
            else false
        end as regional_funding,
        case
            when upper(tax_credit_raw) in ('X', 'OUI', 'TRUE', '1', 'YES') then true
            when tax_credit_raw is null then null
            else false
        end as tax_credit
    from source_data
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
from normalized
where visa_number is not null
