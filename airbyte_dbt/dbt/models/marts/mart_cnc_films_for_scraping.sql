with agreement_cnc as (
    select *
    from {{ ref('int_agreement_cnc_latest_by_visa') }}
)
select *
from agreement_cnc
