import pandas as pd
import numpy as np
import hashlib
import urllib.request
import io
import ssl

def load_real_data():
    """
    Downloads real public retail datasets to serve as the primary experiment data.
    Dataset 1: Monthly Shampoo Sales (Real, Public)
    Dataset 2: Monthly Car Sales (Real, Public)
    """
    # Bypass SSL verification if any issues in local env
    ssl._create_default_https_context = ssl._create_unverified_context
    
    url_shampoo = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/shampoo.csv"
    url_cars = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv"
    
    # Load Shampoo
    print("  -> Fetching Real Dataset: Shampoo Sales...")
    df_shampoo = pd.read_csv(url_shampoo)
    df_shampoo['Month'] = pd.date_range(start='2020-01-01', periods=len(df_shampoo), freq='ME')
    df_shampoo = df_shampoo.rename(columns={'Month': 'date', 'Sales': 'demand'})
    df_shampoo['sku'] = 'SKU-SHAMPOO'
    
    # Load Cars
    print("  -> Fetching Real Dataset: Car Sales...")
    df_cars = pd.read_csv(url_cars)
    df_cars['Month'] = pd.to_datetime(df_cars['Month'])
    df_cars = df_cars.rename(columns={'Month': 'date', 'Sales': 'demand'})
    df_cars['sku'] = 'SKU-CARS'
    
    # Combine
    # For fair testing, we will align lengths or just use one primary for the deep metrics
    df = pd.concat([df_shampoo, df_cars], ignore_index=True)
    
    # Preprocessing (Fill missing, sort)
    df = df.sort_values(by=['sku', 'date']).reset_index(drop=True)
    df['demand'] = df['demand'].ffill()
    
    # Calculate Dataset Hash
    data_str = df.to_csv(index=False).encode('utf-8')
    dataset_hash = hashlib.sha256(data_str).hexdigest()
    
    meta = {
        "dataset_name": "Public Retail Sales (Shampoo & Cars)",
        "dataset_version": "1.0",
        "subset_definition": "Full combined series",
        "num_skus": 2,
        "num_stores": 1,
        "time_range": f"{df['date'].min().date()} to {df['date'].max().date()}",
        "dataset_hash": dataset_hash,
        "preprocessing_steps": ["Forward-fill NA", "Standardize date column", "Concatenate SKUs"]
    }
    
    return df, meta

def engineer_features(df):
    """
    Creates lag features and rolling means.
    """
    df_feat = df.copy()
    
    # Group by SKU and create features
    feature_dfs = []
    for sku, group in df_feat.groupby('sku'):
        group = group.copy()
        group['lag_1'] = group['demand'].shift(1)
        group['lag_2'] = group['demand'].shift(2)
        group['rolling_mean_3'] = group['demand'].rolling(window=3).mean()
        group = group.dropna() # Drop rows with NaNs from lags
        feature_dfs.append(group)
        
    final_df = pd.concat(feature_dfs, ignore_index=True)
    return final_df
