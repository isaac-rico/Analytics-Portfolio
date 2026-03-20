-- Grain: one row per seller, with order and review information

with orders_enriched as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),
reviews as (SELECT * FROM {{ ref('int_olist__order_reviews') }}),
order_items_enriched as (SELECT * FROM {{ ref('int_olist__order_items_enriched') }}),
sellers as (SELECT * FROM {{ ref('stg_olist__sellers') }})

SELECT

    -- seller information
    -- seller unique id, seller city, seller state
    s.seller_id,
    s.seller_city,
    s.seller_state,

    -- order + revenue information
    -- total orders, total revenue, average order value
    count(distinct oi.order_id) as total_orders,
    sum(oi.total_item_value) as total_revenue,
    avg(oi.total_item_value)::numeric(12, 2) as avg_order_value,

    -- review information    
    -- average review score
    avg(oe.avg_review_score)::numeric(10, 2) as avg_review_score,

    -- delivery info
    -- total late deliveries, late delivery rate
    sum(oe.is_late_delivery) as total_late_deliveries,
    ((sum(oe.is_late_delivery) / count(distinct oi.order_id)) * 100)::numeric(12, 2) as late_delivery_rate

from sellers s
left join order_items_enriched oi on s.seller_id = oi.seller_id
left join orders_enriched oe on oi.order_id = oe.order_id
left join reviews r on oe.order_id = r.order_id
group by s.seller_id, s.seller_city, s.seller_state
