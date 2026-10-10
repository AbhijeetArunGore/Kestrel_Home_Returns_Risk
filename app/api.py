import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath('.'))

from src.data import load_all_datasets, clean_and_merge_data
from src.models import load_model
from src.explainability import get_risk_band_and_decision, explain_prediction

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("kestrel_api")

# Global State Container
STATE = {
    "model": None,
    "customers": None,
    "products": None
}

def initialize_service():
    """Load model artifact and reference tables into memory."""
    if STATE["model"] is None:
        try:
            STATE["model"] = load_model("models/model_pipeline.joblib")
            logger.info("Fitted model pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load fitted model artifact: {e}")

    if STATE["customers"] is None or STATE["products"] is None:
        try:
            datasets = load_all_datasets(".")
            STATE["customers"] = datasets["customers"]
            STATE["products"] = datasets["products"]
            logger.info("Reference customer and product datasets loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load reference tables: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan context manager for application startup/shutdown."""
    initialize_service()
    yield

app = FastAPI(
    title="Kestrel Home — Product Returns Risk Service",
    description="Production REST API predicting pre-dispatch return risk for D2C appliance orders.",
    version="1.0.0",
    lifespan=lifespan
)

class OrderRequest(BaseModel):
    order_id: str = Field(..., json_schema_extra={"example": "KO2609999"})
    order_placed_at: str = Field(..., json_schema_extra={"example": "2026-07-15 14:30:00"})
    customer_id: str = Field(..., json_schema_extra={"example": "KC100001"})
    sku: str = Field(..., json_schema_extra={"example": "KH-AF-01"})
    sales_channel: str = Field("app", json_schema_extra={"example": "app"})
    payment_mode: str = Field("prepaid_upi", json_schema_extra={"example": "prepaid_upi"})
    discount_pct: float = Field(0.0, ge=0.0, le=100.0, json_schema_extra={"example": 10.0})
    qty: int = Field(1, ge=1, json_schema_extra={"example": 1})
    order_value_inr: float = Field(..., ge=0.0, json_schema_extra={"example": 4500.0})
    promised_delivery_days: int = Field(3, ge=1, json_schema_extra={"example": 3})
    delivery_pincode: int = Field(411001, json_schema_extra={"example": 411001})
    is_gift: str = Field("N", json_schema_extra={"example": "N"})
    customer_prior_orders: int = Field(0, ge=0, json_schema_extra={"example": 2})
    customer_prior_returns: int = Field(0, ge=0, json_schema_extra={"example": 0})
    delivery_note: Optional[str] = Field(None, json_schema_extra={"example": "Call before delivery"})
    source: str = Field("crm", json_schema_extra={"example": "crm"})

class PredictionResponse(BaseModel):
    order_id: str
    return_probability: float
    risk_band: str
    decision: str
    recommended_action: str
    top_reasons: List[str]
    model_version: str
    disclaimer: str

@app.get("/health")
def health_check():
    """Health status and model readiness endpoint."""
    initialize_service()
    return {
        "status": "healthy" if STATE["model"] is not None else "degraded",
        "model_loaded": STATE["model"] is not None,
        "service": "Kestrel Returns Risk API",
        "version": "1.0.0"
    }

@app.get("/metadata")
def get_metadata():
    """Model version, schema parameters, and evaluation metadata."""
    return {
        "model_version": "1.0.0",
        "model_type": "LogisticRegression (Pre-Dispatch Pipeline)",
        "training_samples": 10504,
        "primary_metric": "ROC-AUC",
        "validation_roc_auc": 0.7807,
        "validation_pr_auc": 0.4033,
        "recommended_decision_threshold": 0.40,
        "financial_return_cost_inr": 1150.0,
        "confirmation_call_cost_inr": 45.0
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_order_risk(order: OrderRequest):
    """Predict return risk probability and generate operational decision guidance for a single order."""
    initialize_service()
    
    if STATE["model"] is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model pipeline artifact is not loaded or missing."
        )

    try:
        raw_dict = order.model_dump()
        single_df = pd.DataFrame([raw_dict])

        if STATE["customers"] is not None and STATE["products"] is not None:
            clean_df = clean_and_merge_data(single_df, STATE["customers"], STATE["products"], is_train=False)
        else:
            clean_df = single_df

        prob = float(STATE["model"].predict_proba(clean_df)[0, 1])

        risk_info = get_risk_band_and_decision(prob, threshold=0.40)
        reasons = explain_prediction(raw_dict, prob)

        logger.info(f"Order {order.order_id} assessed: Prob={prob:.4f}, RiskBand={risk_info['risk_band']}")

        return PredictionResponse(
            order_id=order.order_id,
            return_probability=round(prob, 4),
            risk_band=risk_info["risk_band"],
            decision=risk_info["decision"],
            recommended_action=risk_info["recommended_action"],
            top_reasons=reasons,
            model_version="1.0.0",
            disclaimer="This score is a pre-dispatch statistical risk estimate, not a guaranteed return."
        )

    except Exception as e:
        logger.error(f"Error evaluating order {order.order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing model inference: {str(e)}"
        )
