SELECT
    DISTINCT
    casting.credit_holder_id,
    COALESCE(fix.type, casting.type) AS type,
    COALESCE(fix.first_name, casting.first_name) AS first_name,
    COALESCE(fix.last_name, casting.last_name) AS last_name,
    COALESCE(fix.legal_name, casting.legal_name) AS legal_name,
    COALESCE(fix.gender, NULL) AS gender,
    COALESCE(fix.birthdate, NULL) AS birthdate
FROM {{ ref('int_credit_holders_role') }} AS casting
LEFT JOIN {{ ref('int_fix_credit_holders') }} AS fix
    ON casting.credit_holder_id = fix.id
ORDER BY casting.credit_holder_id