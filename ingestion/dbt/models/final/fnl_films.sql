WITH french_financed AS (
    SELECT
        film_id,
        country_name,
        budget_allocation,
        CASE
            WHEN country_name = 'France' AND budget_allocation >= 50 THEN TRUE
            ELSE FALSE
        END AS is_french_financed
    FROM {{ ref('int_film_country_budget_allocation') }}
    WHERE country_name = 'France'
)
SELECT
    films.film_id,
    films.cnc_visa,
    COALESCE(allocine.allocine_name, films.cnc_name) AS movie_name,
    films.cnc_agreement_year,
    allocine.release_date,
    allocine.duration_mn,
    films.budget,
    films.budget_category,
    films.broadcasters,
    french_financed.is_french_financed,
    films.has_parity_bonus,
    films.has_eof,
    films.has_sofica,
    films.has_tax_credit,
    films.has_regional_funding,
    films.filmography_rank,
    films.has_asr
FROM {{ ref('int_cnc_films') }} AS films
INNER JOIN {{ ref('int_id_matching') }} AS matching
    ON films.cnc_visa = matching.cnc_visa
LEFT JOIN {{ ref('int_allocine_films') }} AS allocine
    ON matching.allocine_id = allocine.allocine_id
LEFT JOIN french_financed
    ON films.film_id = french_financed.film_id