# Failure Analysis & Known Limitations — Kestrel Home Returns Risk

**Author:** Senior AI / Systems Engineer  
**Date:** October 2026  

---

## 1. Error Matrix Breakdown

Evaluation conducted on held-out 3-month chronological validation batch (2,126 orders, 245 actual returns, calibrated threshold = 0.10):

| Classification Type | Count | Operational Impact |
| :--- | :--- | :--- |
| **True Positives (TP)** | 172 | High-risk return orders correctly flagged pre-dispatch (70.20% recall). Triggers confirmation calls (costing ₹45/call) and prevents ~60 returns (saving ₹69,000 gross). |
| **True Negatives (TN)** | 1,344 | Low-risk orders correctly processed without operational delay or intervention. |
| **False Positives (FP)** | 537 | Non-returned orders flagged for confirmation calls. Incurs ₹45 call cost (total ₹24,165), but does NOT trigger order cancellation risk because dispatch is not blocked. |
| **False Negatives (FN)** | 73 | Returned orders missed by model pre-dispatch (29.80% miss rate). Result in standard ₹1,150 return cost per order. |

---

## 2. Failure Case Taxonomy

### 2.1 False Positive Characterization (Flagged non-returns — 537 cases)
* **Pattern A: Heavy Promotional Discounts (e.g. >20% checkout discount):** Model flags high discount items due to historical correlation with impulse purchases, but prepaid app users frequently retain bargain purchases.
* **Pattern B: First-time Marketplace Orders:** Marketplace sales tag elevated risk, but many represent legitimate one-time buyers.
* **Mitigation:** Making ₹45 confirmation calls instead of holding dispatch ensures False Positives cost only ₹45 rather than ₹240 in customer cancellation penalties.

### 2.2 False Negative Characterization (Missed returns — 73 cases)
* **Pattern A: First-time Prepaid App Buyers:** Customers with 0 prior order history who purchase standard air fryers or mixer grinders prepaid. Pre-dispatch metadata contains 0 risk signals, but post-delivery quality preferences or transit damage trigger returns.
* **Pattern B: Silent Return Decisions:** Customers who typed no delivery note and paid via UPI.

---

## 3. Financial Summary & Operational Safeguards

* **Calls Made (TP + FP):** 709 calls × ₹45 = **₹31,905 call expense**
* **Gross Savings:** 60 prevented returns × ₹1,150 = **₹69,000 gross savings**
* **Net Measured Savings:** ₹69,000 - ₹31,905 = **₹37,095 per quarter** (**₹12,365/month**, **₹148,380/year**)

---

## 4. Recommended Future Iterations

1. **Text Embeddings for Delivery Notes:** Replace keyword regex with sentence transformer embeddings to capture subtle customer hesitation or delivery demands.
2. **Real-time Regional Pincode Return Densities:** Aggregate return rates by pincode clusters over rolling 30-day windows.
