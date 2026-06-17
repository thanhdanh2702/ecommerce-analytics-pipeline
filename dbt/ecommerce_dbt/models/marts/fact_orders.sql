WITH orders AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_delivered_customer_date,
        total_payment_value,
        payment_count,
        average_review_score,
        review_count
    FROM {{ ref('int_orders_enriched') }}
)

SELECT
    order_id,
    customer_id,
    order_status,

    order_purchase_timestamp,
    order_purchase_timestamp::DATE AS order_purchase_date,

    order_delivered_customer_date AS order_delivered_customer_timestamp,
    order_delivered_customer_date::DATE AS order_delivered_customer_date,

    total_payment_value,
    payment_count,
    average_review_score,
    review_count,

    CASE
        WHEN order_delivered_customer_date IS NOT NULL
        THEN EXTRACT(DAY FROM order_delivered_customer_date - order_purchase_timestamp)
    END AS delivery_days
FROM orders