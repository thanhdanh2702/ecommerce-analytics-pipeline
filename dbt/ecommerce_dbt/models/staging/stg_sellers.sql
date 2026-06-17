SELECT
    NULLIF(TRIM(seller_id), '') AS seller_id,
    NULLIF(TRIM(seller_zip_code_prefix), '') AS seller_zip_code_prefix,
    NULLIF(TRIM(seller_city), '') AS seller_city,
    NULLIF(TRIM(seller_state), '') AS seller_state
FROM {{ source('raw', 'sellers') }}
