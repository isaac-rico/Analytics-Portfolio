SELECT
    ORDER_ID,
    PAYMENT_SEQUENTIAL,
    PAYMENT_TYPE,
    PAYMENT_INSTALLMENTS,
    cast(PAYMENT_VALUE as number(12,2)) as PAYMENT_VALUE
FROM {{ source('olist_raw', 'raw_order_payments') }}

