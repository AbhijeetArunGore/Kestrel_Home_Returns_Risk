# MEMORANDUM

**TO:** Ritu Deshpande, Head of D2C Operations  
**FROM:** Lead AI & Systems Engineer  
**DATE:** October 2026  
**SUBJECT:** Pre-Dispatch Product Return Risk Model — Evaluation & Operational Deployment Recommendation  

---

### 1. Decision: Ready for Controlled Operational Pilot
The pre-dispatch return risk prediction system is fully built, tested, and ready for a 60-day operational pilot. However, **we strongly recommend deploying the model to trigger pre-dispatch confirmation calls (₹45/call) rather than holding dispatch for flagged orders.** 

Holding dispatch creates a 12% customer cancellation penalty on false positives (losing ~₹2,000 gross margin per cancelled order and irritating high-LTV Kestrel Shield members). In contrast, pre-dispatch confirmation calls resolve address errors, model mix-ups, and buyer's remorse—preventing 35% of returns without risking order cancellations or Shield customer friction.

---

### 2. Measured Performance & Numbers
* **Evaluation Sample:** Evaluated on a strict, chronological held-out validation batch of **2,126 recent historical orders** (April–June 2026, representing 3 full months of operations).
* **Model Ranking Capability (ROC-AUC):** **0.7807** (PR-AUC of 0.4033, a 3.5x improvement over the 11.5% unmanaged random baseline).
* **Return Detection (Recall):** At the recommended operating decision threshold of **0.40**, the model successfully catches **76.73% of all actual returns** (188 out of 245 actual returned orders identified before dispatch).
* **Evaluation of the 95% Accuracy Target:** Predicting the majority class ("no return") blindly achieves 88.5% accuracy while catching zero returns. Requiring 95% accuracy on an imbalanced dataset (~11.5% return rate) forces the model to ignore return risks. Optimizing for ROC-AUC and Net Rupee Savings at threshold 0.40 is far more valuable to Kestrel's P&L.

---

### 3. Financial Analysis (Rupees & Monthly Arithmetic)
All calculations follow Operations Policy v4.1 (Return cost: **₹1,150**, Confirmation call cost: **₹45**, Call return prevention rate: **35%**):

* **Monthly Volume Baseline (at ~700 orders/month):**
  * Expected monthly returns without model: ~80 returns (Unmanaged monthly return cost: **₹92,000**).
* **Model-Assisted Confirmation Call Policy (at Threshold = 0.40):**
  * Flagged orders for confirmation calls: ~280 orders/month (~40% of order volume).
  * Outbound call expense: 280 calls × ₹45 = **₹12,600/month**.
  * Returns prevented: ~22 returns prevented/month (61 returns identified × 35% prevention rate).
  * Gross logistics savings: 22 prevented returns × ₹1,150 = **₹25,300/month**.
  * **Net Monthly P&L Savings:** **₹12,700/month** (**₹38,100 per quarter**).
  * **Net Annualized Savings:** **~₹152,400 per year** in direct bottom-line savings.

---

### 4. Key Limitations & Risk Safeguards
1. **Target Leakage Safeguards:** Features generated after dispatch (`pickup_scheduled_at` and `last_service_event_type`) were strictly excluded.
2. **Data Anomaly Correction:** Corrected a 100x payment gateway error across 748 October 2025 festive orders where order values were recorded in paise instead of rupees.
3. **Walk-in Outlet Orders:** Walk-in partner orders lacking address capture (pincode `000000`) exhibit a 12.6% return rate and are flagged explicitly for phone confirmation.

---

### 5. Next Week: Action Plan
1. **Monday:** Brief warehouse logistics and outsourced call center team on the 0.40 risk threshold.
2. **Tuesday:** Deploy FastAPI prediction endpoint to staging and integrate with the CRM order feed.
3. **Wednesday:** Begin 60-day pilot routing flagged orders (probabilities ≥ 0.40) to the confirmation call queue.
4. **Friday:** Conduct weekly review comparing called order return rates against uncalled control orders.
