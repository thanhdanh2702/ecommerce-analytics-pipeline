-- Distribution of orders by status.
-- Metabase: donut chart
-- Category: order_status
-- Metric: order_count
SELECT
    orders.order_status,
    COUNT(orders.order_id) AS order_count,
    ROUND(
        100.0 * COUNT(orders.order_id)
        / NULLIF(SUM(COUNT(orders.order_id)) OVER (), 0),
        2
    ) AS order_share_pct
FROM analytics.fact_orders AS orders
GROUP BY orders.order_status
ORDER BY order_count DESC;
