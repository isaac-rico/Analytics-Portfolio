# This runs a Linear Regression model on the data to predict revenue

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
import numpy as np

#create engine for postgres
engine = create_engine('postgresql+psycopg2://postgres:12345@localhost:7777/postgres')

# connection verification
if engine:
    print("Connected")
else:
    print("Not Connected")

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
                    features.get('onehot', []) + 
                    features.get('target', []))
    
    # split data
    X = df[all_features] 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # create transformer pipeline
    transformers = []
    if features.get('onehot'):
        transformers.append(('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), features['onehot']))
    elif features.get('target'):
        transformers.append(('target', TargetEncoder(smooth='auto'), features['target']))

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
    elif features.get('target'):
        feature_names += features['target']
    elif features.get('numeric'):
        feature_names += features['numeric']

    # create coefficient dataframe
    coef_df = pd.DataFrame({
        'feature':     feature_names,
        'coefficient': pipeline.named_steps['model'].coef_
    }).sort_values('coefficient', key=abs, ascending=False)

    # calculate metrics, r2, root mean squared error, intecept, coefficient in print section
    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    intercept = pipeline.named_steps['model'].intercept_

    # print metrics
    print(f"========= Feature set: {name} =========")
    print(f"Intercept: {intercept:.2f} | RMSE: {rmse:.2f} | R2: {r2:.4f}")
    print(coef_df.to_string(index=False))

    # ====================== Plot for actual vs predicted revenue ======================
    plt.figure()
    plt.scatter(y_test, y_pred)

    plt.xlabel("Actual Revenue")
    plt.ylabel("Predicted Revenue")
    plt.title(f"Actual vs Predicted Revenue ({name} model)")

    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val])
    plt.show()

    # ====================== Plot for top drivers of revenue ======================
    top_features = coef_df.head(10)

    plt.figure()
    plt.barh(top_features['feature'], top_features['coefficient'])
    plt.title("Top Drivers of Revenue")
    plt.xlabel("Coefficient Impact")
    plt.gca().invert_yaxis()
    plt.show()

    # ====================== Plot for revenue vs units sold ======================
    plt.scatter(df['units_sold'], df['revenue'], alpha=0.5)
    plt.xlabel("Units Sold")
    plt.ylabel("Revenue")
    plt.title("Revenue vs Units Sold")
    plt.show()



