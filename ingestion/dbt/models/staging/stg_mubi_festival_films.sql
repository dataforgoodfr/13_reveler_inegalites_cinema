{{
  config(
    materialized = 'view',
    tags = ['mubi']
  )
}}

SELECT
    run_id,
    extracted_at,
    festival_slug,
    festival_name,
    year AS festival_year,
    page_num,
    title AS mubi_title,
    director AS mubi_director,
    country AS mubi_country,
    nominations,
    film_link,
    split_part(film_link, '/', -1) AS mubi_slug,
    record_hash
FROM {{ source('raw', 'mubi_festival_films') }}
WHERE scrape_status = 'success'
  AND film_link IS NOT NULL
