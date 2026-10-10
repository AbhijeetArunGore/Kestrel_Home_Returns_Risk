# Model Evaluation & Financial Impact Report — Kestrel Home Returns Risk

**Date:** October 2026  
**Evaluated Pipeline:** Pre-Dispatch 5-Fold Calibrated Logistic Regression (`CalibratedClassifierCV(method='sigmoid')`)  
**Validation Strategy:** Chronological Held-Out Split (Train: 2025-04 to 2026-03, Val: 2026-04 to 2026-06)  

---

## 1. Dataset Dimensions & Validation Split

* **Total Clean Historical Orders:** 10,504 unique orders (11,155 raw rows deduplicated by `order_id`).
* **Training Fold (12 months):** 8,378 orders (Return rate: 11.40%).
* **Validation Fold (3 months):** 2,126 orders (Return rate: 11.52%, Total actual returns: 245).
* **Validation Rationale:** Simulates real-world deployment where historical 12-month data predicts the subsequent 3-month unlabelled order batch (`test_unlabelled.csv`).

---

## 2. Model Performance Summary (Calibrated Operating Threshold = 0.10)

| Metric | Value | Prevalence Baseline (All 0s) | Notes / Evaluation |
| :--- | :--- | :--- | :--- |
| **Accuracy** | **71.31%** | 88.48% | Accuracy alone is misleading on imbalanced target |
| **Precision** | **24.26%** | 0.00% | 1 in 4.1 flagged orders returns |
| **Recall** | **70.20%** | 0.00% | **Catches 70.20% of all actual returns (172/245)** |
| **F1 Score** | **0.3606** | 0.0000 | Balance of precision and recall |
| **ROC-AUC** | **0.7807** | 0.5000 | Strong discrimination across positive/negative risk spectrum |
| **PR-AUC** | **0.4038** | 0.1152 | **3.5x improvement** over random prevalence ranking |
| **Brier Score** | **0.0860** | **0.1020** | **Well-calibrated probabilities** (Brier < Prevalence baseline) |

---

## 3. Confusion Matrix Breakdown

At Calibrated Decision Threshold = 0.10 (Validation Sample Size: 2,126 orders):

```
                     Actual Non-Returned (0)    Actual Returned (1)
Predicted Low (0)          1,344 (TN)                 73 (FN)
Predicted High (1)           537 (FP)                172 (TP)
```

* **True Positives (TP = 172):** High-risk returns correctly identified before dispatch.
* **False Positives (FP = 537):** Orders flagged for confirmation calls that would not have returned.
* **False Negatives (FN = 73):** Returned orders missed by the model.
* **True Negatives (TN = 1,344):** Low-risk orders correctly processed without intervention.

---

## 4. Policy-Based Financial Impact Analysis

Using Operations Policy v4.1 parameters:
* Cost per returned order: **₹1,150**
* Pre-dispatch confirmation call cost: **₹45**
* Confirmation call return prevention rate: **35%** (prevents wrong model/address & buyer's remorse)

### Financial Arithmetic (3-Month Validation Window):
1. **Unmanaged Baseline Cost:** 245 returns × ₹1,150 = **₹281,750.00**
2. **Confirmation Calls Made:** 709 calls × ₹45 = **₹31,905.00**
3. **Returns Prevented:** 172 TP × 35% = **60 returns prevented**
4. **Gross Savings:** 60 prevented returns × ₹1,150 = **₹69,000.00**
5. **Measured Quarterly Net Savings:** ₹69,000.00 - ₹31,905.00 = **₹37,095.00 per quarter**
6. **Consistent Annualization:**
   * **Monthly Equivalent:** ₹37,095 / 3 = **₹12,365 / month**
   * **Annualized Equivalent:** ₹37,095 × 4 = **₹148,380 / year**

---

## 5. Calibrated Threshold Sensitivity Analysis

| Threshold | Flagged Vol | TP | FP | FN | Accuracy | Precision | Recall | F1 | Prevented | Call Cost (₹) | Gross Savings (₹) | Net Savings (₹) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.05 | 1329 | 220 | 1109 | 25 | 46.66% | 16.55% | 89.80% | 0.2795 | 77 | ₹59,805 | ₹88,550 | **₹28,745** |
| 0.10 | 709 | 172 | 537 | 73 | 71.31% | 24.26% | 70.20% | 0.3606 | 60 | ₹31,905 | ₹69,000 | **₹37,095** |
| 0.12 | 547 | 149 | 398 | 96 | 76.76% | 27.24% | 60.82% | 0.3763 | 52 | ₹24,615 | ₹59,800 | **₹35,185** |
| 0.15 | 413 | 131 | 282 | 114 | 81.37% | 31.72% | 53.47% | 0.3982 | 46 | ₹18,585 | ₹52,900 | **₹34,315** |
| 0.18 | 315 | 113 | 202 | 132 | 84.29% | 35.87% | 46.12% | 0.4036 | 40 | ₹14,175 | ₹46,000 | **₹31,825** |
| 0.20 | 272 | 103 | 169 | 142 | 85.37% | 37.87% | 42.04% | 0.3985 | 36 | ₹12,240 | ₹41,400 | **₹29,160** |
| 0.25 | 177 | 76 | 101 | 169 | 87.30% | 42.94% | 31.02% | 0.3602 | 27 | ₹7,965 | ₹31,050 | **₹23,085** |
| 0.30 | 126 | 66 | 60 | 179 | 88.76% | 52.38% | 26.94% | 0.3558 | 23 | ₹5,670 | ₹26,450 | **₹20,780** |
| 0.35 | 86 | 50 | 36 | 195 | 89.13% | 58.14% | 20.41% | 0.3021 | 18 | ₹3,870 | ₹20,700 | **₹16,830** |
| 0.40 | 60 | 40 | 20 | 205 | 89.42% | 66.67% | 16.33% | 0.2623 | 14 | ₹2,700 | ₹16,100 | **₹13,400** |
| 0.50 | 28 | 22 | 6 | 223 | 89.23% | 78.57% | 8.98% | 0.1612 | 8 | ₹1,260 | ₹9,200 | **₹7,940** |
| 0.60 | 20 | 17 | 3 | 228 | 89.13% | 85.00% | 6.94% | 0.1283 | 6 | ₹900 | ₹6,900 | **₹6,000** |
| 0.70 | 12 | 10 | 2 | 235 | 88.85% | 83.33% | 4.08% | 0.0778 | 4 | ₹540 | ₹4,600 | **₹4,060** |
| 0.80 | 6 | 6 | 0 | 239 | 88.76% | 100.00% | 2.45% | 0.0478 | 2 | ₹270 | ₹2,300 | **₹2,030** |
| 0.90 | 3 | 3 | 0 | 242 | 88.62% | 100.00% | 1.22% | 0.0242 | 1 | ₹135 | ₹1,150 | **₹1,015** |

---

## 6. Hidden-Test Forecast Qualification

> **Important Forecast Qualification:** The forecast for `test_unlabelled.csv` (ROC-AUC ~0.78 ± 0.02, PR-AUC ~0.40 ± 0.03) is an empirical point estimate derived from the held-out 3-month validation window (April–June 2026). It is not a guaranteed result or statistically established confidence interval on the hidden test outcomes.

---

## 7. Target Leakage & Data Hygiene Safeguards

The following features were strictly excluded from pre-dispatch model inputs:
1. `pickup_scheduled_at`: Created only after logistics receives a return request (100% missing in test data).
2. `last_service_event_type`: Post-dispatch service log (`REVERSE_PICKUP`, `DEMO_DONE`, `INSTALL_DONE`, `TECH_VISIT`).
3. October 2025 Order Value Anomaly: Corrected 100x payment gateway error across 748 October 2025 rows prior to feature scaling.
