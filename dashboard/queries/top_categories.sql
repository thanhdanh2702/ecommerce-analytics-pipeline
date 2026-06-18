-- Top 10 product categories by revenue from delivered orders.
-- Metabase: horizontal bar chart
-- X-axis: revenue
-- Y-axis: product_category
SELECT
    COALESCE(
        products.product_category_name_english,
        'unknown'
    ) AS product_category,
    COUNT(DISTINCT items.order_id) AS order_count,
    COUNT(items.order_item_key) AS item_count,
    ROUND(SUM(items.price), 2) AS revenue,
    ROUND(SUM(items.freight_value), 2) AS freight_value,
    ROUND(SUM(items.total_item_value), 2) AS customer_spend
FROM analytics.fact_order_items AS items
INNER JOIN analytics.fact_orders AS orders
    ON items.order_id = orders.order_id
LEFT JOIN analytics.dim_products AS products
    ON items.product_id = products.product_id
WHERE orders.order_status = 'delivered'
GROUP BY COALESCE(
    products.product_category_name_english,
    'unknown'
)
ORDER BY revenue DESC
LIMIT 10;
