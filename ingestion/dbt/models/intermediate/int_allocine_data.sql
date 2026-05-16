SELECT 
    *,
    CASE
        WHEN LOWER(allocine.genres) = 'animation' THEN 'Animation'
        WHEN LOWER(allocine.genres) IN ('action', 'arts martiaux', 'aventure', 'espionnage', 'judificaire', 'policier', 'thriller', 'western') THEN 'Aventure/Policier/Thriller'
        WHEN LOWER(allocine.genres) IN ('biopic', 'guerre', 'historique') THEN 'Biopic/Guerre/Histoire'
        WHEN LOWER(allocine.genres) IN ('comédie', 'comédie dramatique', 'comédie musicale', 'famille', 'musical', 'romance') THEN 'Comédie/Comédie dramatique'
        WHEN LOWER(allocine.genres) = 'documentaire' THEN 'Documentaire'
        WHEN LOWER(allocine.genres) IN ('drame', 'opéra') THEN 'Drame'
        WHEN LOWER(allocine.genres) IN ('épouvante-horreur', 'expérimental', 'fantastique', 'science fiction') THEN 'Fantastique'
        ELSE 'Autre'
    END AS genre_category,
FROM {{ ref('stg_allocine_data') }}