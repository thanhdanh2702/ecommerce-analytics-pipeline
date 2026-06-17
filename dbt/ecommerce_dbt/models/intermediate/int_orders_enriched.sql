WITH orders AS (
    SELECT
        *
    FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT
        *
    FROM {{ ref('stg_customers') }}
),

payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment_value,
        COUNT(*) AS payment_count
    FROM {{ ref('stg_order_payments') }}
    GROUP BY order_id
),

reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS average_review_score,
        COUNT(*) AS review_count
    FROM {{ ref('stg_order_reviews') }}
    GROUP BY order_id
)

SELECT
    ord.order_id,
    ord.customer_id,
    cus.customer_unique_id,
    cus.customer_city,
    cus.customer_state,
    ord.order_status,
    ord.order_purchase_timestamp,
    ord.order_delivered_customer_date,
    pay.total_payment_value,
    pay.payment_count,
    rev.average_review_score,
    rev.review_count
FROM orders AS ord
LEFT JOIN customers AS cus
    ON ord.customer_id = cus.customer_id
LEFT JOIN payments AS pay
    ON ord.order_id = pay.order_id
LEFT JOIN reviews AS rev
    ON ord.order_id = rev.order_id