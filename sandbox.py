from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import pymc as pm
import arviz as az


# load
data = pd.read_csv('./cleaned_data/final_dataset.csv')

# simplify to numerical encoding
data['result_code'] = data['result'].map(
    {'Home Win': 0, 'Draw': 1, 'Away Win': 2})

# standardice numeric features (important for convergence)

scaler = StandardScaler()
features_home = ['home_avg_market_value',
                 'home_nationalities', 'home_avg_age', 'home_total_minutes']
features_away = ['away_avg_market_value',
                 'away_nationalities', 'away_avg_age', 'away_total_minutes']

X_home = scaler.fit_transform(data[features_home])
X_away = scaler.fit_transform(data[features_away])

# outcome
y = data['result_code'].values
