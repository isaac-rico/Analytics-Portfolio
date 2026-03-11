# This runs a Linear Regression model on the data to predict revenue

# ====================== Imports ======================
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import TargetEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import seaborn as sns
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
    category, region, unit_price_usd, discounted_price_usd,
    SUM(units_sold) AS units_sold, SUM(revenue_usd)::NUMERIC(12, 2) AS revenue
FROM apple_dataset
GROUP BY category, region, unit_price_usd, discounted_price_usd;
"""

# store query into pandas dataframe
df = pd.read_sql(query, engine)

#print(df)

# identify features
features_sets = {
    'baseline':    {'numeric': ['unit_price_usd', 'units_sold']},
    'discounted':  {'numeric': ['discounted_price_usd', 'units_sold']},
    'all':         {'numeric': ['discounted_price_usd', 'units_sold'], 
                     'onehot': ['category', 'region']
                    },
}

y = df['revenue']

# for loop to iterate through feature sets
for name, features in features_sets.items():
    
    # create feature set to identify which features need encoding
    all_features = (features.get('numeric', []) + 
                    features.get('onehot', []))
    # print(all_features)

    # split data
    X = df[all_features] 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # create transformer pipeline
    transformers = []
    if features.get('onehot'):
        transformers.append(('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), features['onehot']))

    # preprocess data that needs encoding
    preprocessor = ColumnTransformer(transformers, remainder='passthrough')

    # create pipeline with preprocessing and model
    pipeline = Pipeline([('preprocessor', preprocessor),
                         ('model', LinearRegression())])

    # fit data to pipeline and predict
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # get feature names; add to feature name list for coefficient tracking
    feature_names = []
    if features.get('onehot'):
        ohe = pipeline.named_steps['preprocessor'].named_transformers_['onehot']
        feature_names += ohe.get_feature_names_out(features['onehot']).tolist()
    
    feature_names += features['numeric']

    # print(feature_names)
    # print(pipeline.named_steps['model'].coef_)
    # print("passed")

    # create coefficient dataframe
    coef_df = pd.DataFrame({
        'feature':     feature_names,
        'coefficient': pipeline.named_steps['model'].coef_
    }).sort_values('coefficient', key=abs, ascending=False)
    # print(len(coef_df['feature']), len(coef_df['coefficient']))

    # calculate metrics, r2, root mean squared error, intecept, coefficient in print section
    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    intercept = pipeline.named_steps['model'].intercept_

    # print metrics
    print(f"========= Feature set: {name} =========")
    print(f"Intercept: {intercept:.2f} | RMSE: {rmse:.2f} | R^2: {r2:.4f}")
    print(coef_df.to_string(index=False))

    # colors per category for identification on plot
    category_colors = {
        'iPhone': '#1f77b4',
        'iPad': '#ff7f0e',
        'Mac': '#2ca02c',
        'Apple Watch': '#d62728',
        'AirPods': '#9467bd',
        'Accessories': '#8c564b'
    }

    # ====================== Plot for actual vs predicted revenue ======================
    plt.figure()
    
    # category names for identification on plot
    for cat, group in df.groupby('category'):
        subset = df.loc[y_test.index, 'category'] == cat
        plt.scatter(y_test[subset], y_pred[subset], color=category_colors.get(cat), label=cat, alpha=0.5, s=20)

    plt.legend()
    plt.xlabel("Actual Revenue")
    plt.ylabel("Predicted Revenue")
    plt.title(f"Actual vs Predicted Revenue ({name} model)")

    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val])
    plt.show()

# ====================== Product Portfolio Analysis 1 - revenue TOTAL vs units sold ======================
plt.figure(figsize=(8, 6))

# aggregate revenue and units sold by category
units_df = df.groupby('category').agg({
    'units_sold': 'sum', 
    'revenue': 'sum'
}).reset_index()

# category names for identification on plot
for cat in units_df['category'].unique():
    subset = units_df[units_df['category'] == cat]
    plt.scatter(subset['units_sold'], subset['revenue'], color=category_colors.get(cat), label=cat, alpha=0.5, s=200)    

# add median lines
plt.axvline(units_df['units_sold'].median(), linestyle="--")
plt.axhline(units_df['revenue'].median(), linestyle="--")

plt.legend()
plt.xlabel("Units Sold")
plt.ylabel("Revenue")
plt.title("Product Portfolio Analysis: Revenue per Units Sold")
plt.show()

# ====================== Product Portfolio Analysis 2 - revenue PER UNIT vs units sold ======================
plt.figure(figsize=(8, 6))

# aggregate revenue and units sold by category
portfolio_df = df.groupby('category').agg({
    'units_sold': 'sum',
    'revenue': 'sum',
}).reset_index()

# calculate revenue per unit
portfolio_df['revenue_per_unit'] = portfolio_df['revenue'] / portfolio_df['units_sold']

# category names for identification on plot
for cat in portfolio_df['category'].unique():
        subset = portfolio_df[portfolio_df['category'] == cat]
        plt.scatter(subset['units_sold'], subset['revenue_per_unit'], color=category_colors.get(cat), label=cat, alpha=0.5, s=200) 

# add median lines
plt.axvline(portfolio_df['units_sold'].median(), linestyle="--")
plt.axhline(portfolio_df['revenue_per_unit'].median(), linestyle="--")

plt.legend()
plt.xlabel("Units Sold")
plt.ylabel("Revenue per Unit")
plt.title("Product Portfolio Analysis: Revenue per Unit vs Units Sold")
plt.show()

# ====================== Heatmap for revenue by category and region ======================
heatmap_df = df.groupby(['category', 'region'])['revenue'].sum().unstack(fill_value=0)
plt.figure(figsize=(12, 6))
sns.heatmap(
    heatmap_df,
    annot=True,
    fmt='0.2f',
    cmap='YlOrRd',
    linewidths=0.5,
    linecolor='#e0e0e0',
    cbar_kws={'label': 'Revenue'}
)
plt.title('Revenue by Category and Region', fontsize=14, pad=16)
plt.xlabel('Region')
plt.ylabel('Category')
plt.xticks(rotation=35, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
