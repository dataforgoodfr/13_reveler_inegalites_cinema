{{
  config(materialized = 'view')
}}

SELECT
	ROW_NUMBER() OVER (ORDER BY "VISA") AS movie_id,    
	CAST("VISA" AS INTEGER) AS cnc_visa,
    "TITRE" AS cnc_name,
    "GENRE" AS genre,
    CAST("ANNEE_D_AGREMENT" AS INTEGER) AS cnc_agreement_year,
	CASE
	    -- Si l'année est >= 2013, on multiplie par 1 000 000 (peu importe le format)
	    WHEN CAST("ANNEE_D_AGREMENT" AS INTEGER) >= 2013 THEN
	        CAST(
	            REPLACE(
	                REPLACE(
	                    REPLACE("DEVIS", ' ', ''),
	                    ' ', ''
	                ),
	                ',', '.'
	            ) AS FLOAT
	        ) * 1000000
	    -- Sinon, on ne multiplie pas
	    ELSE
	        CAST(
	            REPLACE(
	                REPLACE(
	                    REPLACE("DEVIS", ' ', ''),
	                    ' ', ''
	                ),
	                ',', '.'
	            ) AS FLOAT
	        )
	END AS budget,
    -- ARRAYS
	STRING_TO_ARRAY(REPLACE("REALISATEUR", ' ', ''), ' / ') AS director,
   	STRING_TO_ARRAY(REPLACE("RANG", ' ', ''), ' / ') AS director_rank,
	STRING_TO_ARRAY(REPLACE("PRODUCTEURS", ' ', ''), ' / ') AS producer,
	STRING_TO_ARRAY(REPLACE("PAYANT", ' ', ''), ' ') AS paid_broadcaster,
	STRING_TO_ARRAY(REPLACE("CLAIR", ' ', ''), ' ') AS free_broadcaster,
	STRING_TO_ARRAY(REPLACE("NATIONALITE", ' ', ''), ' / ') AS country_funder,
    -- BOOLEANS
    CASE
        WHEN "EOF" = 'OUI' THEN TRUE
        WHEN "EOF" = 'NON' THEN FALSE
        ELSE NULL
    END AS has_eof,
    CASE
        WHEN LOWER("BONUS_PARITE_") = 'x' THEN TRUE
        ELSE FALSE
    END AS has_parity_bonus,
    CASE
        WHEN LOWER("ASR") = 'x' THEN TRUE
        ELSE FALSE
    END AS has_asr,
    CASE
        WHEN LOWER("SOFICA") = 'x' THEN TRUE
        ELSE FALSE
    END AS has_sofica,
    CASE
        WHEN LOWER("CREDIT_D_IMPOT") = 'x' THEN TRUE
        ELSE FALSE
    END AS has_tax_credit,
    CASE
        WHEN LOWER("AIDE_REGIONALE") = 'x' THEN TRUE
        ELSE FALSE
    END AS has_regional_funding,
	-- METADATA
	TO_DATE("UPDATED_DATE", 'DD/MM/YYYY') AS updated_date,
    "UPDATED_BY" AS updated_by,
    _airbyte_raw_id AS airbyte_raw_id,
    CAST(_airbyte_generation_id AS INTEGER) AS airbyte_generation_id,
    CAST(_airbyte_extracted_at AS TIMESTAMP)  AS airbyte_extraction_date,
    CAST(_airbyte_meta AS JSON) AS airbyte_meta
FROM {{ source('raw', 'films') }}
WHERE 1 = 1
	AND "UPDATED_DATE" IS NOT NULL
	AND "UPDATED_BY" IS NOT NULL