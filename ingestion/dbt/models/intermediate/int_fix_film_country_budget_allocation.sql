WITH dedup AS (
    -- Si 2 corrections sont faites pour un même id, on ne garde que la plus récente
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_date DESC) AS rn
    FROM {{ ref('stg_fix_film_country_budget_allocation') }}
)

SELECT
    id,
    country_id,
    film_id,
    budget_allocation
FROM dedup
WHERE rn = 1