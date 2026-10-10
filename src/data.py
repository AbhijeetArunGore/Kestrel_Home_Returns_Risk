import pandas as pd
import numpy as np
import os
from pathlib import Path

def get_data_path(filename: str, base_dir: str = ".") -> str:
    """Check standard locations for data files."""
    candidates = [
        os.path.join(base_dir, filename),
        os.path.join(base_dir, "data", "raw", filename),
        os.path.join(base_dir, "data", filename),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    
    # Check for UUID-prefixed files
    for root in [base_dir, os.path.join(base_dir, "data", "raw")]:
        if os.path.exists(root):
            for f in os.listdir(root):
                if f.endswith("-" + filename) or f == filename:
                    return os.path.join(root, f)
                    
    raise FileNotFoundError(f"Could not locate required assignment file: {filename}")

def load_all_datasets(data_dir: str = ".") -> dict:
    """Load all assignment CSV datasets."""
    train_path = get_data_path("train.csv", data_dir)
    test_path = get_data_path("test_unlabelled.csv", data_dir)
    cust_path = get_data_path("customers.csv", data_dir)
    prod_path = get_data_path("products.csv", data_dir)
    sub_path = get_data_path("sample_submission.csv", data_dir)

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    cust_df = pd.read_csv(cust_path)
    prod_df = pd.read_csv(prod_path)
    sub_df = pd.read_csv(sub_path)

    return {
        "train": train_df,
        "test": test_df,
        "customers": cust_df,
        "products": prod_df,
        "sample_submission": sub_df,
    }

def clean_and_merge_data(orders_df: pd.DataFrame, cust_df: pd.DataFrame, prod_df: pd.DataFrame, is_train: bool = True) -> pd.DataFrame:
    """
    Clean order records, perform exact joins with customer and product references,
    correct October 2025 payment gateway anomalies, and deduplicate training rows.
    """
    df = orders_df.copy()

    # 1. Deduplicate training data by order_id to prevent partner_feed duplicate leakage
    if is_train and 'order_id' in df.columns:
        # Keep CRM source if available, else first
        if 'source' in df.columns:
            df = df.sort_values(by=['order_id', 'source'], ascending=[True, True])
        df = df.drop_duplicates(subset=['order_id'], keep='first').reset_index(drop=True)

    # 2. Join customer details
    df = df.merge(cust_df, on='customer_id', how='left')

    # 3. Join product details
    df = df.merge(prod_df, on='sku', how='left')

    # 4. Correct October 2025 Payment Gateway 100x Order Value Anomaly
    # Expected price = list_price_inr * qty * (1 - discount_pct / 100.0)
    df['order_placed_dt'] = pd.to_datetime(df['order_placed_at'], errors='coerce')
    df['expected_price'] = df['list_price_inr'] * df['qty'] * (1.0 - df['discount_pct'] / 100.0)
    
    # If order_value_inr is ~100x expected_price (Oct 2025 gateway bug), correct it
    ratio = df['order_value_inr'] / (df['expected_price'] + 1e-6)
    anomaly_mask = (ratio > 50.0) & (df['order_placed_dt'].dt.month == 10) & (df['order_placed_dt'].dt.year == 2025)
    df.loc[anomaly_mask, 'order_value_inr'] = df.loc[anomaly_mask, 'order_value_inr'] / 100.0

    return df
