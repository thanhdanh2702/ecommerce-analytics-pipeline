WITH payments AS (
    SELECT
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value
    FROM {{ ref('stg_order_payments') }}
)

SELECT
    order_id || '-' || payment_sequential::TEXT AS payment_key,
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM payments
