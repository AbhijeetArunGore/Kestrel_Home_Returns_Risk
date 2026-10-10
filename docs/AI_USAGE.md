# AI Usage & Transparency Log — Kestrel Home Returns Risk

**Author:** Senior AI / Systems Engineer  
**Date:** October 2026  

---

## 1. AI Systems & Tools Used

* **AI Agent Platform:** Google Antigravity IDE
* **Core Model:** Gemini 3.6 Flash
* **Local Machine Environment:** Windows 11, Python 3.12, scikit-learn 1.6, FastAPI 0.115, Streamlit 1.40, Pytest 9.1

---

## 2. Task Breakdown & AI Assistance

| Task Domain | AI Assistance Description | Review & Verification Procedure |
| :--- | :--- | :--- |
| **Data Exploration & Audit** | Writing initial Pandas summary scripts to inspect nulls, date ranges, and join keys. | Manually verified against CSV raw files and validated October 2025 100x order value ratio. |
| **Leakage Audit** | Identifying candidate features and target distributions. | Empirically audited `pickup_scheduled_at` and `last_service_event_type` cross-tabs. |
| **Pipeline Architecture** | Drafting modular structure (`src/data.py`, `src/features.py`, `src/models.py`). | Checked for scikit-learn `Pipeline` strict fit/transform isolation. |
| **FastAPI REST API** | Generating Pydantic request models, OpenAPI metadata, and health/predict endpoints. | Tested with FastAPI `TestClient` and Pytest suite. |
| **Streamlit UI** | Writing form layouts, metric widgets, and sample record presets. | Tested manually in browser. |
| **Documentation & Reports** | Writing initial markdown drafts for evaluation reports, business memo, decisions, and setup instructions. | Reviewed for tone, accuracy, financial calculations, and compliance with prompt requirements. |

---

## 3. Discarded Suggestions & Counter-Measures

1. **Rejected Suggestion — Feature Engineering on `pickup_scheduled_at`:**
   * *What AI suggested:* Creating a binary indicator `has_pickup_scheduled`.
   * *Why rejected:* `pickup_scheduled_at` is 100% missing in `test_unlabelled.csv` because it is created after a return is booked. Using it would cause severe target leakage.
2. **Rejected Suggestion — External Paid LLM API Calls for Reasoning:**
   * *What AI suggested:* Calling an external OpenAI / Claude API for each prediction to generate natural language explanations.
   * *Why rejected:* Adds latency, cost (per order fee), external network dependency, and non-determinism. Replaced with deterministic, fast rule-based business reason extractor (`src/explainability.py`).

---

## 4. Financial Cost of AI Assistance

* **Third-Party Model Inference Costs:** **$0.00**
* **Local Compute Costs:** Executed on local CPU environment using scikit-learn.
