SELECT
    cnc.movie_id,
    allocine.cnc_visa,
    allocine.allocine_id,
    UNNEST(
        ARRAY(SELECT jsonb_array_elements_text("allocine.genres"))
    ) AS genre
FROM {{ ref('stg_allocine_films') }} AS allocine
LEFT JOIN {{ ref('stg_cnc_films') }} AS cnc
    ON allocine.cnc_visa = cnc.cnc_visa