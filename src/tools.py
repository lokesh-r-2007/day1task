"""
Tools Module for TechGear Private Database Interactions.
Provides atomic functions to query private store data, calculate return eligibility,
process return requests, and issue item replacements.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "private_store_db.json")


def _load_db() -> Dict[str, Any]:
    """Reads the private JSON database from disk."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at {DB_PATH}")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: Dict[str, Any]) -> None:
    """Persists updated state back to the private JSON database."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_order_details(order_id: str) -> Dict[str, Any]:
    """
    Retrieve private order records from the store database by order_id.
    
    Args:
        order_id: The unique identifier for the order (e.g., 'ORD-9482').
    """
    db = _load_db()
    orders = db.get("orders", {})
    order_key = order_id.strip().upper()
    if order_key in orders:
        return {"status": "success", "order": orders[order_key]}
    return {"status": "error", "message": f"Order '{order_id}' not found in private database."}


def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """
    Retrieve private customer information, including tier (VIP vs Standard) and order count.
    
    Args:
        customer_id: The unique customer identifier (e.g., 'CUST-101').
    """
    db = _load_db()
    customers = db.get("customers", {})
    cust_key = customer_id.strip().upper()
    if cust_key in customers:
        return {"status": "success", "customer": customers[cust_key]}
    return {"status": "error", "message": f"Customer '{customer_id}' not found."}


def check_return_eligibility(order_id: str, current_date_str: str = "2026-09-22") -> Dict[str, Any]:
    """
    Evaluates whether an order is eligible for return based on policy rules (30-day window, customer tier).
    
    Args:
        order_id: The order ID to inspect.
        current_date_str: Current reference date in YYYY-MM-DD format.
    """
    order_res = get_order_details(order_id)
    if order_res["status"] == "error":
        return order_res

    order = order_res["order"]
    db = _load_db()
    policy = db.get("return_policy", {})

    delivery_date = datetime.strptime(order["delivery_date"], "%Y-%m-%d")
    current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    days_elapsed = (current_date - delivery_date).days

    cust_res = get_customer_info(order["customer_id"])
    tier = "Standard"
    if cust_res["status"] == "success":
        tier = cust_res["customer"].get("tier", "Standard")

    max_days = policy.get("max_return_window_days", 30)
    is_within_window = days_elapsed <= max_days

    # Restocking fee calculation
    fee_pct = policy.get("restocking_fee_percentage", 10.0)
    if tier == "VIP" and policy.get("vip_restocking_fee_waived", True):
        restocking_fee = 0.0
    else:
        restocking_fee = round(order["price"] * (fee_pct / 100.0), 2)

    estimated_refund = round(order["price"] - restocking_fee, 2)

    return {
        "status": "success",
        "order_id": order_id,
        "item_name": order["item_name"],
        "days_since_delivery": days_elapsed,
        "max_return_window_days": max_days,
        "is_eligible": is_within_window,
        "customer_tier": tier,
        "item_price": order["price"],
        "restocking_fee": restocking_fee,
        "estimated_refund": estimated_refund,
        "reason_if_ineligible": "" if is_within_window else f"Order delivered {days_elapsed} days ago, exceeding the {max_days}-day return limit."
    }


def process_return_request(order_id: str, reason: str = "Customer return request") -> Dict[str, Any]:
    """
    Processes a return for an order: updates order status in DB, logs return request, and restores stock.
    
    Args:
        order_id: The order ID to process.
        reason: Explanation for the return.
    """
    eligibility = check_return_eligibility(order_id)
    if eligibility["status"] == "error":
        return eligibility
    if not eligibility["is_eligible"]:
        return {
            "status": "denied",
            "message": f"Return denied for {order_id}: {eligibility['reason_if_ineligible']}"
        }

    db = _load_db()
    order_key = order_id.strip().upper()
    order = db["orders"][order_key]

    if order.get("return_requested"):
        return {
            "status": "warning",
            "order_id": order_id,
            "refund_amount": order.get("refund_amount", eligibility["estimated_refund"]),
            "return_label_tracking": f"TRK-RET-{order_id}-99",
            "message": f"Return for order {order_id} has already been initiated previously."
        }

    # Perform mutation
    order["return_requested"] = True
    order["status"] = "Return Initiated"
    order["refund_amount"] = eligibility["estimated_refund"]
    order["return_reason"] = reason

    # Update inventory
    item_id = order.get("item_id")
    if item_id in db["inventory"]:
        db["inventory"][item_id]["stock"] += order.get("quantity", 1)

    _save_db(db)

    return {
        "status": "success",
        "order_id": order_id,
        "refund_amount": eligibility["estimated_refund"],
        "return_label_tracking": f"TRK-RET-{order_id}-99",
        "message": f"Return request processed successfully for {order['item_name']}. Refund of ${eligibility['estimated_refund']} queued."
    }


def issue_replacement_order(order_id: str, reason: str = "Damaged upon arrival") -> Dict[str, Any]:
    """
    Issues a zero-cost replacement shipment for damaged or defective items.
    
    Args:
        order_id: The order ID to replace.
        reason: Reason for replacement.
    """
    db = _load_db()
    order_key = order_id.strip().upper()
    if order_key not in db["orders"]:
        return {"status": "error", "message": f"Order '{order_id}' not found."}

    order = db["orders"][order_key]
    item_id = order["item_id"]

    if db["inventory"].get(item_id, {}).get("stock", 0) < 1:
        return {"status": "error", "message": f"Item {order['item_name']} is out of stock. Cannot issue immediate replacement."}

    # Decrement stock for replacement
    db["inventory"][item_id]["stock"] -= 1
    order["status"] = "Replacement Order Expedited"
    order["replacement_issued"] = True
    _save_db(db)

    replacement_id = f"RPL-{order_id}"
    return {
        "status": "success",
        "replacement_order_id": replacement_id,
        "item_name": order["item_name"],
        "shipping_address": order["shipping_address"],
        "expedited_tracking": f"TRK-EXP-{replacement_id}-01",
        "message": f"Replacement order {replacement_id} created for '{order['item_name']}'. Shipping to {order['shipping_address']} via 2-Day Air."
    }


# Export available tools manifest for LLM function calling / reasoning agent
AVAILABLE_TOOLS = {
    "get_order_details": get_order_details,
    "get_customer_info": get_customer_info,
    "check_return_eligibility": check_return_eligibility,
    "process_return_request": process_return_request,
    "issue_replacement_order": issue_replacement_order
}
