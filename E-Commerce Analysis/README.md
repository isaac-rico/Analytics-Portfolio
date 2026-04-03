# E-Commerce Analysis of Olist Store Data

## TL;DR
[Dashboards](#final-mart-models-and-dashboards)
- Built an end-to-end E-Commerce analytics project using **dbt, Snowflake, and Apache Superset**
- Modeled raw Olist marketplace data into reusable intermediate models and dashboard-ready marts
- Created a dashboard suite covering **executive sales overview, category performance, seller performance, and customer behavior
- Designed analytics-ready tables at different grains to support KPI reporting, trend analysis, and performance breakdowns
- Used a layered transformation approach to separate staging, intermediate logic, and mart-level reporting

---

## Project Overview

This project analyzes the **Olist Brazilian E-commerce dataset** to create a modern analytics workflow for reporting and business intelligence.

Using **dbt for transformation, Snowflake for warehousing, and Apache Superset for dashboarding**, I built a set of reusable data models and interactive dashboards to answer key e-commerce questions around:

- sales performance
- category trends
- customer behavior
- seller performance

Unlike a single dashboard-only project, this project focuses on the full analytics engineering pipeline: taking raw e-commerce data, transforming it into clean business-ready models, and exposing those models through dashboard views tailored to different business questions.

--- 

## Skills Demonstrated
- analytics engineering
- SQL data modeling
- dbt transformations
- KPI development
- dashboard development
- dimensional thinking and grain design
- business performance analysis
- data visualization
- metric design for e-commerce reporting

--- 

## Tools and & Technologies

- **Transformation:** dbt
- **Warehouse:** Snowflake
- **Dashboarding:** Apache Superset
- **Querying and Modeling:** SQL

---

## Dataset
**Source:** Kaggle - [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)

**Core fields used:**
- orders
- order items
- customers
- sellers
- products
- payments
- reviews

---

## Project Pipeline

```
Olist Dataset
     ↓
dbt Staging Models
     ↓
dbt Intermediate Models 
     ↓
dbt Mart Models
     ↓
Snowflake Analytics Tables
     ↓
Apache Superset Dashboards
```

---

## Objective

Build a reporting-ready ecommerce analytics stack that can answer:
- How is revenue trending over time?
- Which states and product categories drive the most revenue?
- What does customer purchasing behavior look like?
- Which sellers generate the most revenue and orders?

---

## Key Questions
- How much total revenue and order volume does the business generate?
- How does revenue change over time?
- Which categories contribute the most revenue?
- Which categories show stronger or weaker customer satisfaction?
- Are most customers one-time buyers or repeat buyers?
- Which sellers drive the most revenue?
- Which states contribute the most customer and seller activity?
- Where is late delivery risk highest?

---

## Data Modeling Approach
This project follows a layered analytics engineering structure:

```
staging → intermediate → marts → dashboards
```

### Staging Models
The staging layer was built to clean, preprocess, and standardize the raw data.

Example from [stg_olist__payments.sql](https://github.com/isaac-rico/Analytics-Portfolio/blob/74e1d095ece2fba13f0e67945740923e506ef210/E-Commerce%20Analysis/olist_analytics/models/staging/olist/stg_olist__payments.sql):

```
SELECT
    ORDER_ID,
    PAYMENT_SEQUENTIAL,
    PAYMENT_TYPE,
    PAYMENT_INSTALLMENTS,
    cast(PAYMENT_VALUE as number(12,2)) as PAYMENT_VALUE
FROM {{ source('olist_raw', 'raw_order_payments') }}
```
### Intermediate Models
The intermediate layer was built to handle reusable business logic before dashboard-facing marts are created.

Examples:

[int_olist__orders_enriched.sql](https://github.com/isaac-rico/Analytics-Portfolio/blob/74e1d095ece2fba13f0e67945740923e506ef210/E-Commerce%20Analysis/olist_analytics/models/intermediate/int_olist__orders_enriched.sql)

**Grain:** one row per order

This model enriches order-level data with:
- customer identifiers
- order status
- payment totals
- review metrics
- delivery timing metrics
- late delivery flags
- time fields for reporting

[int_olist__order_items_enriched.sql](https://github.com/isaac-rico/Analytics-Portfolio/blob/74e1d095ece2fba13f0e67945740923e506ef210/E-Commerce%20Analysis/olist_analytics/models/intermediate/int_olist__order_items_enriched.sql)

**Grain:** one row per order item

This model enriches item-level data with:
- product identifiers
- seller info
- category name (translated to English from Portuguese)
- item price
- freight value
- total item value
- freight-to-price ratio

```
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
```

--- 

## Final Mart Models and Dashboards
The mart layer was built to create analytics-ready tables for dashboarding


### Olist Ecommerce Master Dashboard

Mart used: [mart_olist__sales_overview.sql](https://github.com/isaac-rico/Analytics-Portfolio/blob/74e1d095ece2fba13f0e67945740923e506ef210/E-Commerce%20Analysis/olist_analytics/models/mart/mart_olist__sales_overview.sql)

**Grain:** one row per order

This is the primary reporting model for executive sales monitoring. 
Users can filter by time range, category, and state.

Used for:
- total revenue
- total orders
- average order value
- late delivery rate
- revenue trends
- revenue by state
- revenue by category

<img width="2252" height="1318" alt="olist-master-db" src="https://github.com/user-attachments/assets/9118b81c-8d22-4e86-afe6-16ab058ff185" />

### Olist Category Performance Dashboard

Mart used: [mart_olist__category_performance.sql](https://github.com/isaac-rico/Analytics-Portfolio/blob/74e1d095ece2fba13f0e67945740923e506ef210/E-Commerce%20Analysis/olist_analytics/models/mart/mart_olist__category_performance.sql)

**Grain:** one row per order item per category per month

Built for category-level performance tracking.
Users can filter by category.

Used for:
- revenue by category
- total orders by category
- review score by category
- late delivery rate by category
- category revenue trends over time

<img width="2261" height="1321" alt="olist-category-db" src="https://github.com/user-attachments/assets/e66814ad-c6fa-42dc-843d-6684a3e0f505" />

### Olist Customer Overview Dashboard 

Mart used: [mart_olist__customer_overview.sql](https://github.com/isaac-rico/Analytics-Portfolio/blob/74e1d095ece2fba13f0e67945740923e506ef210/E-Commerce%20Analysis/olist_analytics/models/mart/mart_olist__customer_overview.sql)

**Grain:** one row per customer

Built for customer behavior and value analysis.
Users can filter by first order date, last order date, customer state, and total orders.

Used for:
- total customer spend
- total orders per customer
- average order value
- late delivery rate
- geographic customer analysis

<img width="2261" height="1323" alt="olist-customer-db" src="https://github.com/user-attachments/assets/237e2928-34ad-40d7-80e1-4f5b970e4cf0" />

### Olist Seller Performance Dashboard

**Grain:** one row per seller

Built for seller performance analysis.
Users can filter by seller and state.

Used for:
- seller revenue
- seller order volume
- average seller revenue
- review score
- late delivery rate
- seller geography

<img width="2253" height="1315" alt="olist-seller-db" src="https://github.com/user-attachments/assets/9fbf48a0-c62d-408f-860f-905add997b54" />

---


## SQL / Modeling Notes

SQL was used throughout the project to shape reusable reporting models rather than writing queries for dashboards exclusively.

A key design decision in this project was to use correct **grains** for each model:
- order-level grain for sales overview/executive level reporting
- category-month grain for category trend analysis
- customer-level grain for customer behavior and analysis
- seller-level grain for marketplace performance analysis

This helped to keep dashboard queriying simpler and reduced the need to rebuild complex logic inside Superset.

Helpful resource about dbt and snowflake modeling: [DBT Models in Snowflake: Best Practices for Staging, Intermediate, and Mart Layers](https://medium.com/@manik.ruet08/dbt-models-in-snowflake-best-practices-for-staging-intermediate-and-mart-layers-2abf37d08f65)

---

## Key Insights

- Revenue is concentrated in a relatively small number of states and product categories
- Customer ordering behavior is heavily skewed toward lower order counts, indicating that most customers are one-time buyers
- Seller revenue is unevenly distributed, with a small number of sellers contributing a large share of marketplace revenue. 
- Executive KPIs such as revenue, order volume, and average order value can be monitored from a single order-grain reporting mart.

--- 

## Future Improvements

- Adding dbt tests and documentation across all marts
- publishing dbt docs
- expanding into fulfillment and delivery analysis
- adding customer segmentation logic
- adding seller performance scoring or benchmarking
- improving dashboard interactivity

--- 

## Conclusion

This project demonstrates how a modern analytics stack can be used to turn raw e-commerce marketplace data into clean, business-ready reporting assets.

By combining dbt, Snowflake, and Apache Superset, I built a full pipeline that supports executive KPI reporting, category performance tracking, customer behavior analysis, and seller performance monitoring.

The project reflects practical analytics engineering work: designing reusable data models, choosing appropriate grains for reporting, and building dashboards that balance executive visibility with deeper analytical detail.

Thank you for reading,
Isaac





