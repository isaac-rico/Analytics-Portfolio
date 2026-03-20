-- Grain: one row per month

with orders_enriched as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),
order_items_enriched as (SELECT * FROM {{ ref('int_olist__order_items_enriched') }}),

monthly_sales as (
    select 
        date_trunc('month', order_purchase_timestamp) as month,
        date_trunc('year', order_purchase_timestamp) as year,
        sum(total_payment_value) as total_revenue,
        count(distinct order_id) as total_orders,
        avg(total_payment_value)::numeric(12, 2) as avg_order_value,
        avg(delivery_days) as avg_delivery_days,
        avg(is_late_delivery) * 100 as late_delivery_rate
    from orders_enriched
    group by 1, 2
)

SELECT
    month,
    year,
    total_orders,
    round(total_revenue, 2) as total_revenue,
    round(avg_order_value, 2) as avg_order_value,
    round(avg_delivery_days, 2) as avg_delivery_days,
    round(late_delivery_rate, 2) as late_delivery_rate
from monthly_sales
order by month, year