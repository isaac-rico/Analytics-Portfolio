
-- average revenue per year
select
	year,
	avg(revenue_usd) as revenue
from apple_dataset
group by YEAR
order by revenue DESC;

-- average revenue per quarter
select 
	quarter,
	year, 
	avg(revenue_usd) as revenue
from apple_dataset
group by year, quarter
order by quarter DESC;

-- average revenue per region/year
select 
	region,
	avg(revenue_usd) as revenue,
	year
from apple_dataset
group by region, year
order by revenue desc;

-- total revenue per region per YEAR
select
	region,
	SUM(revenue_usd) as revenue,
	YEAR
from apple_dataset
group by region, YEAR
order by revenue desc;

-- avg revenue per region
select 
	region,
	avg(revenue_usd) as revenue
from apple_dataset
group by region
order by revenue desc;

-- total revenue per region
select
	region,
	SUM(revenue_usd) as revenue
from apple_dataset
group by region
order by revenue desc;

----------------- template for region specifics ---------------

-- revenue per year/quarter
select
	region,
	sum(revenue_usd) as revenue,
	year,
	quarter
from apple_dataset
where region = 'Europe' -- <- replace with wanted region
group by quarter, region, YEAR
order by year desc;

-- average revenue per year
select
	region,
	avg(revenue_usd) as revenue,
	year
from apple_dataset
where region = 'Europe' -- <- replace with wanted region
group by region, YEAR
order by year desc;

---------------- product analysis ----------------------

-- revenue per product by year
select
	product_name,
	sum(revenue_usd) as revenue,
	year
from apple_dataset
group by product_name, year
order by revenue desc;

-- revenue per category by year
select
	category, 
	sum(revenue_usd) as revenue,
	year
from apple_dataset
group by category, year
order by revenue desc;

-- top 3 producs in the year 2024
select 
	product_name,
	sum(revenue_usd) as revenue
from apple_dataset
where year = '2024' -- and product_name not like '%Mac%' -- <-- that aren't macs lol
group by product_name, year
order by revenue desc limit 3; -- if you want the bottom 3, order by *asc*

-- airpod trends within the last 2 years (quarterly analysis)
select 
	product_name,
	sum(revenue_usd)::NUMERIC(12, 2) as revenue,
	AVG(revenue_usd)::numeric(12, 2) as average,
	year, quarter
from apple_dataset
where product_name LIKE '%AirPods%'
	and year >= EXTRACT(year from CURRENT_DATE) - 2
group by product_name, quarter, year
order by revenue desc;

-- mac trends within the last 2 years (semi-annual analysis)
select 
	product_name,
	sum(revenue_usd) as revenue,
	avg(revenue_usd) as average,
	case -- case / end as to establish semi-annual
		when quarter in ('Q1', 'Q2') then 'H1'
		when quarter in ('Q3', 'Q4') then 'H2'
	end as half_year,
	year
from apple_dataset
-- uncomment for product specific
--where product_name ILIKE '%mac pro%'
where product_name LIKE '%Mac%'
	and year >- EXTRACT(year from CURRENT_DATE) - 2
group by product_name, half_year, year
order by revenue DESC;

-- iphone trends in the last 3 years per region
select 
	region,
	product_name,
	sum(revenue_usd)::numeric(12, 2) as revenue,
	avg(revenue_usd)::numeric(12, 2) as average,
	year
from apple_dataset
where product_name ILIKE '%iphone%'
group by region, product_name, year
order by revenue desc;	

-- top iphones per region
SELECT 
	region,
	product_name,
	revenue
FROM (
    SELECT
        region,
        product_name,
        sum(revenue_usd)::NUMERIC(12, 2) as revenue,
        RANK() OVER (PARTITION BY region ORDER BY SUM(revenue_usd) DESC) AS rnk -- rank tag
        -- we over/partition by region since we want to keep the total revenue per region, then we associate by product name
    FROM apple_dataset
    where product_name like '%iPhone%'
    group by region, product_name
) AS sub
WHERE rnk = 1
ORDER BY region;

-- top product per country
SELECT
	region,
	product_name, 
	revenue
from (
	SELECT
		region,
		product_name,
		sum(revenue_usd)::numeric(12, 2) as revenue,
		rank() over (PARTITION BY region ORDER by sum(revenue_usd) desc) as rnk
	from apple_dataset
	group by region, product_name
) as subq
where rnk <= 3
order by region;


-- NOTE: TOP N PER CATEGORY 
-- 			SUBQUERY WITH RANK() OVER (PARTITION BY *CATEGORY* ORDER BY *AGGREGATE* DESC(TOP)/ASC(BOT)) AS RNK
