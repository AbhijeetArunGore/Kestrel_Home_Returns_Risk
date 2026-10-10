# Failure Analysis & Known Limitations — Kestrel Home Returns Risk

**Author:** Senior AI / Systems Engineer  
**Date:** October 2026  

---

## 1. Error Matrix Breakdown

Evaluation conducted on held-out validation batch (2,126 orders, 245 actual returns):

| Classification Type | Count | Operational Impact |
| :--- | :--- | :--- |
| **True Positives (TP)** | 188 | High-risk return orders correctly flagged. Triggers confirmation calls (costing ₹45/call) and prevents ~66 returns (saving ₹75,900 gross). |
| **True Negatives (TN)** | 1,221 | Low-risk orders correctly processed without operational delay or intervention. |
| **False Positives (FP)** | 660 | Non-returned orders flagged for confirmation calls. Incurs ₹45 call cost (total ₹29,700), but does NOT trigger order cancellation risk because dispatch is not blocked. |
| **False Negatives (FN)** | 57 | Returned orders missed by model pre-dispatch. Result in standard ₹1,150 return cost per order. |

---

## 2. Failure Case Taxonomy

### 2.1 False Positive Characterization (Flagged non-returns)
* **Pattern A: Heavy Promotional Discounts (e.g. >20% checkout discount):** Model flags high discount items due to historical correlation with impulse purchases, but prepaid app users frequently retain bargain purchases.
* **Pattern B: First-time Marketplace Orders:** Marketplace sales tag elevated risk, but many represent legitimate one-time buyers.
* **Mitigation:** Making ₹45 confirmation calls instead of holding dispatch ensures False Positives cost only ₹45 rather than ₹240 in customer cancellation penalties.

### 2.2 False Negative Characterization (Missed returns)
* **Pattern A: First-time Prepaid App Buyers:** Customers with 0 prior order history who purchase standard air fryers or mixer grinders prepaid. Pre-dispatch metadata contains 0 risk signals, but post-delivery quality preferences or transit damage trigger returns.
* **Pattern B: Silent Return Decisions:** Customers who typed no delivery note and paid via UPI.

---

## 3. Recommended Future Iterations

1. **Text Embeddings for Delivery Notes:** Replace keyword regex with sentence transformer embeddings to capture subtle customer hesitation or delivery demands.
2. **Real-time Regional Pincode Return Densities:** Aggregate return rates by pincode clusters over rolling 30-day windows.
