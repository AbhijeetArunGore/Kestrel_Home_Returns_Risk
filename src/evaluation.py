import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
)

# Cost Constants from Ops Policy v4.1
COST_PER_RETURN = 1150.0        # Rs 1,150 per returned order
COST_PER_CALL = 45.0            # Rs 45 per confirmation call
CALL_PREVENTION_RATE = 0.35     # 35% of returns prevented on called orders
HOLD_CANCELLATION_RATE = 0.12   # 12% customer cancellation rate if held >24h
ESTIMATED_MARGIN_LOSS = 2000.0  # ~Rs 2,000 gross margin loss per cancelled order

def split_chronological(clean_df: pd.DataFrame, split_date: str = "2026-04-01") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataset chronologically into train and validation sets."""
    df = clean_df.copy()
    df['order_placed_dt'] = pd.to_datetime(df['order_placed_at'])
    dt_split = pd.to_datetime(split_date)

    train_df = df[df['order_placed_dt'] < dt_split].copy().reset_index(drop=True)
    val_df = df[df['order_placed_dt'] >= dt_split].copy().reset_index(drop=True)

    return train_df, val_df

def compute_all_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.40) -> Dict[str, Any]:
    """Compute comprehensive classification and financial metrics for a model."""
    y_pred = (y_prob >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.5
    pr_auc = float(average_precision_score(y_true, y_prob))
    brier = float(brier_score_loss(y_true, y_prob))

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # Financial Arithmetic: Confirmation Call Policy
    calls_made = tp + fp
    returns_prevented = int(round(tp * CALL_PREVENTION_RATE))
    gross_savings = float(returns_prevented * COST_PER_RETURN)
    call_cost = float(calls_made * COST_PER_CALL)
    net_savings = float(gross_savings - call_cost)
    unmanaged_cost = float(y_true.sum() * COST_PER_RETURN)

    return {
        "dataset_size": len(y_true),
        "total_returns": int(y_true.sum()),
        "return_rate": float(y_true.mean()),
        "threshold": float(threshold),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "brier_score": round(brier, 4)
        },
        "confusion_matrix": {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp
        },
        "financials_call_policy": {
            "calls_made": calls_made,
            "returns_prevented": returns_prevented,
            "call_cost_inr": call_cost,
            "gross_savings_inr": gross_savings,
            "net_savings_inr": net_savings,
            "unmanaged_return_cost_inr": unmanaged_cost,
            "net_managed_return_cost_inr": unmanaged_cost - net_savings
        }
    }

def evaluate_threshold_grid(y_true: np.ndarray, y_prob: np.ndarray) -> pd.DataFrame:
    """Evaluate financial and classification metrics across a grid of thresholds."""
    thresholds = np.linspace(0.1, 0.9, 17)
    rows = []

    for t in thresholds:
        m = compute_all_metrics(y_true, y_prob, threshold=t)
        fin = m["financials_call_policy"]
        met = m["metrics"]
        cm = m["confusion_matrix"]

        rows.append({
            "threshold": round(t, 2),
            "flagged_volume": fin["calls_made"],
            "tp": cm["tp"],
            "fp": cm["fp"],
            "fn": cm["fn"],
            "accuracy": met["accuracy"],
            "precision": met["precision"],
            "recall": met["recall"],
            "f1_score": met["f1_score"],
            "returns_prevented": fin["returns_prevented"],
            "call_cost_inr": fin["call_cost_inr"],
            "gross_savings_inr": fin["gross_savings_inr"],
            "net_savings_inr": fin["net_savings_inr"]
        })

    return pd.DataFrame(rows)
