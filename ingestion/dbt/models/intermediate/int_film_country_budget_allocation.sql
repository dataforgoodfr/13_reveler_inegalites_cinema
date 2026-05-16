WITH base AS (
    SELECT
        movie_id,
        cnc_visa,
        (elem->>'country') AS country_name_raw,
        CASE INITCAP(UNACCENT(TRIM(elem->>'country')))
            -- France
            WHEN 'Fr' THEN 'France'
            -- Allemagne
            WHEN 'All' THEN 'Allemagne'
            -- Italie
            WHEN 'It' THEN 'Italie'
            -- Belgique
            WHEN 'Belg' THEN 'Belgique'
            WHEN 'Bel' THEN 'Belgique'
            WHEN 'Be' THEN 'Belgique'
            -- Grande Bretagne
            WHEN 'Gb' THEN 'Grande-Bretagne'
            WHEN 'Grande Bretagne' THEN 'Grande-Bretagne'
            -- Espagne
            WHEN 'Esp' THEN 'Espagne'
            WHEN 'Es' THEN 'Espagne'
            -- Portugal
            WHEN 'Port' THEN 'Portugal'
            -- Luxembourg
            WHEN 'Lux' THEN 'Luxembourg'
            -- Canada
            WHEN 'Can' THEN 'Canada'
            -- Irlande
            WHEN 'Irl' THEN 'Irlande'
            -- Russie
            WHEN 'Ru' THEN 'Russie'
            -- Israël
            WHEN 'Isr' THEN 'Israël'
            WHEN 'Israel' THEN 'Israël'
            -- Roumanie
            WHEN 'Roum' THEN 'Roumanie'
            -- République Tchèque
            WHEN 'Rep Tcheque' THEN 'République-Tchèque'
            WHEN 'Rep Tcheq' THEN 'République-Tchèque'
            WHEN 'Rep Tch' THEN 'République-Tchèque'
            WHEN 'Republique Tcheque' THEN 'République-Tchèque'
            -- Pays-Bas
            WHEN 'Paysbas' THEN 'Pays-Bas'
            WHEN 'Pays Bas' THEN 'Pays-Bas'
            -- Nouvelle-Zélande
            WHEN 'Nouvellezelande' THEN 'Nouvelle-Zélande'
            WHEN 'Nouvelle Zelande' THEN 'Nouvelle-Zélande'
            -- Bulgarie
            WHEN 'Bulg' THEN 'Bulgarie'
            -- Bosnie-Herzégovine
            WHEN 'Bosnie Herz' THEN 'Bosnie-Herzégovine'
            WHEN 'Bosnie' THEN 'Bosnie-Herzégovine'
            WHEN 'Bosnie Herzegovine' THEN 'Bosnie-Herzégovine'
            -- Macédoine du Nord
            WHEN 'Macedoine Du N' THEN 'Macédoine du Nord'
            WHEN 'Macedoine' THEN 'Macédoine du Nord'
            WHEN 'Macedoine Du Nord' THEN 'Macédoine du Nord'
            -- Afrique du Sud
            WHEN 'Af Du Sud' THEN 'Afrique du Sud'
            WHEN 'Afrique Du Sud' THEN 'Afrique du Sud'
            -- Mexique
            WHEN 'Mex' THEN 'Mexique'
            -- Danemark
            WHEN 'Dan' THEN 'Danemark'
            -- Pologne
            WHEN 'Pol' THEN 'Pologne'
            -- Finlande
            WHEN 'Fin' THEN 'Finlande'
            -- Norvège
            WHEN 'Norv' THEN 'Norvège'
            WHEN 'Norvege' THEN 'Norvège'
            -- Turquie
            WHEN 'Turquiee' THEN 'Turquie'
            -- Argentine
            WHEN 'Arg' THEN 'Argentine'
            -- Géorgie
            WHEN 'Georgie' THEN 'Géorgie'
            -- Monténégro
            WHEN 'Montenegro' THEN 'Monténégro'
            -- Suède
            WHEN 'Suede' THEN 'Suède'
            -- Grèce
            WHEN 'Grece' THEN 'Grèce'
            -- Brésil
            WHEN 'Bresil' THEN 'Brésil'
            -- Sénégal
            WHEN 'Senegal' THEN 'Sénégal'
            -- Hong-Kong
            WHEN 'Hong Kong' THEN 'Hong-Kong'
            -- Côte d'Ivoire
            WHEN 'Cote Divoire' THEN 'Côte d''Ivoire'
            -- Corée
            WHEN 'Coree' THEN 'Corée'
            -- Égypte
            WHEN 'Egypte' THEN 'Égypte'
            -- Arménie
            WHEN 'Armenie' THEN 'Arménie'
            -- Albanie
            WHEN 'Albanie' THEN 'Albanie'
            -- Algérie
            WHEN 'Algerie' THEN 'Algérie'
            -- États-Unis
            WHEN 'Etats Unis' THEN 'États-Unis'
            ELSE INITCAP(UNACCENT(TRIM(elem->>'country')))
        END AS country_name,
        CAST(elem->>'budget_allocation' AS INTEGER) AS budget_allocation
    FROM {{ ref('stg_films') }},
    UNNEST(country_budget_allocation) AS elem
)
, base_country_id AS (
    SELECT
        movie_id,
        cnc_visa,
        DENSE_RANK() OVER (ORDER BY country_name) AS country_id,
        country_name,
        budget_allocation
    FROM base
)
SELECT
    CONCAT(movie_id, '-', country_id) AS id,
    movie_id,
    cnc_visa,
    country_id,
    country_name,
    budget_allocation
FROM base_country_id