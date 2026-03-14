# ================= Random Forest Classifier =================

# ====================== Imports ======================
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import TargetEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

# create engine for postgres
engine = create_engine('postgresql+psycopg2://postgres:12345@localhost:7777/postgres')

# connection verification
try:
    with engine.connect() as conn:
        print("Connected")
except Exception as e:
    print(f"Not Connected: {e}")

# SQL query
query = """
SELECT  
    category,
    customer_segment,  
    region, 
    sales_channel,
    AVG(customer_rating) AS customer_rating, 
    AVG(discount_pct) AS discount_pct,
    AVG(unit_price_usd) AS unit_price_usd,
    AVG(discounted_price_usd) AS discounted_price_usd,
    SUM(units_sold) AS units_sold
FROM apple_dataset
GROUP BY 
    category, customer_segment, region, sales_channel
"""

# query = """
# SELECT  
#     category,
#     customer_segment,  
#     region, 
#     sales_channel,
#     customer_rating,
#     discount_pct,
#     unit_price_usd,
#     discounted_price_usd,
#     revenue_usd
# FROM apple_dataset
# """

# store query into pandas dataframe
df = pd.read_sql(query, engine)

# preprocessing
features = {
    'numeric': ['customer_rating', 'discount_pct', 'discounted_price_usd', 'unit_price_usd'],
    'categorical': ['category', 'customer_segment', 'region', 'sales_channel']
}

categorical_features = features['categorical']
numeric_features = features['numeric']


# create feature set to identify which features need encoding
all_features = (categorical_features + numeric_features)

# drop rows with missing values
df = df.dropna(subset=all_features + ['units_sold'])

X = df[all_features]
y = df['units_sold']

# split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# create transformer pipeline
transformers = []
if features.get('categorical'):
    transformers.append(('categorical', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), features['categorical']))
if features.get('numeric'):
    transformers.append(('numeric', 'passthrough', features['numeric']))

# preprocess data that needs encoding
preprocessor = ColumnTransformer(transformers)

# create pipeline with preprocessing and model
pipeline = Pipeline([('preprocessor', preprocessor), 
                     ('model', RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_leaf=5, random_state=42, n_jobs=-1))])

# fit data to pipeline and predict
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

# calculate metrics
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"R^2: {r2:.4f} | RMSE: {rmse:.2f}")

# feature importance
feature_names = []
if features.get('categorical'):
    categorical = pipeline.named_steps['preprocessor'].named_transformers_['categorical']
    feature_names += categorical.get_feature_names_out(features['categorical']).tolist()
if features.get('numeric'):
    feature_names += features['numeric']

# create importance dataframe
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': pipeline.named_steps['model'].feature_importances_
}).sort_values('importance', ascending=False)

# print top 10 features
print("Top 10 Features by Importance:")
print(importance_df.head(10).to_string(index=False))

# top 10 features that impact demand prediction
top_features = importance_df.head(10).sort_values('importance', ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(top_features["feature"], top_features["importance"])
plt.xlabel("Feature Importance")
plt.title("Random Forest Feature Importance for Demand Prediction")
plt.tight_layout()
plt.show()

# actual vs predicted values
plt.figure(figsize=(12, 8))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel("Actual Units Sold")
plt.ylabel("Predicted Units Sold")
plt.title("Actual vs Predicted Units Sold - Random Forest Model")
plt.tight_layout()
plt.show()

# what if analysis: discount changes and predicted demand
df_agg = df.copy()

# segment to simulate
row = df_agg.iloc[0].copy() # take first since it has a discount

# simulate discount changes from 0% to 33%
discount_grid = np.linspace(0.0, 0.33, 34)

# create simulated rows for each discount level
simulated_rows = []
# for each discount level, create new row w/ discount and calc discounted price, then add to the list to predict
for d in discount_grid:
    r = row.copy()
    r["discount_pct"] = d
    if "discounted_price_usd" in r.index and "unit_price_usd" in r.index:
        r["discounted_price_usd"] = r["unit_price_usd"] * (1 - d)
    simulated_rows.append(r)

# df of simulated rows
sim_df = pd.DataFrame(simulated_rows)

# predict demand for each simulated row
sim_pred = pipeline.predict(sim_df[all_features])

plt.figure(figsize=(8, 6))
plt.plot(discount_grid, sim_pred)
plt.xlabel("Discount %")
plt.ylabel("Predicted Units Sold")
plt.title("What-If Analysis: Discount vs Predicted Demand")
plt.tight_layout()
plt.show()

