SELECT
    full_name,
    ANY_VALUE(first_name) AS first_name,
    ANY_VALUE(last_name) AS last_name,
    ANY_VALUE(gender) AS gender,
    ANY_VALUE(cnc_movie_name) AS cnc_movie_name
FROM {{ ref('stg_credit_holders_genre') }}
GROUP BY full_name
-- a credit holder can have multiple entries, so we aggregate by full_name