{{
  config(
    materialized = 'view',
    tags = ['mubi']
  )
}}

-- One row per (festival edition, film). mubi_id and cnc_visa resolved via
-- the awards table, which is where the numeric Mubi ID is extracted during scraping.
WITH film_ids AS (
    SELECT DISTINCT film_link, mubi_id
    FROM {{ ref('stg_mubi_film_awards') }}
    WHERE mubi_id IS NOT NULL
)
SELECT
    f.festival_slug,
    f.festival_name,
    f.festival_year,
    f.mubi_title,
    f.mubi_director,
    f.mubi_country,
    f.nominations,
    f.film_link,
    f.mubi_slug,
    ids.mubi_id,
    m.cnc_visa,
    m.allocine_id,
    f.extracted_at
FROM {{ ref('stg_mubi_festival_films') }} f
LEFT JOIN film_ids ids
    ON f.film_link = ids.film_link
LEFT JOIN {{ ref('int_id_matching') }} m
    ON ids.mubi_id = m.mubi_id
