-- Monthly revenue from delivered orders.
-- Metabase: line chart
-- X-axis: order_month
-- Y-axis: revenue
SELECT
    DATE_TRUNC('month', orders.order_purchase_date)::DATE AS order_month,
    COUNT(DISTINCT orders.order_id) AS order_count,
    COUNT(items.order_item_key) AS item_count,
    ROUND(SUM(items.price), 2) AS revenue,
    ROUND(SUM(items.freight_value), 2) AS freight_value,
    ROUND(SUM(items.total_item_value), 2) AS customer_spend,
    ROUND(
        SUM(items.price) / NULLIF(COUNT(DISTINCT orders.order_id), 0),
        2
    ) AS average_order_value
FROM analytics.fact_orders AS orders
INNER JOIN analytics.fact_order_items AS items
    ON orders.order_id = items.order_id
WHERE orders.order_status = 'delivered'
GROUP BY DATE_TRUNC('month', orders.order_purchase_date)
ORDER BY order_month;
