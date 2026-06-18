-- Delivery performance by customer state.
-- Use customer_state as the chart category and average_delivery_days as the metric.
SELECT
    customers.customer_state,
    COUNT(orders.order_id) AS delivered_order_count,
    ROUND(AVG(orders.delivery_days), 2) AS average_delivery_days,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY orders.delivery_days
        )::NUMERIC,
        2
    ) AS median_delivery_days,
    ROUND(
        PERCENTILE_CONT(0.9) WITHIN GROUP (
            ORDER BY orders.delivery_days
        )::NUMERIC,
        2
    ) AS p90_delivery_days,
    MIN(orders.delivery_days) AS minimum_delivery_days,
    MAX(orders.delivery_days) AS maximum_delivery_days
FROM analytics.fact_orders AS orders
INNER JOIN analytics.dim_customers AS customers
    ON orders.customer_id = customers.customer_id
WHERE orders.order_status = 'delivered'
  AND orders.delivery_days IS NOT NULL
GROUP BY customers.customer_state
ORDER BY average_delivery_days DESC;
