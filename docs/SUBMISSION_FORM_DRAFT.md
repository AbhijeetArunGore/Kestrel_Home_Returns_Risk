# Submission Form Draft — Kestrel Home Returns Risk

**Candidate Name:** Abhijeet Arun Gore  
**GitHub Repository:** `https://github.com/AbhijeetArunGore/Kestrel_Home_Returns_Risk`  

---

### Question 1: What did you build, and what business outcome does it move? State the number and the money.
**Answer:**  
I built a complete, production-grade pre-dispatch return risk intelligence platform consisting of:
1. A scikit-learn feature engineering and calibrated Logistic Regression pipeline (`models/model_pipeline.joblib`).
2. A RESTful FastAPI microservice (`app/api.py`) with input validation, human-readable explanations, health/metadata monitoring, and structured JSON logs.
3. A Streamlit web dashboard (`app/ui.py`) for operations teams to evaluate order return risks interactively.
4. A validated submission file `predictions.csv` for the 2,096 unlabelled test orders.

**The Number and The Money:**  
On a strict 3-month chronological held-out validation dataset of 2,126 orders, the model achieves a **0.7807 ROC-AUC** and **0.4033 PR-AUC** (3.5x over the 11.5% random baseline). Operating at decision threshold 0.40, it catches **76.73% of all actual returns** (188/245). Triggering pre-dispatch confirmation calls (₹45/call) on flagged orders prevents 66 returns per quarter, delivering **net savings of ₹37,740 per quarter** (**₹150,960/year**) under Ops Policy v4.1 parameters.

---

### Question 2: What score do you expect predictions.csv to get on the hidden outcomes, on which metric, and why that metric? Say how you estimated it.
**Answer:**  
I expect `predictions.csv` to achieve a **ROC-AUC of 0.77 ± 0.02** and a **PR-AUC of 0.39 ± 0.03** on the hidden test outcomes.  
* **Metric Rationale:** ROC-AUC and PR-AUC measure true probability ranking discrimination independent of threshold. PR-AUC is especially informative given the ~11.5% positive target imbalance.
* **Estimation Methodology:** Estimated using a 3-month chronological split (training on April 2025 – March 2026 [8,378 orders], validating on April – June 2026 [2,126 orders]). This split mirrors the deployment timeframe of `test_unlabelled.csv` (July – September 2026 [2,096 orders]).

---

### Question 3: How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.
**Answer:**  
* **Sample Size & Testing:** Checked on 2,126 validation orders plus 9 automated unit/integration tests (`pytest`) covering data cleaning, payment gateway fixes, feature extractor leakage checks, model predictions, and API error codes.
* **Error Rate:** At threshold 0.40, accuracy is 66.27% (False Positive Rate: 35.1%, False Negative Rate: 23.3%).
* **Failure Patterns:** 
  1. *False Positives (660 cases):* Prepaid orders with high discounts or marketplace channel tags where customers kept the item despite high risk indicators.
  2. *False Negatives (57 cases):* First-time prepaid app buyers who unexpectedly returned products due to post-delivery unboxing/quality issues unobservable prior to dispatch.

---

### Question 4: Did you change, narrow, or push back on the client's ask? What, when, and why?
**Answer:**  
Yes. I pushed back on two specific requests from Ritu Deshpande:
1. **The 95% Accuracy Target:** Predicting the majority class ("no return") gives 88.5% accuracy but catches 0 returns. Demanding 95% accuracy forces a model to suppress risk flags. I demonstrated that optimizing for ROC-AUC and Net Rupee Savings at threshold 0.40 yields ₹37,740/quarter in bottom-line value.
2. **Holding Dispatch for Flagged Orders:** Holding dispatch >24h incurs a 12% customer cancellation penalty (losing ~₹2,000 gross margin per cancelled order) and antagonizes high-LTV Kestrel Shield members. I recommended using flagged orders to trigger ₹45 pre-dispatch confirmation calls (which prevent 35% of returns without cancellation risk).

---

### Question 5: What is wrong with what you are handing us?
**Answer:**  
1. **Delivery Note Processing:** Uses keyword/string matching rather than advanced NLP embeddings.
2. **Dynamic Customer Lifetime Aggregates:** Relies on static `customer_prior_orders` / `customer_prior_returns` features provided in the export rather than real-time graph recalculations.
3. **Local Deployment:** Configured for local SQLite/memory execution rather than a multi-node Kubernetes cluster with Redis caching.

---

### Question 6: What did you deliberately leave out, and why that rather than something else?
**Answer:**  
I deliberately omitted heavy deep learning architectures (e.g. PyTorch tabular transformers) and external paid LLM APIs. Tabular tree/logistic models are vastly more interpretable, calibrated, reproducible, and computationally efficient for tabular data of 10k rows, eliminating external API latency and cost risks.

---

### Question 7: Anything you built or found that nobody asked for?
**Answer:**  
1. **October 2025 Gateway Error Fix:** Discovered that 748 October 2025 festive season orders had `order_value_inr` multiplied by 100 in the payment gateway. I implemented automated ratio correction (`expected_price` matching).
2. **Target Leakage Safeguards:** Identified that `pickup_scheduled_at` and `last_service_event_type` (`REVERSE_PICKUP`) are post-dispatch logs and stripped them from pre-dispatch modeling.
3. **Pincode `000000` Walk-in Handler:** Discovered walk-in partner outlet orders use pincode `000000` and exhibit a 12.6% return rate, creating a specific feature for them.

---

### Question 8: What did you use AI for?
**Answer:**  
* **AI Tool Used:** Google Antigravity IDE powered by Gemini 3.6 Flash.
* **Where AI Helped:** Writing boilerplate FastAPI pydantic schemas, drafting initial Streamlit layout, generating pytest test cases, and speeding up markdown documentation creation.
* **Where AI Wasted Time / Discarded:** Initial script suggestions attempted to use `pickup_scheduled_at` (target leakage), which I caught during empirical feature auditing and rejected.
* **Cost:** $0.00 incremental third-party API cost (all training and inference run locally using scikit-learn).

---

### Question 9: Your Public Google Drive Link
**Answer:**  
`[PLACEHOLDER: Insert Public Google Drive Link for Video & Artifact Backup]`

---

### Question 10: Someone picks this up on Monday and you are unreachable. The three things they need to know.
**Answer:**  
1. **Run Commands:** Run `python scripts/predict_batch.py` to regenerate `predictions.csv`. Run `pytest -v` to run all 9 automated unit tests.
2. **Target Leakage Rule:** Never add `pickup_scheduled_at` or post-dispatch `last_service_event_type` back into the feature set.
3. **Operational Threshold:** Use decision threshold **0.40** for confirmation calls (₹45/call). Do not hold dispatch unconditionally.

---

### Question 11: Honest hours spent. One number.
**Answer:**  
`[PLACEHOLDER: Insert Total Honest Hours Spent, e.g., 14]`

---

### Question 12: GitHub Repo Link
**Answer:**  
`https://github.com/AbhijeetArunGore/Kestrel_Home_Returns_Risk`

---

### Question 13: What does one prediction cost, and what would a month cost at Kestrel's volume (about 700 orders a month)? Show the arithmetic.
**Answer:**  
* **Inference Compute Cost per Order:** **₹0.0000** (Local scikit-learn CPU inference takes < 2 milliseconds per prediction with 0 paid external API calls).
* **Monthly Infrastructure Cost (at 700 orders/month):**
  * Local/Internal Server: **₹0 / month**.
  * Small Cloud Instance (e.g. AWS t4g.nano or Render Starter at $7/mo): **~₹580 / month**.
* **Total Monthly Arithmetic at 700 orders/month:**
  * Incremental API model call fee: 700 × ₹0 = **₹0**.
  * Optional cloud hosting: **~₹580**.
  * Total Monthly System Cost: **₹580 / month**.
