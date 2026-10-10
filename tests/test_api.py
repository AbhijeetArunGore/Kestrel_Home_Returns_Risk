import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath('.'))

from app.api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "model_loaded" in data

def test_metadata_endpoint():
    response = client.get("/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == "1.0.0"
    assert data["training_samples"] == 10504

def test_predict_valid_order():
    payload = {
        "order_id": "TEST_ORDER_001",
        "order_placed_at": "2026-07-15 14:30:00",
        "customer_id": "KC100001",
        "sku": "KH-AF-01",
        "sales_channel": "app",
        "payment_mode": "prepaid_upi",
        "discount_pct": 10.0,
        "qty": 1,
        "order_value_inr": 4500.0,
        "promised_delivery_days": 3,
        "delivery_pincode": 411001,
        "is_gift": "N",
        "customer_prior_orders": 2,
        "customer_prior_returns": 0,
        "delivery_note": "Handle with care",
        "source": "crm"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "TEST_ORDER_001"
    assert 0.0 <= data["return_probability"] <= 1.0
    assert data["risk_band"] in ["Low Risk", "Medium Risk", "High Risk"]
    assert "decision" in data
    assert len(data["top_reasons"]) > 0

def test_predict_missing_required_field():
    payload = {
        "order_id": "TEST_ORDER_002"
        # Missing required order_value_inr, customer_id, sku, etc.
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Pydantic validation error

def test_predict_invalid_data_type():
    payload = {
        "order_id": "TEST_ORDER_003",
        "order_placed_at": "2026-07-15 14:30:00",
        "customer_id": "KC100001",
        "sku": "KH-AF-01",
        "discount_pct": "INVALID_NUMBER_STRING",
        "order_value_inr": 4500.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
