-- Grain: one row per customer

with orders_enriched as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),

review_count as (
    select 
        order_id, 
        count(review_id) as total_reviews
    from {{ ref('stg_olist__reviews') }}
    group by order_id
)

SELECT

    -- customer information
    -- customer unique id
    oe.customer_unique_id,

    -- spending information
    -- total amount spent, total orders, average order value
    sum(oe.total_payment_value) as total_spent,
    count(distinct oe.order_id) as total_orders,
    avg(oe.total_payment_value)::numeric(12, 2) as avg_order_value,

    -- review information
    -- total reviews, average review score
    sum(rc.total_reviews) as total_reviews,
    avg(oe.avg_review_score)::numeric(10, 2) as avg_review_score,

    -- order information
    -- total late deliveries, late delivery rate
    sum(oe.is_late_delivery) as total_late_deliveries,
    ((sum(oe.is_late_delivery) / count(distinct oe.order_id)) * 100)::numeric(12, 2) as late_delivery_rate

    
from orders_enriched oe
left join review_count rc on oe.order_id = rc.order_id
group by oe.customer_unique_id
    

