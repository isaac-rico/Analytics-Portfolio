-- Grain: one row per order item, with product and seller info

with order_items as (SELECT * FROM {{ref('stg_olist__order_items')}}),
products as (SELECT * FROM {{ref('stg_olist__products')}}),
sellers as (SELECT * FROM {{ref('stg_olist__sellers')}}),
product_category_name as (SELECT * FROM {{ref('stg_olist__product_category_name')}})

SELECT
    -- order item information
    o.order_id,
    o.order_item_id,
    o.product_id,
    o.seller_id,
    o.price as item_price,
    o.freight_value,

    -- product information (put in english)
    pc.en_category_name,

    -- seller information
    s.seller_id,
    s.seller_city,
    s.seller_state,

    -- pricing information
    o.price + o.freight_value as total_item_value,
    (((o.freight_value / o.price) * 100)::numeric(12,2)) as freight_to_price_ratio

from order_items o
left join products p on o.product_id = p.product_id
left join sellers s on o.seller_id = s.seller_id
left join product_category_name pc on p.product_category_name = pc.pt_category_name
