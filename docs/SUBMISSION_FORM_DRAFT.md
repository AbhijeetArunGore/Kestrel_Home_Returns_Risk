# Submission Form Draft — Kestrel Home Returns Risk

**Candidate Name:** Abhijeet Arun Gore  
**GitHub Repository:** `https://github.com/AbhijeetArunGore/Kestrel_Home_Returns_Risk`  

---

### Question 1: What did you build, and what business outcome does it move? State the number and the money.
**Answer:**  
I built a complete, production-grade pre-dispatch return risk intelligence platform consisting of:
1. A scikit-learn feature engineering and 5-fold calibrated Logistic Regression pipeline (`CalibratedClassifierCV(method='sigmoid')`, saved at `models/model_pipeline.joblib`).
2. A RESTful FastAPI microservice (`app/api.py`) with Pydantic validation, human-readable explanations, health/metadata monitoring, and structured JSON logs.
3. A Streamlit web dashboard (`app/ui.py`) for operations teams to evaluate order return risks interactively.
4. A validated submission file `predictions.csv` for the 2,096 unlabelled test orders.

**The Number and The Money:**  
On a strict 3-month chronological held-out validation dataset of 2,126 orders (April–June 2026), the model achieves a **0.7807 ROC-AUC**, a **0.4038 PR-AUC** (3.5x over the 11.5% random baseline), and a **0.0860 Brier score** (outperforming the 0.1020 prevalence baseline). Operating at decision threshold 0.10 (flagging orders with ≥10% return probability), it catches **70.20% of all actual returns** (172/245). Triggering pre-dispatch confirmation calls (₹45/call) on flagged orders prevents an estimated 60 returns per quarter, delivering **estimated validation-based net savings of ₹37,095 per quarter** (**₹12,365/month**, **₹148,380/year**) under the stated operational assumptions (specifically the assumed 35% return-prevention rate from Policy §7, which requires a live pilot to validate).

---

### Question 2: What score do you expect predictions.csv to get on the hidden outcomes, on which metric, and why that metric? Say how you estimated it.
**Answer:**  
* **Forecast Range:** I estimate `predictions.csv` will achieve a **ROC-AUC of ~0.78 ± 0.02** and a **PR-AUC of ~0.40 ± 0.03** on the hidden test outcomes.  
* **Forecast Qualification:** This forecast is a rough empirical estimate derived from the 3-month chronological validation split (April – June 2026). The actual hidden-test score remains unknown until evaluated by the grading suite.
* **Metric Rationale:** ROC-AUC and PR-AUC measure true probability ranking discrimination independent of threshold. PR-AUC is especially informative given the ~11.5% positive target prevalence.

---

### Question 3: How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.
**Answer:**  
* **Sample Size & Testing:** Checked on 2,126 validation orders plus 9 automated unit/integration tests (`pytest`) covering data cleaning, payment gateway fixes, feature extractor leakage checks, calibrated model inference, and API response codes.
* **Error Rate & Metrics:** At calibrated threshold 0.10, accuracy is 71.31%, recall is 70.20%, and precision is 24.26%. The model explicitly prioritizes detecting return risks over maximizing overall accuracy on an imbalanced dataset.
* **Failure Patterns:** 
  1. *False Positives (537 cases):* Prepaid orders with high discounts or marketplace channel tags where customers kept the item despite high risk indicators.
  2. *False Negatives (73 cases):* First-time prepaid app buyers who unexpectedly returned products due to post-delivery unboxing/quality issues unobservable prior to dispatch.

---

### Question 4: Did you change, narrow, or push back on the client's ask? What, when, and why?
**Answer:**  
Yes. I challenged the request to optimize solely for 95% accuracy because accuracy alone can hide poor return detection on an imbalanced dataset. On the chronological validation set, the highest accuracy in the tested threshold sweep was 89.42% at threshold 0.40, where recall fell to 16.33%. At threshold 0.10, the model detected 70.20% of actual returns. I therefore recommended evaluating the system on return detection and estimated net business value, not accuracy alone. The 95% target was not achieved in this validation experiment.

---

### Question 5: What is wrong with what you are handing us?
**Answer:**  
1. **Delivery Note Processing:** Uses keyword regex matching rather than sentence transformer NLP embeddings.
2. **Customer Lifetime Features:** Uses static historical aggregates (`customer_prior_orders`, `customer_prior_returns`) from the export rather than real-time graph recalculations.
3. **Local Compute Setup:** Designed for single-instance local/container execution rather than a multi-node Kubernetes cluster.

---

### Question 6: What did you deliberately leave out, and why that rather than something else?
**Answer:**  
I deliberately omitted heavy deep learning architectures (e.g. PyTorch tabular transformers) and external paid LLM APIs. Tabular tree/calibrated logistic models are vastly more interpretable, reproducible, and computationally efficient for tabular data of 10k rows. 5-fold sigmoid calibration improved probability alignment (Brier score 0.0860 vs 0.1020 baseline), though full calibration curves across subsets should be monitored during a live pilot.

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
* **Where AI Helped:** Writing boilerplate FastAPI pydantic schemas, drafting Streamlit layout, generating pytest test cases, and speeding up documentation creation.
* **Where AI Wasted Time / Discarded:** Initial script suggestions attempted to use `pickup_scheduled_at` (target leakage), which I caught during empirical feature auditing and rejected.
* **Cost:** $0.00 incremental third-party API cost (all training and inference run locally using scikit-learn).

---

### Question 9: Your Public Google Drive Link
**Answer:**  
`[MANUAL USER PLACEHOLDER: Insert Public Google Drive Link for Video & Artifact Backup]`

---

### Question 10: Someone picks this up on Monday and you are unreachable. The three things they need to know.
**Answer:**  
1. **Run Commands:** Run `python scripts/predict_batch.py` to regenerate `predictions.csv`. Run `python -m pytest tests/` to execute all 9 automated unit tests.
2. **Target Leakage Rule:** Never add `pickup_scheduled_at` or post-dispatch `last_service_event_type` back into the feature set.
3. **Operational Threshold:** Use calibrated decision threshold **0.10** for confirmation calls (₹45/call). Do not hold dispatch unconditionally.

---

### Question 11: Honest hours spent. One number.
**Answer:**  
`[MANUAL USER PLACEHOLDER: Insert Total Honest Hours Spent, e.g., 14]`

---

### Question 12: GitHub Repo Link
**Answer:**  
`https://github.com/AbhijeetArunGore/Kestrel_Home_Returns_Risk`

---

### Question 13: What does one prediction cost, and what would a month cost at Kestrel's volume (about 700 orders a month)? Show the arithmetic.
**Answer:**  
* **Inference Compute Cost per Order:** **₹0.0000** (Local scikit-learn CPU inference takes < 2 milliseconds per prediction with 0 paid external API calls).
* **Estimated Monthly Infrastructure Cost (at 700 orders/month):**
  * Local/Internal Server: **₹0 / month**.
  * Small Cloud Instance (e.g. AWS t4g.nano or Render Starter at $7/mo): **~₹580 / month** (estimated).
* **Total Monthly Arithmetic at 700 orders/month:**
  * Incremental API model call fee: 700 × ₹0 = **₹0**.
  * Estimated cloud hosting: **~₹580**.
  * Total Monthly System Cost: **~₹580 / month**.
