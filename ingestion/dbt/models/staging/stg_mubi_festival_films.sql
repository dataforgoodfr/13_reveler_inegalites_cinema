{{
  config(
    materialized = 'view',
    tags = ['mubi']
  )
}}

-- raw.mubi_festival_films is an append-only scrape log: the same festival
-- edition page (festival_slug, year, page_num) can be scraped across several
-- runs -- after blocked/error retries, or when runs overlap -- and each
-- successful scrape appends a full copy of the page's films. We deduplicate to
-- the single most recent successful run per edition page here.
--
-- We dedup at the RUN level (not the row level) on purpose: each page lists a
-- given film exactly once, so keeping all rows of the latest run preserves
-- every distinct film while dropping the re-inserted copies from earlier runs.
-- record_hash cannot be used as a dedup key because it hashes run_id /
-- extracted_at and is therefore unique per insert.
WITH success_films AS (
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
        -- Normalise the film link by stripping Mubi's locale prefix so the same
        -- film resolves to one key. Mubi serves '/fr/fr/films/x', '/fr/us/films/x',
        -- etc. for the same film; the scraper now stores the '/films/x' form, but
        -- older rows still carry a locale prefix, so we reconcile both here.
        -- Matches MubiPageScraper._normalize_film_link.
        regexp_replace(film_link, '^.*?(/films/)', '\1') AS film_link,
        split_part(film_link, '/', -1) AS mubi_slug,
        record_hash,
        DENSE_RANK() OVER (
            PARTITION BY festival_slug, year, page_num
            ORDER BY extracted_at DESC, run_id DESC
        ) AS run_rank
    FROM {{ source('raw', 'mubi_festival_films') }}
    WHERE scrape_status = 'success'
      AND film_link IS NOT NULL
)
SELECT
    run_id,
    extracted_at,
    festival_slug,
    festival_name,
    festival_year,
    page_num,
    mubi_title,
    mubi_director,
    mubi_country,
    nominations,
    film_link,
    mubi_slug,
    record_hash
FROM success_films
WHERE run_rank = 1
