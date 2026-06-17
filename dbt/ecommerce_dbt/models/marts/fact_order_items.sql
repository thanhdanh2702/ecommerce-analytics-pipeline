WITH order_items AS (
    SELECT
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        freight_value
    FROM {{ ref('int_order_items_enriched') }}
)

SELECT
    order_id || '-' || order_item_id::TEXT AS order_item_key,
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    shipping_limit_date::DATE AS shipping_limit_date_day,
    price,
    freight_value,
    price + freight_value AS total_item_value
FROM order_items
