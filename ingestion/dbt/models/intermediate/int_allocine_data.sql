SELECT 
    *,
    CASE
        WHEN LOWER(genres) = 'animation' THEN 'Animation'
        WHEN LOWER(genres) IN ('action', 'arts martiaux', 'aventure', 'espionnage', 'judificaire', 'policier', 'thriller', 'western') THEN 'Aventure/Policier/Thriller'
        WHEN LOWER(genres) IN ('biopic', 'guerre', 'historique') THEN 'Biopic/Guerre/Histoire'
        WHEN LOWER(genres) IN ('comédie', 'comédie dramatique', 'comédie musicale', 'famille', 'musical', 'romance') THEN 'Comédie/Comédie dramatique'
        WHEN LOWER(genres) = 'documentaire' THEN 'Documentaire'
        WHEN LOWER(genres) IN ('drame', 'opéra') THEN 'Drame'
        WHEN LOWER(genres) IN ('épouvante-horreur', 'expérimental', 'fantastique', 'science fiction') THEN 'Fantastique'
        ELSE 'Autre'
    END AS genre_category
FROM {{ ref('stg_allocine_data') }}
