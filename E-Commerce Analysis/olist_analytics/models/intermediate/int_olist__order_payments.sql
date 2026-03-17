-- Grain of this model: one row per order, with payment information

with payments as (

    select * from {{ ref('stg_olist__payments') }}

)

select 
    order_id,
    sum(payment_value) as total_payment_value,
    count(*) as num_payments,
    max(payment_installments) as max_installments,
    -- flags for each payment type, since there can be multiple payments of differnt types per order -- keeps grain
    max(case when payment_type = 'credit_card' then 1 else 0 end) as used_credit_card,
    max(case when payment_type = 'voucher' then 1 else 0 end) as used_voucher,
    max(case when payment_type = 'boleto' then 1 else 0 end) as used_boleto,
    max(case when payment_type = 'debit_card' then 1 else 0 end) as used_debit_card
from payments
group by order_id