WITH base AS (
    SELECT
        matching.film_id,
        allocine.cnc_visa,
        allocine.allocine_id,
        UNNEST(allocine.genres) AS genre
    FROM {{ ref('stg_allocine_films') }} AS allocine
    LEFT JOIN {{ ref('stg_cnc_films') }} AS cnc
        ON allocine.cnc_visa = cnc.cnc_visa
    LEFT JOIN {{ ref('stg_id_matching') }} AS matching
        ON allocine.cnc_visa = matching.cnc_visa
),
agg_genre AS (
    SELECT
        film_id,
        cnc_visa,
        allocine_id,
        CASE
            WHEN LOWER(genre) = 'animation' THEN 'Animation'
            WHEN LOWER(genre) IN ('action', 'arts martiaux', 'aventure', 'espionnage', 'judificaire', 'policier', 'thriller', 'western') THEN 'Aventure/Policier/Thriller'
            WHEN LOWER(genre) IN ('biopic', 'guerre', 'historique') THEN 'Biopic/Guerre/Histoire'
            WHEN LOWER(genre) IN ('comédie', 'comédie dramatique', 'comédie musicale', 'famille', 'musical', 'romance') THEN 'Comédie/Comédie dramatique'
            WHEN LOWER(genre) = 'documentaire' THEN 'Documentaire'
            WHEN LOWER(genre) IN ('drame', 'opéra') THEN 'Drame'
            WHEN LOWER(genre) IN ('épouvante-horreur', 'expérimental', 'fantastique', 'science fiction') THEN 'Fantastique'
            ELSE 'Autre'
        END AS genre_name
    FROM base
)
SELECT
    film_id,
    cnc_visa,
    allocine_id,
    MD5(CAST(genre_name AS TEXT))::UUID as genre_id,
    genre_name
FROM agg_genre