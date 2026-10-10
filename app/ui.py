import os
import sys
import requests
import streamlit as st

st.set_page_config(
    page_title="Kestrel Home — Returns Risk",
    page_icon="📦",
    layout="wide"
)

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.title("📦 Kestrel Home — Product Returns Risk Assessment")
st.markdown("""
*Pre-dispatch Return Risk Intelligence for D2C Appliance Fulfillment.*  
This system evaluates incoming orders before dispatch to flag return risks, recommend pre-dispatch confirmation calls, and prevent unnecessary logistics costs.
""")

st.sidebar.header("⚙️ Configuration")
api_base_url = st.sidebar.text_input("Backend API Base URL", value=API_URL)

# Health Check Indicator
try:
    health_resp = requests.get(f"{api_base_url}/health", timeout=3)
    if health_resp.status_code == 200:
        st.sidebar.success("🟢 API Connected & Ready")
    else:
        st.sidebar.warning("🟡 API Status Degraded")
except Exception:
    st.sidebar.error("🔴 API Connection Failed (Start backend API with `python -m uvicorn app.api:app --reload`)")

st.sidebar.markdown("---")
st.sidebar.markdown("### Sample Record Presets")
preset = st.sidebar.radio(
    "Load Sample Preset Order:",
    ["Custom Order", "High Risk Order (COD + Returns History)", "Low Risk Order (Prepaid + Shield Member)"]
)

# Preset Values
default_values = {
    "order_id": "KO2609101",
    "order_placed_at": "2026-08-10 11:20:00",
    "customer_id": "KC100045",
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
    "delivery_note": "Deliver during daytime hours"
}

if preset == "High Risk Order (COD + Returns History)":
    default_values.update({
        "order_id": "KO2609888",
        "customer_id": "KC100120",
        "payment_mode": "cod",
        "sales_channel": "marketplace",
        "discount_pct": 25.0,
        "customer_prior_orders": 3,
        "customer_prior_returns": 2,
        "delivery_note": "Urgent delivery needed asap"
    })
elif preset == "Low Risk Order (Prepaid + Shield Member)":
    default_values.update({
        "order_id": "KO2609111",
        "customer_id": "KC100005",
        "payment_mode": "prepaid_upi",
        "sales_channel": "app",
        "discount_pct": 5.0,
        "customer_prior_orders": 5,
        "customer_prior_returns": 0,
        "delivery_note": ""
    })

st.subheader("1. Order Details Entry")

col1, col2, col3 = st.columns(3)

with col1:
    order_id = st.text_input("Order ID", value=default_values["order_id"])
    order_placed_at = st.text_input("Order Placed At (IST)", value=default_values["order_placed_at"])
    customer_id = st.text_input("Customer ID", value=default_values["customer_id"])
    sku = st.selectbox("Product SKU", ["KH-AF-01", "KH-AF-02", "KH-MG-01", "KH-WP-01", "KH-RV-01"], index=0)
    sales_channel = st.selectbox("Sales Channel", ["app", "web", "marketplace", "partner_outlet"], index=0)

with col2:
    payment_mode = st.selectbox("Payment Mode", ["prepaid_upi", "prepaid_card", "cod", "emi"], index=0)
    discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=default_values["discount_pct"])
    qty = st.number_input("Quantity", min_value=1, value=default_values["qty"])
    order_value_inr = st.number_input("Order Value (INR)", min_value=0.0, value=default_values["order_value_inr"])
    promised_delivery_days = st.number_input("Promised Delivery Days", min_value=1, value=default_values["promised_delivery_days"])

with col3:
    delivery_pincode = st.number_input("Delivery Pincode", min_value=0, value=default_values["delivery_pincode"])
    is_gift = st.selectbox("Is Gift?", ["N", "Y"], index=0)
    customer_prior_orders = st.number_input("Customer Prior Orders", min_value=0, value=default_values["customer_prior_orders"])
    customer_prior_returns = st.number_input("Customer Prior Returns", min_value=0, value=default_values["customer_prior_returns"])
    delivery_note = st.text_area("Delivery Note", value=default_values["delivery_note"])

st.markdown("---")

if st.button("📊 Assess Return Risk", type="primary", use_container_width=True):
    payload = {
        "order_id": order_id,
        "order_placed_at": order_placed_at,
        "customer_id": customer_id,
        "sku": sku,
        "sales_channel": sales_channel,
        "payment_mode": payment_mode,
        "discount_pct": float(discount_pct),
        "qty": int(qty),
        "order_value_inr": float(order_value_inr),
        "promised_delivery_days": int(promised_delivery_days),
        "delivery_pincode": int(delivery_pincode),
        "is_gift": is_gift,
        "customer_prior_orders": int(customer_prior_orders),
        "customer_prior_returns": int(customer_prior_returns),
        "delivery_note": delivery_note if delivery_note else None,
        "source": "crm"
    }

    with st.spinner("Evaluating pre-dispatch risk model..."):
        try:
            resp = requests.post(f"{api_base_url}/predict", json=payload, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
                st.subheader("2. Risk Assessment Results")

                prob = result["return_probability"]
                band = result["risk_band"]
                decision = result["decision"]

                res_col1, res_col2, res_col3 = st.columns(3)

                with res_col1:
                    st.metric("Estimated Return Probability", f"{prob:.1%}")

                with res_col2:
                    if band == "High Risk":
                        st.error(f"**Risk Category:** {band}")
                    elif band == "Medium Risk":
                        st.warning(f"**Risk Category:** {band}")
                    else:
                        st.success(f"**Risk Category:** {band}")

                with res_col3:
                    st.info(f"**Decision Recommendation:** {decision}")

                st.markdown("### 💡 Recommended Operational Action")
                st.write(result["recommended_action"])

                st.markdown("### 🔍 Key Risk Factors (Top Reasons)")
                for idx, reason in enumerate(result["top_reasons"], 1):
                    st.markdown(f"**{idx}.** {reason}")

                st.caption(f"⚠️ *{result['disclaimer']} (Model Version: {result['model_version']})*")

            else:
                st.error(f"API Error ({resp.status_code}): {resp.text}")

        except Exception as e:
            st.error(f"Failed to connect to backend API at {api_base_url}. Error: {e}")
