
select 
    category,
    sum(revenue_usd) as revenue,
    year
from apple_dataset
group by category, year
order by revenue desc;


