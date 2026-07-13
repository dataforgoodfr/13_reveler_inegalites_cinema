SELECT
    matching.film_id,
    films.allocine_visa,
    films.allocine_id,
    films.allocine_name,
    films.release_date,
    films.duration_mn
FROM {{ ref('stg_allocine_films') }} AS films
LEFT JOIN {{ ref('stg_id_matching') }} AS matching
    ON films.allocine_id = matching.allocine_id