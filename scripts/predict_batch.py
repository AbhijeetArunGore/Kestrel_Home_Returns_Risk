import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import numpy as np
from src.data import load_all_datasets, clean_and_merge_data
from src.models import load_model

def generate_predictions(data_dir: str = ".", output_path: str = "predictions.csv"):
    """
    Generate predictions for test_unlabelled.csv using the fitted model pipeline,
    validate against sample_submission.csv schema, and save predictions.csv.
    """
    print("=== Generating Batch Predictions for test_unlabelled.csv ===")
    
    # 1. Load data & fitted model
    raw = load_all_datasets(data_dir)
    test_df = raw['test']
    cust_df = raw['customers']
    prod_df = raw['products']
    sub_df = raw['sample_submission']

    model = load_model("models/model_pipeline.joblib")

    # 2. Clean and merge test data (is_train=False)
    test_clean = clean_and_merge_data(test_df, cust_df, prod_df, is_train=False)

    # 3. Predict Return Probabilities
    scores = model.predict_proba(test_clean)[:, 1]

    # 4. Construct Output DataFrame
    pred_df = pd.DataFrame({
        "order_id": test_clean["order_id"],
        "score": scores
    })

    # 5. Rigorous Validation Checks
    print("\n--- Running Schema Validation Checks ---")
    
    # Check 1: Row count
    assert len(pred_df) == len(sub_df), f"Row count mismatch! Got {len(pred_df)}, expected {len(sub_df)}"
    print(f"[PASS] Row count matches exactly: {len(pred_df)} rows")

    # Check 2: Column names and order
    assert list(pred_df.columns) == list(sub_df.columns), f"Column mismatch! Got {list(pred_df.columns)}, expected {list(sub_df.columns)}"
    print(f"[PASS] Columns match sample submission: {list(pred_df.columns)}")

    # Check 3: Order ID match and sequence
    assert (pred_df["order_id"] == sub_df["order_id"]).all(), "order_id sequence does not match sample_submission.csv!"
    print("[PASS] order_id sequence matches sample_submission.csv 100%")

    # Check 4: Null value check
    assert pred_df["score"].isnull().sum() == 0, "Found null values in score column!"
    print("[PASS] 0 null values in predictions")

    # Check 5: Score probability range
    assert (pred_df["score"] >= 0.0).all() and (pred_df["score"] <= 1.0).all(), "Scores out of bounds [0, 1]!"
    print(f"[PASS] Probability scores valid within range [{pred_df['score'].min():.4f}, {pred_df['score'].max():.4f}]")

    # Check 6: Uniqueness check
    assert pred_df["order_id"].nunique() == len(pred_df), "Duplicate order_ids found in predictions!"
    print("[PASS] order_id uniqueness verified")

    # 6. Save final file
    pred_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Final predictions saved to '{output_path}'")

    # Print summary statistics
    print("\nPrediction Score Distribution Summary:")
    print(pred_df["score"].describe())

if __name__ == "__main__":
    generate_predictions()
