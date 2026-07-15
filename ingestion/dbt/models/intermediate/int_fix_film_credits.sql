WITH dedup AS (
    -- Si 2 corrections sont faites pour un même id, on ne garde que la plus récente
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY film_credit_id ORDER BY updated_date DESC) AS rn
    FROM {{ ref('stg_fix_film_credits') }}
)
SELECT
    film_credit_id,
    film_id,
    role_id,
    credit_holder_id
FROM dedup
WHERE rn = 1