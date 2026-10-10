import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath('.'))

from src.data import load_all_datasets, clean_and_merge_data

def test_load_all_datasets():
    datasets = load_all_datasets(".")
    assert "train" in datasets
    assert "test" in datasets
    assert "customers" in datasets
    assert "products" in datasets
    assert "sample_submission" in datasets

    assert len(datasets["train"]) == 11155
    assert len(datasets["test"]) == 2096
    assert len(datasets["sample_submission"]) == 2096

def test_clean_and_merge_data_deduplication():
    raw = load_all_datasets(".")
    train_clean = clean_and_merge_data(raw['train'], raw['customers'], raw['products'], is_train=True)
    
    # Verify deduplication reduced 11,155 rows to 10,504 unique order_ids
    assert len(train_clean) == 10504
    assert train_clean['order_id'].nunique() == 10504

def test_october_payment_gateway_fix():
    raw = load_all_datasets(".")
    train_clean = clean_and_merge_data(raw['train'], raw['customers'], raw['products'], is_train=True)
    
    # Verify no order values exceed 100,000 INR after 100x fix
    assert (train_clean['order_value_inr'] < 100000).all()
