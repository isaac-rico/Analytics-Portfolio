with orders as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),
order_items as (SELECT * FROM {{ ref('int_olist__order_items_enriched') }}),

seller_perf as (
    select 
        seller_id,
        min(seller_city) as seller_city,
        min(seller_state) as seller_state,

        order_id,
        count(*) as items_sold,
        count(distinct product_id) as distinct_products,
        sum(item_price) as total_item_price,
        sum(freight_value) as total_freight_value,
        sum(total_item_value) as total_order_revenue,
        
    from order_items
    group by seller_id, order_id
),

final as (

    select
        s.seller_id,
        min(s.seller_city) as seller_city,
        min(s.seller_state) as seller_state,

        count(distinct s.order_id) as total_orders,
        sum(s.items_sold) as total_items_sold,
        sum(s.total_order_revenue) as total_revenue,
        avg(s.total_order_revenue) as avg_order_value,

        avg(o.avg_review_score) as avg_review_score,
        avg(o.delivery_days) as avg_delivery_days,
        sum(o.is_delivered) as delivered_orders,
        sum(case when o.order_status = 'canceled' then 1 else 0 end) as canceled_orders,
        sum(o.is_late_delivery) as total_late_deliveries,
        avg(case when o.is_late_delivery = 1 then 1.0 else 0.0 end) * 100 as late_delivery_rate,

        min(cast(o.order_purchase_timestamp as date)) as first_order_date,
        max(cast(o.order_purchase_timestamp as date)) as most_recent_order_date

    from seller_perf s
    left join orders o
        on s.order_id = o.order_id
    group by s.seller_id

)

select
    seller_id,
    seller_city,
    seller_state,
    first_order_date,
    most_recent_order_date,
    total_orders,
    total_items_sold,
    round(total_revenue, 2) as total_revenue,
    round(avg_order_value, 2) as avg_order_value,
    round(avg_review_score, 2) as avg_review_score,
    round(avg_delivery_days, 2) as avg_delivery_days,
    delivered_orders,
    canceled_orders,
    total_late_deliveries,
    round(late_delivery_rate, 2) as late_delivery_rate
from final