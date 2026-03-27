with orders as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),

customer_overview as(
    select
        customer_unique_id,
        min(customer_city) as customer_city,
        min(customer_state) as customer_state,

        min(cast(order_purchase_timestamp as date)) as first_order_date,
        max(cast(order_purchase_timestamp as date)) as last_order_date,

        count(distinct order_id) as total_orders,
        sum(total_payment_value) as total_spent,
        avg(total_payment_value) as avg_order_value,

        sum(coalesce(num_reviews, 0)) as total_reviews,
        avg(avg_review_score) as avg_review_score,

        sum(is_delivered) as total_delivered_orders,
        sum(case when order_status = 'canceled' then 1 else 0 end) as canceled_orders,
        sum(is_late_delivery) as total_late_deliveries,
        avg(case when is_late_delivery = 1 then 1.0 else 0.0 end) * 100 as late_delivery_rate

    from orders
    group by customer_unique_id
)

select 
    customer_unique_id,
    customer_city,
    customer_state,
    first_order_date,
    last_order_date,
    total_orders,
    round(total_spent, 2) as total_spent,
    round(avg_order_value, 2) as avg_order_value,
    total_reviews,
    round(avg_review_score, 2) as avg_review_score,
    total_delivered_orders,
    canceled_orders,
    total_late_deliveries,
    round(late_delivery_rate, 2) as late_delivery_rate

from customer_overview