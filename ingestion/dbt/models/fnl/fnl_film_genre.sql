SELECT DISTINCT
    film_id,
    genre_id
FROM {{ ref('int_film_genres') }}