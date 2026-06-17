WITH order_dates AS (
    SELECT
        order_purchase_timestamp::DATE AS date_day
    FROM {{ ref('stg_orders') }}
    WHERE order_purchase_timestamp IS NOT NULL

    UNION ALL

    SELECT
        order_delivered_customer_date::DATE AS date_day
    FROM {{ ref('stg_orders') }}
    WHERE order_delivered_customer_date IS NOT NULL

    UNION ALL

    SELECT
        shipping_limit_date::DATE AS date_day
    FROM {{ ref('stg_order_items') }}
    WHERE shipping_limit_date IS NOT NULL
),

date_bounds AS (
    SELECT
        MIN(date_day) AS min_date,
        MAX(date_day) AS max_date
    FROM order_dates
),

date_spine AS (
    SELECT
        GENERATE_SERIES (
            min_date,
            max_date,
            INTERVAL '1 DAY'
        )::DATE AS date_day
    FROM date_bounds
)

SELECT
    date_day,
    EXTRACT(YEAR FROM date_day)::INTEGER AS year,
    EXTRACT(QUARTER FROM date_day)::INTEGER AS quarter,
    EXTRACT(MONTH FROM date_day)::INTEGER AS month,
    EXTRACT(DAY FROM date_day)::INTEGER AS day_of_month,
    EXTRACT(DOW FROM date_day)::INTEGER AS day_of_week,
    EXTRACT(ISOYEAR FROM date_day)::INTEGER AS iso_year,
    EXTRACT(WEEK FROM date_day)::INTEGER AS iso_week_of_year,
    TO_CHAR(date_day, 'IYYY-IW') AS iso_year_week,
    TO_CHAR(date_day, 'WW')::INTEGER AS calendar_week_of_year,
    TO_CHAR(date_day, 'YYYY-MM') AS year_month,
    TO_CHAR(date_day, 'Month') AS month_name,
    CASE
        WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM date_spine
