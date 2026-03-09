# Apple Product Revenue Dashboard

For this analysis I explored Apple product sales from 2022-2024 to identify top-performing products across regions using SQL and Superset dashboards.

## Tools & Technologies
- **Database & Queries:** PostgreSQL  
- **Dashboarding:** Apache Superset  
- **Data Analysis:** SQL, pandas (Python), scikit-learn (Python)
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
- What categories drive revenue the most?
- What has the biggest impact to demand?

## Dashboard Preview
<img width="1238" height="720" alt="KPIs   Time-Based Analytics" src="https://github.com/user-attachments/assets/12932ce0-e057-4a88-829d-d2c8f456f09d" />
<img width="1231" height="644" alt="Categorical Analytics" src="https://github.com/user-attachments/assets/4ae6b0df-fed4-42c6-851b-28f98c6016a6" />
<img width="1231" height="357" alt="Top N Analytics" src="https://github.com/user-attachments/assets/6361bbf6-bce2-4b68-986d-83209c6febaf" />
<img width="191" height="307" alt="Filters" src="https://github.com/user-attachments/assets/1f58ff15-b977-47ca-97d0-af1b3d9d1f35" />

---

## Key Insights
- Macs (Especially the Mac Pro (M2 Ultra)) dominate revenue across most regions 
- Europe produces the highest total sales  
- Certain regions show stronger MacBook adoption  

---

## Adjustments and Improvements
- Include more filters to filter by region and product.
- Presence of more time-series trends (Per-Product Revenue over time, regional revenue over time)

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
```

--- 

## Machine Learning Analysis
See [`demand-prediction.py`](demand-prediction.py) and [`revenue-prediction.py`](reveneue-prediction.py) for code. 

### Demand Prediction
**Model used: Linear Regression**
**Fields used: unit_price_usd, category, region**

- Used a linear regression model with two feature sets to determine the impact of unit price to demand and category + region to demand.

**Results:** 
```
========= Feature set: price =========
Intercept: 451.69 | RMSE: 539.28 | R2: -0.0026
       feature  coefficient
unit_price_usd     0.041217
========= Feature set: cat_region =========
Intercept: 407.92 | RMSE: 227.27 | R2: 0.8219
             feature  coefficient
         region_Asia   972.678164
       region_Europe   940.775247
category_Apple Watch  -326.682178
    category_AirPods  -303.148799
     category_iPhone   261.413508
       category_iPad  -259.110750
  region_Europe/Asia  -138.854512
  region_Middle East  -125.506743
      region_Oceania  -118.340076
        category_Mac   -96.931475
region_South America    64.178164
region_North America   -41.571836
```

From these statistics, the demand for Apple products is driven almost entirely by geography and product category, not as much price. The model using category and region (cat_region) has an R<sup>2</sup> value of 0.82, explaining 82% of demand variance, while the model using unit price alone has an R<sup>2</sup> value of -0.0026, meaning there's near-zero price elasticity across the product lineup. We can note that the strongest demand is through region, with Asia and Europe generating around 940-970 additional units. Category-wise, the iPhone is the only product that outperforms the others in unit volumn (+261) while the Apple Watch, AirPods, and iPad underperform and sell fewer units; consistent with their higher price points. For demand planning purposes, price should not be included as a predictor, instead be in favor of a category-region model that'll provide both stronger predictive accuracy and more interpretable and actionable coefficients. 


## Revenue Prediction -- wip



