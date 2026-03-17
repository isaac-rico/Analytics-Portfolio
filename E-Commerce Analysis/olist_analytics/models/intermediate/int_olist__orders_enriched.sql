with orders as (SELECT * FROM {{ ref('stg_olist__orders') }}),

customers as (SELECT * FROM {{ ref('stg_olist__customers') }}),

payments as (SELECT * FROM {{ ref('int_olist__order_payments') }}),

reviews as (SELECT * FROM {{ ref('int_olist__order_reviews') }})

SELECT 
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    p.total_payment_value,
    p.used_credit_card,
    p.used_voucher,
    p.used_boleto,
    p.used_debit_card,
    p.num_payments,
    p.max_installments,

    r.avg_review_score,
    r.most_recent_review_date,

    case 
        when o.order_estimated_delivery_date is not null 
        and o.order_purchase_timestamp is not null
        then datediff('day', o.order_purchase_timestamp, o.order_estimated_delivery_date)
        else null
    end as estimated_delivery_days,
    case 
        when o.order_delivered_customer_date is not null
        and o.order_purchase_timestamp is not null
        then datediff('day', o.order_purchase_timestamp, o.order_delivered_customer_date)
        else null
    end as delivery_days,
    case 
        when o.order_approved_at is not null
        and o.order_purchase_timestamp is not null
        then datediff('day', o.order_purchase_timestamp, o.order_approved_at)
        else null
    end as approval_days,


    case 
        when o.order_estimated_delivery_date < o.order_delivered_customer_date
        and o.order_delivered_customer_date is not null
        and o.order_estimated_delivery_date is not null
        then 1 
        else 0 
    end as is_late_delivery,

    case when o.order_delivered_customer_date is not null 
        then 1 
        else 0 
    end as is_delivered,

    extract(year from o.order_purchase_timestamp) as order_year,
    extract(month from o.order_purchase_timestamp) as order_month

FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN payments p ON o.order_id = p.order_id
LEFT JOIN reviews r ON o.order_id = r.order_id    