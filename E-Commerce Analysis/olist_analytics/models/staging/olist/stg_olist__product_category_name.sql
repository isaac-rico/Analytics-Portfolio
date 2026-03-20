SELECT
    C1 as pt_category_name,
    C2 as en_category_name,
FROM {{ source('olist_raw', 'raw_product_category_name') }}