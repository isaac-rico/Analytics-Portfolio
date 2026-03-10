# Apple Product Revenue & Demand Analytics Dashboard

## TL;DR
- Built an end-to-end analytics project using PostgreSQL, Python, and Apache Superset
- Analyzed Apple product sales from 2022-2024 across global markets
- Built machine learning models to predict demand and revenue drivers
- Found demand is primarily driven by geography and product category rather than price
- Revenue analysis shows sales volume is the dominant driver of revenue performance

---

## Project Overview
This project analyzes global Apple product sales data to identify **key drivers of revenue and product demand** across Apple's product lineup.

Using **SQL for data aggregation, Python for machine learning**, and **Apache Superset dashboards for visualization**, this project explores how factors like **pricing, product category, and geographic markets influence sales performance**.

The analysis combines business intelligence platforms with predictive modeling to better understand Apple product demand patterns across global markets.

---

## Skills Demonstrated
- SQL analytics
- Data aggregation
- KPI development
- Dashboard development
- Machine learning modeling
- Feature engineering
- Data visualization
- Business insight generation

---

## Tools & Technologies
- **Database & Queries:** PostgreSQL  
- **Dashboarding:** Apache Superset  
- **Data Analysis:** SQL, pandas, scikit-learn 
- **Visualizations:** Superset charts  

---

## Dataset
**Source:** Kaggle – [Apple Global Product Sales Dataset](https://www.kaggle.com/datasets/ashyou09/apple-global-product-sales-dataset)  

**Fields used:** 
| Field | Description |
|---|---|
| region | Global sales region |
| country | Country of purchase |
| product_name | Apple product name |
| category | Product category |
| revenue_usd | Revenue generated |
| unit_price_usd | Product price |
| units_sold | Units sold |
| date | Transaction date |

---

## Project Pipeline
```
Kaggle Dataset
      ↓
PostgreSQL Database
      ↓
SQL Queries for KPI Aggregation → Apache Superset Dashboard Visualization
      ↓
Python Data Processing (pandas)
      ↓
Machine Learning Models (scikit-learn)
      ↓
Apache Superset Dashboard Visualization
```

---

## Objective
Analyze Apple product sales data to identify:
- top-performing products globally
- regions contributing the most revenue
- product demand patterns across markets
- key factors driving revenue and product demand

---

## Key Questions
- Which Apple products generate the most revenue globally?  
- Which regions contribute the highest total sales?  
- What are the top-selling products per country?
- Which product categories drive revenue the most?
- What factors influence product demand?
- What variables impact revenue the most?

---

## Dashboard Overview
This Superset dashboard provides multiple analytical views

### KPI Overview
- Total Revenue, Top Products, Average Order Value
  
<img width="1251" height="357" alt="image" src="https://github.com/user-attachments/assets/5eedc1e8-cf90-4c2a-ae9d-928f502442ae" />

### Time Based Analytics
- Revenue trends over time, product performance trends
  
<img width="1237" height="458" alt="image" src="https://github.com/user-attachments/assets/53ee5572-37dc-4fd2-9177-1552b441b3be" />

### Categorical Analysis
- Regional revenue comparison, market share by product category
  
<img width="1241" height="360" alt="image" src="https://github.com/user-attachments/assets/0dfef36d-81b1-499d-b093-8198d9187c66" />

### Top-N Analysis
- top performing products globally, highest revenue products by region
  
<img width="1243" height="640" alt="image" src="https://github.com/user-attachments/assets/ad003d54-9fad-4455-a361-ea2778afc257" />

### Interactive Filters
- year, month, quarter, region, country, product, product category, rank
  
<img width="186" height="549" alt="image" src="https://github.com/user-attachments/assets/4a99a772-279b-4024-851b-494789c1f781" />

---

## SQL Analysis

SQL queries were used to generate KPIs and aggregated metrics for the dashboard.

Example query to find top products by region:

```sql
SELECT 
    region,
    product_name,
    SUM(revenue_usd)::NUMERIC(12,2) AS revenue
FROM apple_dataset
GROUP BY region, product_name
ORDER BY revenue DESC;
```
See [`trends.sql`](trends.sql) for all SQL queries + more used in the dashboard

--- 

## Machine Learning Analysis
Two machine learning analyses were conducted:
1. Demand Prediction Model
2. Revenue Prediction Model
   
See [`demand-prediction.py`](demand-prediction.py) and [`revenue-prediction.py`](revenue-prediction.py) for code. 

---

## Demand Prediction Model
**Model: Linear Regression**
**Target Variable:** units_sold

### Feature Sets Tested:
**Price Model:** unit_price_usd
**Category + Region Model:** category, region

---

## Demand Model Performance
| Feature Set | Features | R^2 | RMSE |
| --- | --- | --- | --- |
| Price | unit_price_usd | -0.0026 | 539.28 |
| Category + Region | category + region | 0.8219 | 227.27 |

**Coefficients for Category + Region Feature Set:** 
| Feature | Coefficient |
| --- | --- | 
| region_Asia | 972.678164 |
| region_Europe | 940.775247 |
| category_Apple Watch | -326.682178 |
| category_AirPods | -303.148799 |
| category_iPhone | 261.413508 |
| category_iPad | -259.110750 |
| region_Europe/Asia | -138.854512 |
| region_Middle East | -125.506743 |
| region_Oceania | -118.340076 |
| category_Mac | -96.931475 |
| region_South America | 64.178164 |
| region_North America | -41.571836 |


---

## Demand Model Insights
The category + region feature set explains **82% of demand variance**, indicating that **product category and geography** strongly influence product demand.

Key observations:
- Asia and Europe generate the highest demand
- iPhones dominate unit sales volume
- Pricing shows near-zero predictive power, suggesting very minimal price elasticity across Apple's product lineup

These results indicate that **demand for forecasting models should prioritize product categorization and geographic markets rather than price variables along.**

--- 

## Revenue Prediction Model
A second regression model was built to understand the **drivers of Apple product revenue.**

**Target Variable:** units_sold

### Feature Sets Tested:
**Baseline Model:** unit_price_usd, units_sold
**Discounted Price Model:** discounted_price_usd, units_sold
**Full Model:** discounted_price_usd, units_sold, category, region

---

## Revenue Model Performance

| Model | R^2 | RMSE |
| --- | --- | --- |
| Baseline Model | 0.760 | 1335 |
| Discounted Model | 0.768 | 1314 |
| Full Model | 0.768 | 1314 |

**Baseline Model Features and Coefficients**
| Feature | Coefficient |
| --- | --- | |
|units_sold | 766.939003|
|unit_price_usd  |  1.911222|

**Discounted Model Features and Coefficients**
| Feature | Coefficient |
| --- | --- | 
|units_sold  | 766.229327|
|discounted_price_usd   |  1.988374|

**Full Model Features and Coefficients**
| Feature | Coefficient |
| --- | --- | 
|          units_sold |  765.969302|
|  region_Europe/Asia |  138.081932|
|  region_Middle East |  100.621849|
|     region_Oceania  |  85.579493|
|      region_Europe  |  58.972056|
|     category_iPhone |  44.294941|
|region_South America |   38.227884|
|        category_Mac |   29.043123|
|       category_iPad |  26.814988|
|    category_AirPods |   23.659333|
|region_North America |   22.296577|
|         region_Asia |   18.411948|
|category_Apple Watch |    4.823739|
|discounted_price_usd |    1.983639|


---

## Revenue Model Insights
The regression model explains about **76-77% of revenue variance**, indicating strong predictive performance.

Key Observations:
- Sales volume drives revenue
  - the units_sold coefficient (~766) was consistently the largest across all models, confirming that **sales volume is the most dominant driver of revenue performance.**
- Pricing has a smaller impact
- Regional variables slightly influence revenue outcomes
- Product category coefficients suggest that **iPhone products contribute the strongest revenue impact**, followed by Mac products, etc.

---

## Key Insights
- Macs (Especially the Mac Pro (M2 Ultra)) dominate revenue across most regions. 
- Europe produces the highest **total sales** among global markets.
- iPhones generate the highest **demand** across product categories.
- Demand is driven primarily by **geographic market and product category**.
- Pricing has **minimal influence on demand** within the Apple product ecosystem.
- Revenue performance is largely determined by **sales volume rather than price variation**.

--- 

## Future Improvements
Potential improvements to this project include:
- demand elasticity modeling with additional pricing variables
- advanced ML models like Random Forest or Gradient Boosting
- additional dashboard filters and time-series visualizations
- integrating marketing or product launch data

---

## Conclusion
This project demonstrates how **SQL analytics, machine learning, and dashboard visualization can be combined to analyze global product sales performance.**

The analysis shows that **Apple product demand is driven primarily by geography and product category**, while **revenue is largely determined by sales volume rather than pricing**.

The findings in this project highlight the importance of **market segmentation and demand forecasting when analyzing global product performance**.






