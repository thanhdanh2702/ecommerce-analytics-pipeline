WITH customers AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    FROM {{ ref('stg_customers') }}
),

customer_orders AS (
    SELECT
        customer_id,
        COUNT(order_id) AS total_orders,
        SUM(total_payment_value) AS lifetime_payment_value,
        MIN(order_purchase_timestamp) AS first_order_at,
        MAX(order_purchase_timestamp) AS last_order_at
    FROM {{ ref('int_orders_enriched') }}
    GROUP BY customer_id
)

SELECT
    customers.customer_id,
    customers.customer_unique_id,
    customers.customer_zip_code_prefix,
    customers.customer_city,
    customers.customer_state,
    COALESCE(customer_orders.total_orders, 0) AS total_orders,
    COALESCE(customer_orders.lifetime_payment_value, 0) AS lifetime_payment_value,
    customer_orders.first_order_at,
    customer_orders.last_order_at
FROM customers
LEFT JOIN customer_orders
    ON customers.customer_id = customer_orders.customer_id