# Apple Product Revenue Dashboard

For this analysis I analyzed Apple product sales to identify top-performing products across regions using SQL and Superset dashboards.

## Tools & Technologies
- **Database & Queries:** PostgreSQL  
- **Dashboarding:** Apache Superset  
- **Data Analysis:** SQL, pandas (Python)  
- **Visualizations:** Superset charts  


## Dataset
**Source:** Kaggle – [Apple Global Product Sales Dataset](https://www.kaggle.com/datasets/ashyou09/apple-global-product-sales-dataset)   
**Fields used:** region, country, product_name, revenue_usd, date  


## Objective
Analyze Apple product revenue trends across regions and countries to identify top-performing products and growth opportunities.

## Key Questions
- Which Apple products generate the most revenue globally?  
- Which regions contribute the highest sales?  
- What are the top-selling products per country?  

## Dashboard Preview
<img width="1238" height="720" alt="KPIs   Time-Based Analytics" src="https://github.com/user-attachments/assets/12932ce0-e057-4a88-829d-d2c8f456f09d" />
<img width="1231" height="644" alt="Categorical Analytics" src="https://github.com/user-attachments/assets/4ae6b0df-fed4-42c6-851b-28f98c6016a6" />
<img width="1231" height="357" alt="Top N Analytics" src="https://github.com/user-attachments/assets/6361bbf6-bce2-4b68-986d-83209c6febaf" />
<img width="191" height="307" alt="Filters" src="https://github.com/user-attachments/assets/1f58ff15-b977-47ca-97d0-af1b3d9d1f35" />

---

## Key Insights
- iPhones dominate revenue across most regions  
- North America produces the highest total sales  
- Certain regions show stronger MacBook adoption  
- iPad revenue is increasing steadily in Asia  
- iPod and accessories have declining revenue trends  

---

## SQL Analysis
See [`trends.sql`](trends.sql) for all SQL queries used to generate KPIs, metrics, and charts.

Sample query to find top products by region:

```sql
SELECT 
    region,
    product_name,
    SUM(revenue_usd)::NUMERIC(12,2) AS revenue
FROM apple_dataset
GROUP BY region, product_name
ORDER BY revenue DESC;
