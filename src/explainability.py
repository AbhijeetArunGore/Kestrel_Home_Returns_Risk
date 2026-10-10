import pandas as pd
import numpy as np
from typing import Dict, Any, List

def get_risk_band_and_decision(prob: float, threshold: float = 0.40) -> Dict[str, str]:
    """Categorize risk probability into transparent business risk band and action decision."""
    if prob < 0.25:
        return {
            "risk_band": "Low Risk",
            "decision": "Normal Processing",
            "recommended_action": "Proceed with standard warehouse dispatch. No operational intervention required."
        }
    elif prob < 0.50:
        return {
            "risk_band": "Medium Risk",
            "decision": "Standard Confirmation Call",
            "recommended_action": f"Initiate a pre-dispatch confirmation call (Cost: ₹45) to verify order details and delivery readiness."
        }
    else:
        return {
            "risk_band": "High Risk",
            "decision": "Priority Review & Confirmation Call",
            "recommended_action": "Flag for urgent pre-dispatch phone verification. Verify model selection, address accuracy, and payment commitment."
        }

def explain_prediction(order_dict: Dict[str, Any], prob: float) -> List[str]:
    """Generate human-readable, plain-language business reasons for the prediction."""
    reasons = []

    # 1. Customer Prior History
    prior_orders = float(order_dict.get("customer_prior_orders", 0))
    prior_returns = float(order_dict.get("customer_prior_returns", 0))
    if prior_returns > 0:
        rate = (prior_returns / max(prior_orders, 1)) * 100
        reasons.append(f"Customer has a history of returns ({int(prior_returns)} returns across {int(prior_orders)} past orders, {rate:.0f}% return rate).")
    elif prior_orders == 0:
        reasons.append("First-time customer with no prior transaction or return history.")

    # 2. Payment Mode & COD Risk
    pm = str(order_dict.get("payment_mode", "")).lower()
    if pm == "cod":
        reasons.append("Cash on Delivery (COD) payment mode carries higher pre-dispatch refusal risk.")
    elif pm == "emi":
        reasons.append("EMI financing transaction structure.")

    # 3. Discount Percentage
    discount = float(order_dict.get("discount_pct", 0))
    if discount >= 20.0:
        reasons.append(f"High promotional discount applied ({discount:.0f}% checkout discount).")

    # 4. Walk-in Pincode / Missing Address
    pincode = str(order_dict.get("delivery_pincode", "0"))
    if pincode in ["0", "000000"]:
        reasons.append("Walk-in partner outlet order with no captured delivery address (default pincode 000000).")

    # 5. Order Value & High-End Appliances
    val = float(order_dict.get("order_value_inr", 0))
    if val >= 15000:
        reasons.append(f"High order value appliance (₹{val:,.2f}) sensitive to post-delivery satisfaction.")

    # 6. Delivery Note Keywords
    note = str(order_dict.get("delivery_note", "") or "").lower()
    if any(k in note for k in ['urgent', 'fast', 'asap', 'quick']):
        reasons.append("Customer note requests urgent delivery, indicating tight customer timeline expectations.")
    elif len(note) > 0:
        reasons.append(f"Customer provided specific delivery instructions: '{note[:40]}...'")

    # 7. Sales Channel
    channel = str(order_dict.get("sales_channel", "")).lower()
    if channel == "marketplace":
        reasons.append("Marketplace channel sales exhibit higher return rates compared to direct app orders.")

    # 8. Shield Membership
    shield = str(order_dict.get("shield_member", "N")).upper()
    if shield == "Y":
        reasons.append("Kestrel Shield member profile (eligible for free 30-day returns).")

    # Return top 3 reasons
    if not reasons:
        reasons.append("Order parameters align closely with typical fulfillment profiles.")

    return reasons[:3]
