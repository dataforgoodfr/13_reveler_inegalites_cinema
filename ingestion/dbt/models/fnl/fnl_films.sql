WITH french_financed AS (
    SELECT
        movie_id,
        country,
        budget_allocation,
        CASE
            WHEN country = 'France' AND budget_allocation >= 50 THEN TRUE
            ELSE FALSE
        END AS is_french_financed
    FROM {{ ref('int_film_country_budget_allocation') }}
    WHERE country = 'France'
)
SELECT
    films.movie_id,
    films.allocine_id,
    films.mubi_id,
    films.tmdb_id,
    films.cnc_visa,
    COALESCE(allocine.allocine_name, films.cnc_name) AS movie_name,
    films.cnc_agreement_year,
    allocine.release_date,
    allocine.duration_mn,
    films.budget,
    films.budget_category,
    allocine.genre_category,
    films.broadcasters,
    french_financed.is_french_financed,
    films.has_parity_bonus,
    films.has_eof,
    films.has_sofica_funding,
    films.has_tax_credit,
    films.has_regional_funding,
    films.filmography_rank,
    films.has_asr,
FROM {{ ref('int_films') }} AS films
LEFT JOIN {{ ref('int_allocine_data') }} AS allocine
    ON films.allocine_id = allocine.allocine_id
LEFT JOIN french_financed
    ON films.movie_id = french_financed.movie_id