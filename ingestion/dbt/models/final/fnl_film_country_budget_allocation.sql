SELECT
    COALESCE(fix.id, original.id) AS id,
    COALESCE(fix.movie_id, original.movie_id) AS movie_id,
    COALESCE(fix.cnc_visa, original.cnc_visa) AS cnc_visa,
    COALESCE(fix.country_id, original.country_id) AS country_id,
    COALESCE(fix.country_name, original.country_name) AS country_name,
    COALESCE(fix.budget_allocation, original.budget_allocation) AS budget_allocation
FROM {{ ref('int_film_country_budget_allocation') }} AS original
LEFT JOIN {{ ref('int_fix_film_country_budget_allocation') }} AS fix
    ON original.id = fix.id