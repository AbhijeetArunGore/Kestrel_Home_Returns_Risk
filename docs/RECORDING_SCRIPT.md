# Three-Minute Screen Recording Script — Kestrel Home Returns Risk

**Target Duration:** 3 minutes (180 seconds)  
**Format:** Live Screen & Voice Walkthrough (No Slides)  

---

### Timeline & Narration Script

#### **0:00 – 0:25 (Problem & Data Pack Context)**
> *"Hello, I'm presenting the Kestrel Home Product Returns Risk system. Kestrel operates D2C and partner channels in India with ~700 orders/month. Returns cost ₹1,150 each. Our goal is to assess pre-dispatch return risk to save money without disrupting good customers. The data pack includes 15 months of historical orders, 3 months of unlabelled test orders, customer profiles, product specs, and Ops Policy v4.1."*

#### **0:25 – 0:55 (Leakage Auditing & Data Quality)**
> *"First action was inspecting data hygiene. I discovered that features like `pickup_scheduled_at` and `last_service_event_type == REVERSE_PICKUP` are post-dispatch logs—they are 100% missing in the test set. Using them would cause massive target leakage, so I stripped them. I also found that October 2025 festive orders had a 100x payment gateway error where order values were stored in paise instead of rupees, which my data pipeline automatically cleans."*

#### **0:55 – 1:35 (Evaluation & Financial Trade-Off)**
> *"Rather than blindly pursuing the client's 95% accuracy ask—which on an 11.5% return dataset can be achieved by predicting 'no return' for everything—I built a chronological validation split predicting April-June 2026. The Logistic Regression pipeline achieves a 0.7807 ROC-AUC and 0.4033 PR-AUC. At threshold 0.40, it catches 76.7% of returns. Pushing for confirmation calls (₹45/call) rather than holding dispatch prevents 66 returns/quarter, yielding net savings of ₹37,740 per quarter."*

#### **1:35 – 2:20 (Live API & UI Assessment Demo)**
> *"Here is the working Streamlit UI connected to the FastAPI backend. Let's load a high-risk sample order—a COD marketplace purchase with a prior return history. Clicking 'Assess Return Risk' sends the JSON payload to `/predict`. The API returns a 72% probability, 'High Risk' band, and recommends a Priority Confirmation Call, listing the top 3 human-readable reasons."*

#### **2:20 – 2:50 (Submission Verification & Automated Tests)**
> *"Here is `predictions.csv` generated at the project root. Running `python scripts/predict_batch.py` validates all 2,096 test rows against `sample_submission.csv`. And running `pytest -v` executes our automated test suite covering data pipeline, leakage safeguards, model inference, and API error codes."*

#### **2:50 – 3:00 (Key Limitation & Handover)**
> *"Main limitation: Delivery notes use keyword parsing; upgrading to NLP embeddings is the next step. Everything runs cleanly from `README.md` with zero paid API dependencies. Thank you!"*
