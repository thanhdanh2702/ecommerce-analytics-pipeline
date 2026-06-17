SELECT
    NULLIF(TRIM(order_id), '') AS order_id,
    NULLIF(TRIM(payment_sequential), '')::INTEGER AS payment_sequential,
    NULLIF(TRIM(payment_type), '') AS payment_type,
    NULLIF(TRIM(payment_installments), '')::INTEGER AS payment_installments,
    NULLIF(TRIM(payment_value), '')::NUMERIC(12, 2) AS payment_value
FROM {{ source('raw', 'order_payments') }}
