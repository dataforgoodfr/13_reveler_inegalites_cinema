SELECT
    cnc_visa,
    cnc_name,
    allocine_id,
    mubi_id,
    tmdb_id
FROM {{ ref('stg_id_matching') }}