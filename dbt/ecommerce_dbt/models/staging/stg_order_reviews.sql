SELECT
    NULLIF(TRIM(review_id), '') AS review_id,
    NULLIF(TRIM(order_id), '') AS order_id,
    NULLIF(TRIM(review_score), '')::INTEGER AS review_score,
    NULLIF(TRIM(review_comment_title), '') AS review_comment_title,
    NULLIF(TRIM(review_comment_message), '') AS review_comment_message,
    NULLIF(TRIM(review_creation_date), '')::TIMESTAMP AS review_creation_date,
    NULLIF(TRIM(review_answer_timestamp), '')::TIMESTAMP AS review_answer_timestamp
FROM {{ source('raw', 'order_reviews') }}
