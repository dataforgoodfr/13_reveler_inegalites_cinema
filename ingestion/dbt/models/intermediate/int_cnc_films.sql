SELECT
    matching.film_id,
    films.cnc_visa,
    films.cnc_name,
    films.genre,
    films.cnc_agreement_year,
    films.budget,
    CASE
        WHEN films.budget < 2000000 THEN 'Moins de 2M€'
        WHEN films.budget >= 2000000 AND films.budget < 5000000 THEN '2 à 5M€'
        WHEN films.budget >= 5000000 AND films.budget < 10000000 THEN '5 à 10M€'
        WHEN films.budget >= 10000000 AND films.budget < 20000000 THEN '10 à 20M€'
        WHEN films.budget >= 20000000 THEN 'Plus de 20M€'
        ELSE NULL
    END AS budget_category,
    films.director,
    ARRAY(
        SELECT
            CASE
                WHEN str_filmography_rank = '1' THEN '1er film'
                WHEN str_filmography_rank = '2' THEN '2e film'
                WHEN str_filmography_rank IN ('3', '4') THEN '3e film ou plus'
                ELSE NULL
            END
        FROM UNNEST(films.director_rank) AS str_filmography_rank
    ) AS filmography_rank,
    films.producer,
    ARRAY(
        SELECT
            CASE str_broadcaster
                WHEN 'France5' THEN 'FranceTV'
                ELSE str_broadcaster
            END
        FROM UNNEST(
            COALESCE(films.paid_broadcaster, ARRAY[]::TEXT[]) ||
            COALESCE(films.free_broadcaster, ARRAY[]::TEXT[])
        ) AS str_broadcaster
        WHERE str_broadcaster != 'FranceÔ'
    ) AS broadcasters,
    films.country_funder,
    films.has_eof,
    films.has_parity_bonus,
    films.has_asr,
    films.has_sofica,
    films.has_tax_credit,
    films.has_regional_funding
FROM {{ ref('stg_cnc_films') }} AS films
LEFT JOIN {{ ref('stg_id_matching') }} AS matching
    ON films.cnc_visa = matching.cnc_visa