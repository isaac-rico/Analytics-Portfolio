from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import seaborn as sns
import numpy as np

#create engine for postgres
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
    category, region,
    AVG(unit_price_usd) AS unit_price_usd,
    SUM(units_sold) AS units_sold
FROM apple_dataset
GROUP BY category, region;
"""

# store query into pandas dataframe
df = pd.read_sql(query, engine)

# create feature sets
features = {
    'price': {'numeric': ['unit_price_usd']},
    'cat_region': {'onehot': ['category', 'region']},
}

y = df['units_sold']

# for loop to iterate through feature sets
for name, features in features.items():

    # create feature set to identify which features need encoding
    all_features = (features.get('numeric', []) + features.get('onehot', []))

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
        onehot = pipeline.named_steps['preprocessor'].named_transformers_['onehot']
        feature_names += onehot.get_feature_names_out(features['onehot']).tolist()
    elif features.get('numeric'): 
        feature_names += features['numeric']

    # create coefficient dataframe
    coef_df = pd.DataFrame({
        'feature':     feature_names,
        'coefficient': pipeline.named_steps['model'].coef_
    }).sort_values('coefficient', key=abs, ascending=False)

    # calculate metrics
    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    intercept = pipeline.named_steps['model'].intercept_

    print(f"=== Feature set: {name} ===")
    print(f"Intercept: {intercept:.2f} | RMSE: {rmse:.2f} | R2: {r2:.4f}")
    print(coef_df.to_string(index=False))

    # ====================== Heatmap for units sold by category and region ======================
    if name == 'cat_region':
        heatmap_df = df.groupby(['category', 'region'])['units_sold'].sum().unstack(fill_value=0)

        plt.figure(figsize=(12, 6))
        sns.heatmap(
            heatmap_df,
            annot=True,
            fmt=',d',
            cmap='YlOrRd',
            linewidths=0.5,
            linecolor='#e0e0e0',
            cbar_kws={'label': 'Units Sold'}
        )

        plt.title('Demand by Category and Region', fontsize=14, pad=16)
        plt.xlabel('Region')
        plt.ylabel('Category')
        plt.xticks(rotation=35, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()

    # ====================== Scatter plot for unit price vs units sold ======================
    elif name == 'price':
        plt.scatter(df['unit_price_usd'], df['units_sold'], alpha=0.5)
        plt.xlabel("Unit Price")
        plt.ylabel("Units Sold")
        plt.title("Unit Price vs Demand")
        plt.show()

        