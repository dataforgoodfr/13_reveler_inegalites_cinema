WITH
-- 1. Données pour les individus (direction, casting, screenwriters, production, technical_team, distribution)
individuals AS (
    -- Direction (type = "individual", role = "director")
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(UNNEST(direction), '" ') AS full_name,
        SPLIT_PART(TRIM(UNNEST(direction), '" '), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(UNNEST(direction), '" '), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        'Réalisateur' AS role
    FROM {{ ref('stg_allocine_films') }}
    WHERE direction IS NOT NULL

    UNION ALL

    -- Casting (type = "individual", role = "actor")
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(UNNEST(casting), '" ') AS full_name,
        SPLIT_PART(TRIM(UNNEST(casting), '" '), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(UNNEST(casting), '" '), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        'Acteur' AS role
    FROM {{ ref('stg_allocine_films') }}
    WHERE casting IS NOT NULL

    UNION ALL

    -- Screenwriters (type = "individual", role = JSON->>'role')
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(elem->>'name') AS full_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        COALESCE(NULLIF(TRIM(elem->>'role'), ''), 'screenwriter') AS role
    FROM {{ ref('stg_allocine_films') }},
    JSONB_ARRAY_ELEMENTS(screenwriters::JSONB) AS elem
    WHERE screenwriters IS NOT NULL

    UNION ALL

    -- Production (type = "individual", role = JSON->>'role')
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(elem->>'name') AS full_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        COALESCE(NULLIF(TRIM(elem->>'role'), ''), 'production') AS role
    FROM {{ ref('stg_allocine_films') }},
    JSONB_ARRAY_ELEMENTS(production::JSONB) AS elem
    WHERE production IS NOT NULL

    UNION ALL

    -- Technical team (type = "individual", role = JSON->>'role')
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(elem->>'name') AS full_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        COALESCE(NULLIF(TRIM(elem->>'role'), ''), 'technical') AS role
    FROM {{ ref('stg_allocine_films') }},
    JSONB_ARRAY_ELEMENTS(technical_team::JSONB) AS elem
    WHERE technical_team IS NOT NULL

    UNION ALL

    -- Distribution (type = "individual", role = JSON->>'role')
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(elem->>'name') AS full_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        COALESCE(NULLIF(TRIM(elem->>'role'), ''), 'distribution') AS role
    FROM {{ ref('stg_allocine_films') }},
    JSONB_ARRAY_ELEMENTS(distribution::JSONB) AS elem
    WHERE distribution IS NOT NULL

    UNION ALL

    -- Soundtrack (type = "individual", role = JSON->>'role')
    SELECT
        allocine_id,
        'Individual' AS type,
        TRIM(elem->>'name') AS full_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 1) AS first_name,
        SPLIT_PART(TRIM(elem->>'name'), ' ', 2) AS last_name,
        NULL::TEXT AS legal_name,
        COALESCE(NULLIF(TRIM(elem->>'role'), ''), 'Compositeur') AS role
    FROM {{ ref('stg_allocine_films') }},
    JSONB_ARRAY_ELEMENTS(soundtrack::JSONB) AS elem
    WHERE soundtrack IS NOT NULL
),

-- 2. Données pour les companies
companies AS (
    -- Companies (type = "company", role = NULL)
    SELECT
        allocine_id,
        'Company' AS type,
        NULL::TEXT AS full_name,
        NULL::TEXT AS first_name,
        NULL::TEXT AS last_name,
        TRIM(elem->>'name') AS legal_name,
        TRIM(elem->>'role') AS role
    FROM {{ ref('stg_allocine_films') }},
    JSONB_ARRAY_ELEMENTS(companies::JSONB) AS elem
    WHERE companies IS NOT NULL
),

unioned AS (
    -- 3. Union des deux CTEs
    SELECT
        allocine_id,
        type,
        full_name,
        first_name,
        last_name,
        legal_name,
        role
    FROM individuals
    UNION ALL
    SELECT
        allocine_id,
        type,
        full_name,
        first_name,
        last_name,
        legal_name,
        role
    FROM companies
)

SELECT
    matching.film_id,
    unioned.type,
    MD5(CAST(unioned.full_name AS TEXT))::UUID AS credit_holder_id,
    unioned.full_name,
    unioned.first_name,
    unioned.last_name,
    unioned.legal_name,
    MD5(CAST(unioned.role AS TEXT))::UUID AS role_id,
    unioned.role
FROM unioned
LEFT JOIN {{ ref('stg_id_matching') }} AS matching
    ON unioned.allocine_id = matching.allocine_id