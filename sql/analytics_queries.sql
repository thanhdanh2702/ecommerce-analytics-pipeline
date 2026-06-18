SET search_path TO analytics;

-- 1. Monthly revenue
-- Revenue is the product price from delivered orders; freight is reported separately.
SELECT
    dates.year_month,
    COUNT(DISTINCT orders.order_id) AS order_count,
    COUNT(items.order_item_key) AS item_count,
    ROUND(SUM(items.price), 2) AS revenue,
    ROUND(SUM(items.freight_value), 2) AS freight_value,
    ROUND(SUM(items.total_item_value), 2) AS customer_spend
FROM analytics.fact_order_items AS items
INNER JOIN analytics.fact_orders AS orders
    ON items.order_id = orders.order_id
INNER JOIN analytics.dim_dates AS dates
    ON orders.order_purchase_date = dates.date_day
WHERE orders.order_status = 'delivered'
GROUP BY dates.year_month
ORDER BY dates.year_month;


-- 2. Revenue by product category
SELECT
    COALESCE(products.product_category_name_english, 'unknown') AS product_category,
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
GROUP BY COALESCE(products.product_category_name_english, 'unknown')
ORDER BY revenue DESC;


-- 3. Top sellers by revenue
SELECT
    sellers.seller_id,
    sellers.seller_city,
    sellers.seller_state,
    COUNT(DISTINCT items.order_id) AS order_count,
    COUNT(items.order_item_key) AS item_count,
    ROUND(SUM(items.price), 2) AS revenue,
    ROUND(SUM(items.freight_value), 2) AS freight_value
FROM analytics.fact_order_items AS items
INNER JOIN analytics.fact_orders AS orders
    ON items.order_id = orders.order_id
INNER JOIN analytics.dim_sellers AS sellers
    ON items.seller_id = sellers.seller_id
WHERE orders.order_status = 'delivered'
GROUP BY
    sellers.seller_id,
    sellers.seller_city,
    sellers.seller_state
ORDER BY revenue DESC
LIMIT 20;


-- 4. Order count by customer state
SELECT
    customers.customer_state,
    COUNT(orders.order_id) AS total_orders,
    COUNT(orders.order_id) FILTER (
        WHERE orders.order_status = 'delivered'
    ) AS delivered_orders,
    COUNT(orders.order_id) FILTER (
        WHERE orders.order_status = 'canceled'
    ) AS canceled_orders,
    ROUND(
        100.0
        * COUNT(orders.order_id) FILTER (
            WHERE orders.order_status = 'delivered'
        )
        / NULLIF(COUNT(orders.order_id), 0),
        2
    ) AS delivery_rate_pct
FROM analytics.fact_orders AS orders
INNER JOIN analytics.dim_customers AS customers
    ON orders.customer_id = customers.customer_id
GROUP BY customers.customer_state
ORDER BY total_orders DESC;


-- 5. Payment value by payment type
SELECT
    payments.payment_type,
    COUNT(payments.payment_key) AS payment_count,
    COUNT(DISTINCT payments.order_id) AS order_count,
    ROUND(SUM(payments.payment_value), 2) AS total_payment_value,
    ROUND(AVG(payments.payment_value), 2) AS average_payment_value,
    ROUND(AVG(payments.payment_installments), 2) AS average_installments
FROM analytics.fact_payments AS payments
INNER JOIN analytics.fact_orders AS orders
    ON payments.order_id = orders.order_id
WHERE orders.order_status = 'delivered'
GROUP BY payments.payment_type
ORDER BY total_payment_value DESC;


-- 6. Average review score by product category
-- DISTINCT prevents an order with multiple items in one category from duplicating its review.
WITH order_categories AS (
    SELECT DISTINCT
        items.order_id,
        COALESCE(products.product_category_name_english, 'unknown') AS product_category
    FROM analytics.fact_order_items AS items
    LEFT JOIN analytics.dim_products AS products
        ON items.product_id = products.product_id
)

SELECT
    categories.product_category,
    COUNT(*) FILTER (
        WHERE orders.average_review_score IS NOT NULL
    ) AS reviewed_order_count,
    ROUND(AVG(orders.average_review_score), 2) AS average_review_score
FROM order_categories AS categories
INNER JOIN analytics.fact_orders AS orders
    ON categories.order_id = orders.order_id
WHERE orders.order_status = 'delivered'
GROUP BY categories.product_category
ORDER BY average_review_score DESC NULLS LAST;


-- 7. Delivery time by customer state
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
    MIN(orders.delivery_days) AS minimum_delivery_days,
    MAX(orders.delivery_days) AS maximum_delivery_days
FROM analytics.fact_orders AS orders
INNER JOIN analytics.dim_customers AS customers
    ON orders.customer_id = customers.customer_id
WHERE orders.order_status = 'delivered'
  AND orders.delivery_days IS NOT NULL
GROUP BY customers.customer_state
ORDER BY average_delivery_days;
 