# Project Assumptions & Data Evidence — Kestrel Home Returns Risk

**Author:** Senior AI / ML / Systems Engineer  
**Date:** October 2026  
**Client:** Ritu Deshpande (Head of D2C Operations), Farhan Sheikh (Finance Controller), Meenal Joshi (Service Desk Manager), Tanmay Kulkarni (Data & IT Admin)  
**Company:** Kestrel Home Appliances (Pune, India)  

---

## 1. Executive Summary & Core Decisions

This document details all technical decisions, dataset evidence, leakage exclusions, operational trade-offs, and financial parameters for the Kestrel Home Product Return Risk System.

All decisions are grounded in direct empirical analysis of `train.csv`, `test_unlabelled.csv`, `customers.csv`, `products.csv`, `ops-policy.pdf`, and `email-thread.txt`.

---

## 2. Dataset Audit & Data Integrity

### 2.1 File Dimensions & Schemas
* `train.csv`: 11,155 total rows, 19 columns. 10,504 unique `order_id`s. Date range: April 1, 2025 to June 30, 2026 (15 months).
* `test_unlabelled.csv`: 2,096 total rows, 18 columns. 2,096 unique `order_id`s. Date range: July 1, 2026 to September 30, 2026 (3 months).
* `customers.csv`: 9,000 unique records (`customer_id`, `city`, `state`, `signup_date`, `shield_member`). 100% join key match with train and test orders.
* `products.csv`: 21 unique SKUs (`sku`, `family`, `model_name`, `list_price_inr`, `warranty_months`, `launch_date`). 100% join key match with train and test orders.
* `sample_submission.csv`: 2,096 rows (`order_id`, `score`). Matches test `order_id` sequence exactly.

### 2.2 Target Class Distribution
* Positive class (`returned = 1`): 1,267 rows (**11.36%** return rate).
* Negative class (`returned = 0`): 9,888 rows (**88.64%** non-returned rate).
* **Imbalance Warning:** A trivial baseline that predicts `returned = 0` for all orders achieves **88.64% accuracy** while catching 0 returns and delivering 0 rupees in business value.

### 2.3 Order Value Anomaly (October 2025 Gateway Error)
* **Evidence:** In `train.csv` for October 2025 (748 rows), the mean `order_value_inr` was ₹786,853 with a maximum of ₹5,880,204. In all other 14 months, the mean was ~₹8,000.
* **Root Cause:** Corroborated by Tanmay Kulkarni's email (*"the October festive orders went through the new payment gateway, I haven't checked those"*). The gateway multiplied `order_value_inr` by 100 (storing paise as rupees).
* **Audit Result:** Comparing `order_value_inr` against expected gross price (`list_price_inr * qty * (1 - discount_pct/100)`) shows an exact ratio of `100.00` for all 748 October 2025 rows, and `1.00` for all other rows in train and test.
* **Decision:** `order_value_inr` is corrected for October 2025 rows by dividing by 100 (or recalculated as `list_price_inr * qty * (1 - discount_pct/100)`).

### 2.4 Duplicate Records & Partner Feed Re-Imports
* **Evidence:** `train.csv` contains 1,302 duplicate rows (651 order pairs present in both `source == 'crm'` and `source == 'partner_feed'`).
* **Root Cause:** Tanmay's email notes: *"partner-outlet orders get re-imported from the partner feed so you'll see some orders twice"*.
* **Decision:** Training data is deduplicated by `order_id` (retaining 10,504 unique order records) prior to splitting to prevent duplicate-order data leakage across train and validation sets.

### 2.5 Walk-in Outlet Pincodes (`000000`)
* **Evidence:** 889 rows in train and 176 rows in test have `delivery_pincode == 0`.
* **Root Cause:** README.txt confirms `000000` is the default code for walk-in partner outlet orders where no address was captured.
* **Decision:** Flagged using a binary indicator `is_walkin_pincode = (delivery_pincode == 0)`.

---

## 3. Target Leakage Exclusions

An order return prediction system deployed at the warehouse dispatch point sees orders **BEFORE** dispatch. Any feature generated after dispatch or during/after return processing must be excluded from model training.

### 3.1 Excluded Features
1. `pickup_scheduled_at`:
   * **Evidence:** 100% missing in `test_unlabelled.csv` (2,096/2,096 nulls). In `train.csv`, 91.6% of rows with a non-null `pickup_scheduled_at` were returned. Logistics creates this timestamp only after a return request is submitted.
2. `last_service_event_type`:
   * **Evidence:** In `train.csv`, 789 rows have `last_service_event_type == 'REVERSE_PICKUP'` (100% returned). In `test_unlabelled.csv`, only pre-dispatch values (`NONE` and `INSTALL_BOOKED`) exist. Post-dispatch events (`REVERSE_PICKUP`, `DEMO_DONE`, `INSTALL_DONE`, `TECH_VISIT`) occur after dispatch.
   * **Decision:** Excluded from feature set to ensure strict deployment fidelity.

---

## 4. Financial & Operational Parameters (Ops Policy v4.1)

| Parameter | Value | Source / Rationale |
| :--- | :--- | :--- |
| **Cost per Returned Order** | **₹1,150** | Policy §4 & Finance Controller (Farhan Sheikh). Includes reverse logistics, QC inspection, repacking, write-down. |
| **Pre-Dispatch Call Cost** | **₹45** | Policy §4. Outsourced confirmation call cost per completed call. |
| **Call Success Rate** | **35%** | Policy §7. Pre-dispatch calls prevent 35% of returns on called orders (resolving model/address errors & buyer's remorse). |
| **Order Hold Cancellation Risk** | **12%** | Policy §7. Orders held >24 hrs at dispatch are cancelled by customers 12% of the time. |
| **Average Profit Margin Loss on Cancellation** | **~₹2,000** | Derived from average order value (~₹8,000) and standard D2C appliance gross margin (~25%). |
| **Shield Member Strategy** | Free returns & 24m warranty | Policy §6 & Service Manager (Meenal Joshi). Highest LTV segment (~22% of customers). Indiscriminate holds risk customer churn. |

---

## 5. Evaluation & Validation Strategy

1. **Validation Split:** Chronological split.
   * **Train set:** Orders placed from 2025-04-01 to 2026-03-31 (8,409 orders).
   * **Validation set:** Orders placed from 2026-04-01 to 2026-06-30 (2,095 orders).
   * Approximates real-world deployment where historical 12 months predict the upcoming 3 months (`test_unlabelled.csv`).
2. **Primary Ranking Metric:** ROC-AUC & PR-AUC (Precision-Recall Area Under Curve).
3. **Primary Financial Metric:** Net Financial Savings (INR) calculated under operational decision policies (Confirmation Call Pilot vs. Order Hold Policy).
