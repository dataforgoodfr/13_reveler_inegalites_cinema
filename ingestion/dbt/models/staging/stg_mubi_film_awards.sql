{{
  config(
    materialized = 'view',
    tags = ['mubi']
  )
}}

-- raw.mubi_film_awards is an append-only scrape log; the awards page for a film
-- can be scraped across several runs (retries or overlapping/parallel Prefect
-- runs), each appending a full copy of that film's awards. We keep only the most
-- recent successful run per film_link. Dedup is at the RUN level (a film's awards
-- all come from one page scrape), so all award rows of the latest run survive.
-- record_hash is unusable as a key because it hashes run_id / extracted_at.
WITH award_rows AS (
    SELECT
        run_id,
        extracted_at,
        -- Normalise the film link by stripping Mubi's locale prefix so the same
        -- film resolves to one key (and joins cleanly to stg_mubi_festival_films).
        -- Matches MubiPageScraper._normalize_film_link.
        regexp_replace(film_link, '^.*?(/films/)', '\1') AS film_link,
        split_part(film_link, '/', -1) AS mubi_slug,
        mubi_id,
        festival,
        year AS award_year,
        distinction,
        award,
        record_hash,
        DENSE_RANK() OVER (
            PARTITION BY film_link
            ORDER BY extracted_at DESC, run_id DESC
        ) AS run_rank
    FROM {{ source('raw', 'mubi_film_awards') }}
    WHERE scrape_status IN ('success', 'no_awards')
      AND film_link IS NOT NULL
)
SELECT
    run_id,
    extracted_at,
    film_link,
    mubi_slug,
    mubi_id,
    festival,
    award_year,
    distinction,
    award,
    record_hash
FROM award_rows
WHERE run_rank = 1
