-- Grain: one row per order item per category per month

with orders_enriched as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),
order_items_enriched as (SELECT * FROM {{ ref('int_olist__order_items_enriched') }}),

monthly_category_perf as (
    SELECT
        date_trunc('month', oe.order_purchase_timestamp) as order_month,
        oe.order_year,
        oe.order_month as order_month_num,
        oi.en_category_name,

        count(distinct oi.order_id) as total_orders,
        count(*) as total_items_sold,
        count(distinct oi.seller_id) as distinct_sellers,
        count(distinct oi.product_id) as distinct_products,

        sum(oi.total_item_value) as total_revenue,
        avg(oi.total_item_value) as avg_item_value,
        avg(oe.total_payment_value) as avg_order_value,

        avg(oe.avg_review_score) as avg_review_score,
        avg(oe.delivery_days) as avg_delivery_days,
        avg(case when oe.is_late_delivery = 1 then 1.0 else 0.0 end) * 100 as late_delivery_rate,
        avg(case when oe.is_delivered = 1 then 1.0 else 0.0 end) * 100 as delivered_order_rate,

        avg(oi.freight_value) as avg_freight_value,
        avg(oi.freight_to_price_ratio) as avg_freight_to_price_ratio

    from order_items_enriched oi
    left join orders_enriched oe on oi.order_id = oe.order_id
    group by 1, 2, 3, 4

)


SELECT
    order_month,
    order_year,
    order_month_num, 
    en_category_name,
    total_orders,
    total_items_sold,
    distinct_sellers,
    distinct_products,
    round(total_revenue, 2) as total_revenue,
    round(avg_item_value, 2) as avg_item_value,
    round(avg_order_value, 2) as avg_order_value,
    round(avg_review_score, 2) as avg_review_score,
    round(avg_delivery_days, 2) as avg_delivery_days,
    round(late_delivery_rate, 2) as late_delivery_rate,
    round(delivered_order_rate, 2) as delivered_order_rate,
    round(avg_freight_value, 2) as avg_freight_value,
    round(avg_freight_to_price_ratio, 2) as avg_freight_to_price_ratio
from monthly_category_perf
order by order_month, total_revenue desc

