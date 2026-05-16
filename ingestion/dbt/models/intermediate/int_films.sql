SELECT
    movie_id,
    cnc_visa,
    cnc_name,
    genre, 
    cnc_agreement_year,
    budget,
    director,
    ARRAY(
        SELECT
            CASE 
                WHEN str_filmography_rank = '1' THEN '1er film'
                WHEN str_filmography_rank = '2' THEN '2e film'
                WHEN str_filmography_rank IN ('3', '4') THEN '3e film ou plus'
                ELSE NULL
            END
        FROM UNNEST(filmography_rank) AS str_filmography_rank
    ) AS filmography_rank,
    producer,
    ARRAY(
        SELECT 
            CASE str_broadcaster
                WHEN 'France5' THEN 'FranceTV'
                ELSE str_broadcaster
            END
        FROM UNNEST(
            COALESCE(paid_broadcaster, ARRAY[]::TEXT[]) ||
            COALESCE(free_broadcaster, ARRAY[]::TEXT[])
        ) AS str_broadcaster
        WHERE str_broadcaster != 'FranceÔ'
    ) AS broadcasters,
    country_funder,
    has_eof,
    has_parity_bonus,
    has_asr,
    has_sofica,
    has_tax_credit,
    has_regional_funding
FROM {{ ref('stg_films') }}