SELECT
    NULLIF(TRIM(geolocation_zip_code_prefix), '') AS geolocation_zip_code_prefix,
    NULLIF(TRIM(geolocation_lat), '')::NUMERIC(10, 6) AS geolocation_lat,
    NULLIF(TRIM(geolocation_lng), '')::NUMERIC(10, 6) AS geolocation_lng,
    NULLIF(TRIM(geolocation_city), '') AS geolocation_city,
    NULLIF(TRIM(geolocation_state), '') AS geolocation_state
FROM {{ source('raw', 'geolocation') }}
