import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath('.'))

from src.data import load_all_datasets, clean_and_merge_data
from src.features import KestrelFeatureExtractor

def test_feature_extractor_no_leakage():
    raw = load_all_datasets(".")
    train_clean = clean_and_merge_data(raw['train'], raw['customers'], raw['products'], is_train=True)

    extractor = KestrelFeatureExtractor()
    features_df = extractor.transform(train_clean)

    # Ensure target leakage fields are NOT present
    assert 'pickup_scheduled_at' not in features_df.columns
    assert 'last_service_event_type' not in features_df.columns
    assert 'returned' not in features_df.columns

    # Verify no nulls in generated numeric features
    assert features_df['order_value_inr'].isnull().sum() == 0
    assert features_df['customer_prior_return_rate'].isnull().sum() == 0
