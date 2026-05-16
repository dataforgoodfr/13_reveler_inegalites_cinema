WITH dedup AS (
    -- Si 2 corrections sont faites pour un même id, on ne garde que la plus récente
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_date DESC) AS rn
    FROM {{ ref('stg_fix_film_genres') }}
)

SELECT
    id,
    film_id,
    genre_id
FROM dedup
WHERE rn = 1