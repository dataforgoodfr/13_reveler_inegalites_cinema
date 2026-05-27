{{
  config(
    materialized = 'view',
    tags = ['mubi']
  )
}}

SELECT
    run_id,
    extracted_at,
    film_link,
    split_part(film_link, '/', -1) AS mubi_slug,
    mubi_id,
    festival,
    year AS award_year,
    distinction,
    award,
    record_hash
FROM {{ source('raw', 'mubi_film_awards') }}
WHERE scrape_status IN ('success', 'no_awards')
  AND film_link IS NOT NULL
