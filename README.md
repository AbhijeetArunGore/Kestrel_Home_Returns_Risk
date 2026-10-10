# Kestrel Home — Product Returns Risk Assessment Platform

**Author:** Abhijeet Arun Gore  
**GitHub Repository:** [Kestrel_Home_Returns_Risk](https://github.com/AbhijeetArunGore/Kestrel_Home_Returns_Risk)  

---

## 1. Business Problem & Solution Architecture

Kestrel Home Appliances sells air fryers, mixer-grinders, water purifiers, robot vacuums, cooktops, fans, and heaters across D2C online channels and ~380 partner-outlet locations in India.

Product returns cost Kestrel **₹1,150 per returned order** (reverse pickup, QC inspection, repacking, write-down). This repository implements an end-to-end, production-grade pre-dispatch return risk intelligence platform that:
1. Audits and cleans raw order feeds (excluding post-dispatch target leakage features and correcting a 100x payment gateway error across October 2025 orders).
2. Fits a calibrated scikit-learn feature pipeline (`models/model_pipeline.joblib`) evaluated on a chronological held-out validation batch.
3. Generates validated return probability predictions (`predictions.csv`) for 2,096 unlabelled test orders.
4. Exposes a FastAPI prediction REST microservice (`app/api.py`) with input validation, human-readable explanations, and structured logs.
5. Provides an interactive Streamlit operations dashboard (`app/ui.py`) for warehouse and service desk teams.

---

## 2. Key Findings & Financial Impact

| Metric | Validation Measured Result | Operational Note |
| :--- | :--- | :--- |
| **Validation Dataset** | 2,126 orders (2026-04 to 2026-06) | Chronological held-out split (12m train, 3m val) |
| **ROC-AUC** | **0.7807** | Strong discrimination across positive/negative risk spectrum |
| **PR-AUC** | **0.4033** | 3.5x improvement over 11.5% random baseline |
| **Return Recall** | **76.73%** | Catches 188 of 245 actual returns at decision threshold 0.40 |
| **Net Financial Savings** | **₹37,740 / quarter** (**~₹151,000/year**) | Under Ops Policy v4.1 Confirmation Call Policy (₹45/call) |

> **Client Target Evaluation:** Demanding 95% accuracy on an imbalanced dataset (~11.5% returns) is counter-productive because predicting all 0s ("no return") achieves 88.5% accuracy while catching 0 returns. Optimizing for ROC-AUC and Net Rupee Savings at threshold **0.40** maximizes bottom-line P&L savings while avoiding customer churn for high-LTV Kestrel Shield members.

---

## 3. Repository Architecture

```
Kestrel_Home_Returns_Risk/
├── app/
│   ├── api.py                   # FastAPI prediction REST service (/predict, /health, /metadata)
│   └── ui.py                    # Streamlit web interface
├── data/
│   └── raw/                     # Standard raw CSV data files (train, test_unlabelled, etc.)
├── docs/
│   ├── ASSUMPTIONS.md           # Empirical data audit, leakage analysis & business context
│   ├── DECISIONS.md             # Technical architecture & financial policy decisions
│   ├── FAILURE_ANALYSIS.md      # Error matrix & limitation taxonomy
│   ├── AI_USAGE.md              # AI tools, prompts, costs, and counter-measures log
│   ├── RECORDING_SCRIPT.md      # 3-minute screen recording walkthrough script
│   └── SUBMISSION_FORM_DRAFT.md # Draft answers for interview submission form
├── models/
│   └── model_pipeline.joblib    # Persisted fitted scikit-learn pipeline
├── reports/
│   ├── metrics.json             # Machine-readable evaluation metrics
│   └── model_evaluation.md      # Comprehensive markdown evaluation report
├── scripts/
│   ├── train.py                 # Pipeline training and persistence script
│   ├── evaluate.py              # Reproducible evaluation report generator
│   └── predict_batch.py         # Batch prediction script generating predictions.csv
├── src/
│   ├── data.py                  # Data loading, join logic & Oct 2025 gateway fix
│   ├── features.py              # Pre-dispatch zero-leakage feature extraction transformer
│   ├── models.py                # Scikit-learn pipeline builders & persistence
│   ├── evaluation.py            # Chronological split, metrics & financial math
│   └── explainability.py        # Business reason generator & risk band categorizer
├── tests/
│   ├── test_api.py              # FastAPI unit & integration tests
│   ├── test_data.py             # Data loading, deduplication & gateway fix tests
│   └── test_features.py         # Leakage exclusion & feature shape tests
├── memo_to_ritu.md              # One-page executive business memo
├── predictions.csv              # Submission prediction output file
├── requirements.txt             # Python package dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # System documentation & setup guide
```

---

## 4. Quick Start & Setup Instructions

### Prerequisites
* Python 3.11 or 3.12 installed.

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/AbhijeetArunGore/Kestrel_Home_Returns_Risk.git
cd Kestrel_Home_Returns_Risk
pip install -r requirements.txt
```

### 2. Data File Placement
Ensure assignment files (`train.csv`, `test_unlabelled.csv`, `customers.csv`, `products.csv`, `sample_submission.csv`, `ops-policy.pdf`, `email-thread.txt`, `README.txt`) are present in the project root or `data/raw/` directory.

### 3. Model Training & Pipeline Persistence
Train the pipeline on historical data and persist the fitted model artifact:
```bash
python scripts/train.py
```

### 4. Reproducible Evaluation
Run held-out chronological evaluation and generate reports (`reports/metrics.json` & `reports/model_evaluation.md`):
```bash
python scripts/evaluate.py
```

### 5. Generate Submission Predictions (`predictions.csv`)
Generate and validate batch predictions for `test_unlabelled.csv`:
```bash
python scripts/predict_batch.py
```

### 6. Run Automated Test Suite
Execute unit and integration tests:
```bash
python -m pytest tests/ -v
```

### 7. Launch REST API Service
Start the FastAPI backend server:
```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```
* Interactive API Documentation (Swagger UI): `http://localhost:8000/docs`
* Health Check Endpoint: `http://localhost:8000/health`
* Metadata Endpoint: `http://localhost:8000/metadata`

### 8. Launch Streamlit User Interface
In a separate terminal, launch the web dashboard:
```bash
streamlit run app/ui.py
```
Open browser at `http://localhost:8501`.

---

## 5. Sample API Request & Response

### Request (`POST /predict`):
```json
{
  "order_id": "KO2609888",
  "order_placed_at": "2026-08-10 11:20:00",
  "customer_id": "KC100120",
  "sku": "KH-AF-01",
  "sales_channel": "marketplace",
  "payment_mode": "cod",
  "discount_pct": 25.0,
  "qty": 1,
  "order_value_inr": 4500.0,
  "promised_delivery_days": 3,
  "delivery_pincode": 411001,
  "is_gift": "N",
  "customer_prior_orders": 3,
  "customer_prior_returns": 2,
  "delivery_note": "Urgent delivery needed asap"
}
```

### Response (`200 OK`):
```json
{
  "order_id": "KO2609888",
  "return_probability": 0.7245,
  "risk_band": "High Risk",
  "decision": "Priority Review & Confirmation Call",
  "recommended_action": "Flag for urgent pre-dispatch phone verification. Verify model selection, address accuracy, and payment commitment.",
  "top_reasons": [
    "Customer has a history of returns (2 returns across 3 past orders, 67% return rate).",
    "Cash on Delivery (COD) payment mode carries higher pre-dispatch refusal risk.",
    "High promotional discount applied (25% checkout discount)."
  ],
  "model_version": "1.0.0",
  "disclaimer": "This score is a pre-dispatch statistical risk estimate, not a guaranteed return."
}
```

---

## 6. Document Index & Links

* Executive Memo to Operations Head: [memo_to_ritu.md](memo_to_ritu.md)
* Empirical Data Audit & Assumptions: [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)
* Architecture & Financial Decisions: [docs/DECISIONS.md](docs/DECISIONS.md)
* Detailed Model Evaluation Report: [reports/model_evaluation.md](reports/model_evaluation.md)
* Failure Analysis & Known Limitations: [docs/FAILURE_ANALYSIS.md](docs/FAILURE_ANALYSIS.md)
* AI Usage & Transparency Log: [docs/AI_USAGE.md](docs/AI_USAGE.md)
* 3-Minute Screen Recording Script: [docs/RECORDING_SCRIPT.md](docs/RECORDING_SCRIPT.md)
* Submission Form Draft: [docs/SUBMISSION_FORM_DRAFT.md](docs/SUBMISSION_FORM_DRAFT.md)
