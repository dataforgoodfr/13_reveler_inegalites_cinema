{{
  config(
    materialized = 'view',
    tags = ['mubi']
  )
}}

-- One row per (film, festival award). Joined to id_matching on mubi_id.
-- cnc_visa is null when the film has no entry in id_matching yet.
SELECT
    a.film_link,
    a.mubi_slug,
    a.mubi_id,
    a.festival,
    a.award_year,
    a.distinction,
    a.award,
    a.extracted_at,
    m.cnc_visa,
    m.allocine_id
FROM {{ ref('stg_mubi_film_awards') }} a
LEFT JOIN {{ ref('int_id_matching') }} m
    ON a.mubi_id = m.mubi_id
WHERE a.award IS NOT NULL
