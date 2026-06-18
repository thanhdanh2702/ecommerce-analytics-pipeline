-- Payment method usage for delivered orders.
-- Metabase: bar chart or donut chart
-- Category: payment_type
-- Metric: total_payment_value or payment_share_pct
SELECT
    payments.payment_type,
    COUNT(payments.payment_key) AS payment_count,
    COUNT(DISTINCT payments.order_id) AS order_count,
    ROUND(SUM(payments.payment_value), 2) AS total_payment_value,
    ROUND(AVG(payments.payment_value), 2) AS average_payment_value,
    ROUND(AVG(payments.payment_installments), 2) AS average_installments,
    ROUND(
        100.0 * SUM(payments.payment_value)
        / NULLIF(SUM(SUM(payments.payment_value)) OVER (), 0),
        2
    ) AS payment_share_pct
FROM analytics.fact_payments AS payments
INNER JOIN analytics.fact_orders AS orders
    ON payments.order_id = orders.order_id
WHERE orders.order_status = 'delivered'
GROUP BY payments.payment_type
ORDER BY total_payment_value DESC;
