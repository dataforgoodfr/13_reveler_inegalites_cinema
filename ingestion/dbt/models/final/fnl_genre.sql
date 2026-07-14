WITH base AS (
    SELECT
        genre_id,
        genre_name
    FROM {{ ref('int_film_genres') }}
    GROUP BY
        genre_id,
        genre_name
)
SELECT
    COALESCE(fix.id, base.genre_id) AS genre_id,
    COALESCE(fix.name, base.genre_name) AS genre_name
FROM base
LEFT JOIN {{ ref('int_fix_genres') }} AS fix
    ON base.genre_id = fix.id
ORDER BY genre_id