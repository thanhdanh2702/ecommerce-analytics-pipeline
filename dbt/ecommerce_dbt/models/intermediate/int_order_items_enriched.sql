WITH order_items AS (
    SELECT
        *
    FROM {{ ref('stg_order_items') }}
),

products AS (
    SELECT
        *
    FROM {{ ref('stg_products') }}
),

sellers AS (
    SELECT
        *
    FROM {{ ref('stg_sellers') }}
),

product_category_name_translation AS (
    SELECT
        *
    FROM {{ ref('stg_product_category_name_translation') }}
)

SELECT
    order_items.order_id,
    order_items.order_item_id,
    order_items.product_id,
    products.product_category_name,
    prod_trans.product_category_name_english,
    products.product_name_length,
    products.product_description_length,
    products.product_photos_qty,
    products.product_weight_g,
    products.product_length_cm,
    products.product_height_cm,
    products.product_width_cm,
    order_items.seller_id,
    sellers.seller_zip_code_prefix,
    sellers.seller_city,
    sellers.seller_state,
    order_items.shipping_limit_date,
    order_items.price,
    order_items.freight_value
FROM order_items
LEFT JOIN products
    ON order_items.product_id = products.product_id
LEFT JOIN sellers
    ON order_items.seller_id = sellers.seller_id
LEFT JOIN product_category_name_translation AS prod_trans
    ON products.product_category_name = prod_trans.product_category_name