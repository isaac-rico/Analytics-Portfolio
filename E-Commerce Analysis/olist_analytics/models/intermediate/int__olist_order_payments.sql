with payments as (

    select * from {{ ref('stg_olist__payments') }}

)

select 
    order_id,
    payment_type,
    sum(payment_value) as total_payment_value,
    count(*) as num_payments,
    max(payment_installments) as max_installments
from payments
group by 1