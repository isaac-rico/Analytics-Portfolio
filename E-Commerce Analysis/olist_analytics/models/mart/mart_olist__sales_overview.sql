-- Grain: one row per order

with orders_enriched as (SELECT * FROM {{ ref('int_olist__orders_enriched') }}),
order_items_enriched as (SELECT * FROM {{ ref('int_olist__order_items_enriched') }}),

order_items as (
    select 
        order_id,
        count(*) as item_count,
        count(distinct product_id) as distinct_product_count,
        count(distinct seller_id) as distinct_seller_count,
        sum(item_price) as total_item_price,
        sum(freight_value) as total_freight_value,
        sum(total_item_value) as total_item_value,
    from order_items_enriched
    group by order_id
),

-- category ranks
category_rank as (
    select
        order_id,
        en_category_name,
        sum(total_item_value) as category_revenue,
        rank() over (
            partition by order_id order by category_revenue desc
            ) as rnk
    from order_items_enriched
    group by order_id, en_category_name
),

-- top cateogry
top_category as (
    select
        order_id,
        en_category_name as top_category
    from category_rank
    where rnk = 1
)


SELECT 
    -- order information
    oe.order_id,
    oe.customer_id,
    oe.customer_unique_id,
    oe.order_status,
    oe.order_purchase_timestamp,
    cast(oe.order_purchase_timestamp as date) as order_date,
    oe.order_year,
    oe.order_month,
    oe.customer_city,
    oe.customer_state,
    oe.total_payment_value,
    oe.num_payments,
    oe.max_installments,
    oe.used_credit_card,
    oe.used_voucher,
    oe.used_boleto,
    oe.used_debit_card,
    oe.avg_review_score,
    oe.most_recent_review_date,
    oe.estimated_delivery_days,
    oe.delivery_days,
    oe.approval_days,
    oe.is_late_delivery,
    oe.is_delivered,

    -- order item information
    -- coalesce to 0 if null
    coalesce(oi.item_count, 0) as item_count,
    coalesce(oi.distinct_product_count, 0) as distinct_product_count,
    coalesce(oi.distinct_seller_count, 0) as distinct_seller_count,
    coalesce(oi.total_item_price, 0) as total_item_price,
    coalesce(oi.total_freight_value, 0) as total_freight_value,
    coalesce(oi.total_item_value, 0) as total_item_value,
    tc.top_category

from orders_enriched oe
left join order_items oi
    on oe.order_id = oi.order_id
left join top_category tc
    on oe.order_id = tc.order_id