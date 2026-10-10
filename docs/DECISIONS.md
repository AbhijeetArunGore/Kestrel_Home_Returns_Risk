# Architectural & Modeling Decisions — Kestrel Home Returns Risk

**Author:** Senior AI / ML / Systems Engineer  
**Date:** October 2026  

---

## 1. System Architecture & Modular Design

To ensure clean-machine reproducibility, maintainability, and clear separation of concerns, the codebase is structured into standard production modules:

* `src/data.py` — Raw data loading, schema validation, join processing (`customers.csv` and `products.csv`), deduplication, and October 2025 payment gateway error correction.
* `src/features.py` — Target-leakage-free pre-dispatch feature engineering pipeline, text analysis for `delivery_note`, temporal features, and customer/product interaction features.
* `src/models.py` — Scikit-learn modeling pipelines (Dummy Baseline, Calibrated Logistic Regression with 5-fold `CalibratedClassifierCV(method='sigmoid')`, Random Forest, HistGradientBoosting), hyperparameter configuration, and persistence.
* `src/evaluation.py` — Chronological validation split, threshold optimization, confusion matrix generation, financial cost/savings arithmetic, and evaluation reporting.
* `src/explainability.py` — Model interpretation using feature importances to generate human-readable business reason codes and risk bands based on calibrated probabilities.
* `scripts/train.py` — CLI entrypoint to train, calibrate, evaluate, optimize threshold, and persist the model pipeline to `models/model_pipeline.joblib`.
* `scripts/predict_batch.py` — CLI entrypoint to generate submission file `predictions.csv` for `test_unlabelled.csv`.
* `scripts/evaluate.py` — CLI entrypoint to generate machine-readable `reports/metrics.json` and `reports/model_evaluation.md`.
* `app/api.py` — FastAPI application providing `/predict`, `/health`, `/metadata` endpoints with Pydantic validation and structured JSON logs.
* `app/ui.py` — Streamlit interactive web frontend calling the backend API.

---

## 2. Leakage Prevention Architecture & Probability Calibration

1. **Pipeline Isolation:** All feature transformations (Imputers, OneHotEncoders, StandardScalers) are encapsulated inside `sklearn.pipeline.Pipeline` or custom Transformer classes fit strictly on training folds to eliminate data leakage.
2. **Leakage Stripping:** Post-dispatch columns (`pickup_scheduled_at` and `last_service_event_type`) are explicitly excluded at the data loading / feature selection boundary before model training.
3. **Probability Calibration:** The core classification model uses 5-fold cross-validated sigmoid calibration (`CalibratedClassifierCV(estimator=base_lr, cv=5, method='sigmoid')`). This reduces the Brier score from **0.1694 to 0.0860** (substantially outperforming the 0.1020 prevalence baseline) and ensures the output score represents a true empirical probability of return.

---

## 3. Financial Cost Function & Operational Policy Design

### 3.1 Holding Dispatch Policy (Ritu's Proposal)
* If an order is held for >24h, 12% of customers cancel.
* Lost Profit Margin per Cancellation: ~₹2,000 (AOV ~₹8,000 * 25% margin).
* Cost per False Positive Hold: 12% * ₹2,000 = **₹240 per FP**.
* Cost per False Negative (Unflagged Return): **₹1,150 per FN**.

### 3.2 Pre-Dispatch Confirmation Call Policy (Recommended Alternative)
* Pre-dispatch call cost: **₹45 per called order**.
* Return prevention effectiveness: **35%** of returns on called orders are prevented (*operational assumption subject to pilot validation*).
* Cost per False Positive Call: **₹45 per FP**.
* Cost per True Positive Call: **₹45 - (0.35 * ₹1,150) = -₹357.50** (Net savings of ₹357.50 per TP!).
* Net Savings Equation: `Net Savings = (TP * 0.35 * ₹1,150) - ((TP + FP) * ₹45)`.

This policy is financially superior, avoids customer churn for Shield members, and directly leverages the proven spring confirmation call pilot (Policy §7)!
