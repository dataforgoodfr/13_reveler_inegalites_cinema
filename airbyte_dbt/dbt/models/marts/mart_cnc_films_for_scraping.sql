with agreement_cnc as (
    select *
    from {{ ref('stg_raw_ric_films') }}
)
select *,
case when film_id = 4 then TRUE else FALSE end as should_scrape_allocine
from agreement_cnc
-- THIS MUST BE COMPLETED TO MERGE BETWEEN THE TWO SOURCES AND GET THE COMPLETE LIST OF FILMS TO SCRAPE