SELECT
	CAST(visa_number AS INTEGER) AS cnc_visa,	
	CAST(allocine_visa_number AS INTEGER) AS allocine_visa,
	CAST(allocine_id AS INTEGER) AS allocine_id,
	--
	original_name AS cnc_name,
	allocine_title AS allocine_name, 
	--
	CAST(cnc_agrement_year AS INTEGER) AS cnc_agreement_year
	CAST(release_date AS DATE) AS release_date, 
	CAST(duration_minutes AS INTEGER) AS duration_mn, 
	--
	search_url AS search_url, 
	source_url AS source_url, 
	allocine_url AS allocine_url, 
	trailer_url AS trailer_url, 
	--
	genres, 
	direction, 
	casting, 
	screenwriters, 
	production, 
	technical_team, 
	soundtrack, 
	distribution, 
	companies, 
	-- METADATA
	run_id AS run_id, 
	CAST(extracted_at AS TIMESTAMP) AS extracted_ts,
	CAST(source_record_id AS INTEGER) AS source_record_id, 
	match_strategy AS match_strategy, 
	scrape_status AS scrapping_status, 
	error_hash AS record_hash
FROM {{ source('raw', 'allocine_data') }}
WHERE source_record_id IS NOT NULL
