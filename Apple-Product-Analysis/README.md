# Global Apple Product Sales Analytics: Revenue and Demand Modeling

## TL;DR
[Dashboard](#dashboard-overview)
- Built an end-to-end analytics project using PostgreSQL, Python, and Apache Superset
- Analyzed Apple product sales from 2022-2024 across global markets
- Built Linear Regression and Random Forest ML models to predict demand and revenue drivers
- Found demand is primarily driven by geography and product category rather than price
- Revenue analysis shows that units sold is the most significant predictor for revenue

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
- Revenue trends over time, units sold trends over time
  
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
- **Model: Linear Regression**
- **Target Variable:** units_sold

### Feature Sets Tested:
- **Price Model:** unit_price_usd
- **Category + Region Model:** category, region

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

## (3/13) Random Forest Demand Model

To further explore nonlinear relationships between product demand and market characteristics, a **Random Forest regression model** was implemented.

### Features:
- **Numeric**: unit_price_usd, discounted_price_usd, discount_pct, customer_rating
- **Categorical**: category, customer_segment, region, sales_channel

### Target variable:
- units_sold


The original dataset contained very low variance in the target variable, where units_sold values ranged between 1 and 9 units per transaction.

To improve model performance, the dataset was **aggregated by category, customer segment, region, and sales channel**, increrasing the variance in the target variable and enabling the model to learn stronger demand patterns across market segments. 

---

## Random Forest Model Performance

| R^2 | RMSE |
| --- | --- |
| 0.8729 | 8.79 |
 
### Actual vs Predicted Demand

<img width="733" height="561" alt="image" src="https://github.com/isaac-rico/Analytics-Portfolio/blob/d929f9305fa7fdb28d751a2aa7e629227a6e74ae/Apple-Product-Analysis/Actual%20vs%20Predicted%20-%20Random%20Forest.png"/>

This visualization compares the **actual vs predicted demand across category/ customer segment/region/sales channel segments**.

Each point represents a predicted demand value compared with the observed value in the test dataset. With a variance of 0.8729, we expect a decent trend of points grouped closer to the diagonal, which we observe in the graph.

---

## Feature Importance

<img width="733" height="561" alt="image" src="https://github.com/isaac-rico/Analytics-Portfolio/blob/274d41fe4f868c514308cbbe5b791b16bd6f2b37/Apple-Product-Analysis/Feature%20Importance.png"/>

Feature importance analysis shows the strongest predictors of demand. Results are similar to that of the Linear Regression model:

| Feature | Importance Insight | 
| ------- | ------------------ |
|region_Europe | strongest demand driver |
|region_Asia | second strongest market |
|category_iPhone | highest demand category |
|discounted_price_usd | moderate influence |

These results reinforce findings from the Linear Regression model that **geography and product category primarily drive product demand**.

---

## What-If Demand Simulation

To demonstrate how the model can support decision-making, a **what-if analysis** was conducted by varying the product discount percentage while keep other features constant. This simulation allows us to estimate how demand may respond to different pricing strategies. 

### Example Scenario
A sample product-market segment was selected and discount percentages were varied from 0-30%. 

The Random Forest model was then used to predict demand under each scenario.

<img width="733" height="561" alt="image" src="https://github.com/isaac-rico/Analytics-Portfolio/blob/98ce786ba006aa3cdb4232626bb5091c3cd88c5f/Apple-Product-Analysis/What%20if%20-%20discount%20%25.png"/>

Observations:
- Increasing discounts generally lead to **higher predicted demand**
- Demand increases at a **diminishing rate as discounts grow**
- This type of simulation can help estimate **optimal pricing strategies**

---

## Random Forest Model Insights

Key observations:
- Regional demand differences dominate sales performance
- iPhones consistently generate the highest demand
- Pricing variables influence demand, but secondary to geography.

Compared to the Linear Regression model, Random Forest provides **stronger predictive flexibility,** capturing nonlinear interactions between market and product variables.

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
| --- | --- |
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

## Product Portfolio Analysis
To further analyze product strategy, **product demand (units sold)** and **revenue and revenue efficiency** were compared together.

### Revenue vs Units Sold
<img width="733" height="561" alt="image" src="https://github.com/user-attachments/assets/a5ba783f-976d-4db0-a898-71a23e3c6ec6" />

This chart shows overall revenue performance by product category.

Takeaways:
- Mac products generate highest total revenue
- iPhones maintain the highest demand across markets

---

### Revenue Efficiency (Revenue per Unit)
<img width="756" height="568" alt="image" src="https://github.com/user-attachments/assets/7ef33089-656d-41db-92c9-8058e73c5eea" />

This chart shows the relationship between product demand and revenue efficiency.

Takeaways:
- Mac products still generate the highest revenue per unit
- Accessories sell at high volume but generate lower revenue per unit

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
- integrating sales channels, customer segments and ratings.

---

## Conclusion
This project demonstrates how **SQL analytics, machine learning, and dashboard visualization can be combined to analyze global product sales performance.**

The analysis shows that **Apple product demand is driven primarily by geography and product category**, while **revenue is largely determined by sales volume rather than pricing**.

The findings in this project highlight the importance of **market segmentation and demand forecasting when analyzing global product performance**.













