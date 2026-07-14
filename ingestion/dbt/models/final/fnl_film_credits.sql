SELECT
    chr.film_id,
    chr.role_id,
    chr.credit_holder_id
FROM {{ ref('int_credit_holders_role') }} AS chr
LEFT JOIN {{ ref('int_id_matching') }} AS matching
    ON chr.allocine_id = matching.allocine_id