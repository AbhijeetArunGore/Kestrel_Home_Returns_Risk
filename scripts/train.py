import sys, os
sys.path.insert(0, os.path.abspath('.'))

import json
import joblib
import pandas as pd
import numpy as np

from src.data import load_all_datasets, clean_and_merge_data
from src.models import build_model_pipeline, save_model
from src.evaluation import split_chronological, compute_all_metrics, evaluate_threshold_grid

def main():
    print("=== Training Calibrated Kestrel Returns Risk Model Pipeline ===")
    raw = load_all_datasets(".")
    train_clean = clean_and_merge_data(raw['train'], raw['customers'], raw['products'], is_train=True)

    # Chronological Split for Validation
    train_fold, val_fold = split_chronological(train_clean, split_date="2026-04-01")
    print(f"Full Clean Dataset: {len(train_clean)} rows")
    print(f"Chronological Train Fold: {len(train_fold)} rows (2025-04 to 2026-03)")
    print(f"Chronological Validation Fold: {len(val_fold)} rows (2026-04 to 2026-06)")

    # Build Calibrated Pipeline
    pipeline = build_model_pipeline(model_type="logistic", calibrated=True)

    # Fit on Train Fold
    X_tr, y_tr = train_fold.drop(columns=['returned']), train_fold['returned']
    X_val, y_val = val_fold.drop(columns=['returned']), val_fold['returned']

    print("\nFitting 5-Fold Calibrated Logistic Regression Pipeline...")
    pipeline.fit(X_tr, y_tr)

    # Evaluate on Validation Fold
    val_probs = pipeline.predict_proba(X_val)[:, 1]
    metrics = compute_all_metrics(y_val, val_probs, threshold=0.10)
    print("\n=== Validation Fold Metrics (Calibrated Threshold = 0.10) ===")
    print(json.dumps(metrics, indent=2))

    # Evaluate Threshold Grid
    grid_df = evaluate_threshold_grid(y_val, val_probs)
    print("\n=== Calibrated Threshold Optimization Grid ===")
    print(grid_df.to_string(index=False))

    # Retrain on Full Clean Dataset for Production Persistence
    print("\nRetraining calibrated pipeline on full clean dataset (10,504 orders)...")
    X_full, y_full = train_clean.drop(columns=['returned']), train_clean['returned']
    pipeline.fit(X_full, y_full)

    # Save Fitted Pipeline
    model_path = "models/model_pipeline.joblib"
    save_model(pipeline, model_path)
    print(f"Successfully saved calibrated pipeline to {model_path}")

if __name__ == "__main__":
    main()
