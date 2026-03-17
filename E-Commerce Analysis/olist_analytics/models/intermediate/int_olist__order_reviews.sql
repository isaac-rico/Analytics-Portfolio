-- Grain of this model: one row per order, with review information

with reviews as (SELECT * FROM {{ ref('stg_olist__reviews') }})

SELECT 
    order_id,
    avg(review_score) as avg_review_score,
    count(*) as num_reviews,
    max(review_creation_date) as most_recent_review_date
FROM reviews
GROUP BY order_id