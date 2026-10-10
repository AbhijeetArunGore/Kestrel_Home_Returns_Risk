import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class KestrelFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible feature extraction transformer that strictly uses
    only features available at pre-dispatch decision time (0 target leakage).
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()

        # Parse Datetimes
        order_dt = pd.to_datetime(df['order_placed_at'], errors='coerce')
        signup_dt = pd.to_datetime(df['signup_date'], errors='coerce')
        launch_dt = pd.to_datetime(df['launch_date'], errors='coerce')

        # 1. Temporal & Seasonal Features
        df['order_month'] = order_dt.dt.month.fillna(6).astype(int)
        df['order_day'] = order_dt.dt.day.fillna(15).astype(int)
        df['order_dow'] = order_dt.dt.dayofweek.fillna(0).astype(int)
        df['order_hour'] = order_dt.dt.hour.fillna(12).astype(int)
        df['is_weekend'] = (df['order_dow'] >= 5).astype(int)
        df['is_festive_season'] = df['order_month'].isin([10, 11]).astype(int)

        # 2. Customer Profile & Interactions
        df['shield_member_binary'] = (df['shield_member'] == 'Y').astype(int)
        df['days_since_signup'] = (order_dt - signup_dt).dt.days.fillna(365).clip(lower=0)
        df['customer_prior_orders'] = df['customer_prior_orders'].fillna(0).astype(float)
        df['customer_prior_returns'] = df['customer_prior_returns'].fillna(0).astype(float)
        df['customer_prior_return_rate'] = df['customer_prior_returns'] / (df['customer_prior_orders'] + 1.0)
        df['is_repeat_customer'] = (df['customer_prior_orders'] > 0).astype(int)

        # 3. Product & Price Features
        df['discount_pct'] = df['discount_pct'].fillna(0).astype(float)
        df['qty'] = df['qty'].fillna(1).astype(float)
        df['list_price_inr'] = df['list_price_inr'].fillna(5000).astype(float)
        df['order_value_inr'] = df['order_value_inr'].fillna(df['list_price_inr'] * df['qty']).astype(float)
        df['discount_amount_inr'] = df['list_price_inr'] * df['qty'] * (df['discount_pct'] / 100.0)
        df['unit_order_value'] = df['order_value_inr'] / (df['qty'] + 1e-6)
        df['warranty_months'] = df['warranty_months'].fillna(12).astype(float)
        df['days_since_launch'] = (order_dt - launch_dt).dt.days.fillna(365).clip(lower=0)

        # 4. Order & Logistics Features
        df['promised_delivery_days'] = df['promised_delivery_days'].fillna(3).astype(float)
        df['is_gift_binary'] = (df['is_gift'] == 'Y').astype(int)
        df['is_walkin_pincode'] = (df['delivery_pincode'] == 0).astype(int)
        df['pincode_prefix'] = df['delivery_pincode'].astype(str).str.zfill(6).str[:2]

        # 5. Delivery Note Features
        notes = df['delivery_note'].fillna("").astype(str).str.lower()
        df['has_delivery_note'] = (notes.str.len() > 0).astype(int)
        df['delivery_note_len'] = notes.str.len()
        df['note_has_urgent'] = notes.str.contains('urgent|fast|quick|asap', regex=True).astype(int)
        df['note_has_call'] = notes.str.contains('call|ring|phone', regex=True).astype(int)
        df['note_has_gift'] = notes.str.contains('gift|wrap|present|birthday', regex=True).astype(int)
        df['note_has_fragile'] = notes.str.contains('handle|fragile|care|break', regex=True).astype(int)
        df['note_has_gate'] = notes.str.contains('gate|security|guard|flat|apartment', regex=True).astype(int)

        # Select columns to retain (excluding target leak fields: pickup_scheduled_at, last_service_event_type)
        feature_cols = [
            # Numeric
            'discount_pct', 'qty', 'order_value_inr', 'list_price_inr', 'discount_amount_inr',
            'unit_order_value', 'promised_delivery_days', 'customer_prior_orders',
            'customer_prior_returns', 'customer_prior_return_rate', 'days_since_signup',
            'days_since_launch', 'warranty_months', 'delivery_note_len', 'order_month',
            'order_day', 'order_dow', 'order_hour',
            # Binary
            'is_weekend', 'is_festive_season', 'shield_member_binary', 'is_repeat_customer',
            'is_gift_binary', 'is_walkin_pincode', 'has_delivery_note', 'note_has_urgent',
            'note_has_call', 'note_has_gift', 'note_has_fragile', 'note_has_gate',
            # Categorical
            'sales_channel', 'payment_mode', 'family', 'sku', 'city', 'state', 'pincode_prefix'
        ]

        return df[feature_cols]

NUMERIC_FEATURES = [
    'discount_pct', 'qty', 'order_value_inr', 'list_price_inr', 'discount_amount_inr',
    'unit_order_value', 'promised_delivery_days', 'customer_prior_orders',
    'customer_prior_returns', 'customer_prior_return_rate', 'days_since_signup',
    'days_since_launch', 'warranty_months', 'delivery_note_len', 'order_month',
    'order_day', 'order_dow', 'order_hour', 'is_weekend', 'is_festive_season',
    'shield_member_binary', 'is_repeat_customer', 'is_gift_binary', 'is_walkin_pincode',
    'has_delivery_note', 'note_has_urgent', 'note_has_call', 'note_has_gift',
    'note_has_fragile', 'note_has_gate'
]

CATEGORICAL_FEATURES = [
    'sales_channel', 'payment_mode', 'family', 'sku', 'city', 'state', 'pincode_prefix'
]
