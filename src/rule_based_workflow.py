"""
Paradigm 2: Rule-Based Workflow (No LLM)

Characteristics:
- Predefined procedural rules and conditional logic (if/else, regex).
- NO LLM involved for semantic understanding or reasoning.
- Direct read/write access to private_store_db.json via strict parameters.
- Fast, deterministic execution for structured inputs.
- Extremely fragile when dealing with informal, conversational, or ambiguous queries.
"""

import re
from typing import Dict, Any
try:
    from src.tools import get_order_details, check_return_eligibility, process_return_request, issue_replacement_order
except ImportError:
    from tools import get_order_details, check_return_eligibility, process_return_request, issue_replacement_order

class RuleBasedWorkflow:
    """
    A rule-based workflow engine that processes customer requests using predefined keyword rules and regex matching.
    """

    def handle_request(self, user_query: str) -> Dict[str, Any]:
        """
        Processes request using rigid pattern rules.
        """
        # Step 1: Parse input string using explicit Regex patterns
        order_match = re.search(r"ORD-\d{4}", user_query, re.IGNORECASE)
        
        if not order_match:
            return {
                "paradigm": "Rule-Based Workflow (No LLM)",
                "query": user_query,
                "status": "FAILED_TO_PARSE",
                "response": (
                    "ERROR: Invalid Request Format.\n"
                    "The system requires an exact order number matching pattern 'ORD-XXXX'. "
                    "No LLM intelligence is available to infer context from your query."
                ),
                "has_private_data_access": True,
                "tools_used": [],
                "limitations_noted": ["Fails completely when input does not conform to expected regex pattern"]
            }

        order_id = order_match.group(0).upper()
        query_lower = user_query.lower()

        # Step 2: Exact Rule evaluation
        tools_executed = []
        
        # Rule Branch 1: Explicit Return Command
        if "return" in query_lower:
            tools_executed.append("check_return_eligibility")
            eligibility = check_return_eligibility(order_id)
            
            if eligibility["status"] == "error":
                return {
                    "paradigm": "Rule-Based Workflow (No LLM)",
                    "query": user_query,
                    "response": f"ERROR: Order {order_id} not found in database.",
                    "tools_used": tools_executed
                }

            if eligibility["is_eligible"]:
                tools_executed.append("process_return_request")
                res = process_return_request(order_id, reason="Rule-based return pipeline trigger")
                response = (
                    f"SUCCESS [Rule Engine]: Order {order_id} processed.\n"
                    f"- Item: {eligibility['item_name']}\n"
                    f"- Days Elapsed: {eligibility['days_since_delivery']}/30\n"
                    f"- Restocking Fee: ${eligibility['restocking_fee']} (VIP Status: {eligibility['customer_tier']})\n"
                    f"- Refund Queued: ${eligibility['estimated_refund']}\n"
                    f"- Tracking Label: {res['return_label_tracking']}"
                )
            else:
                response = (
                    f"DENIED [Rule Engine]: Return for {order_id} is ineligible.\n"
                    f"Reason: {eligibility['reason_if_ineligible']}"
                )

        # Rule Branch 2: Replacement Command for Damaged Goods
        elif "damaged" in query_lower or "broken" in query_lower or "replacement" in query_lower:
            tools_executed.append("issue_replacement_order")
            res = issue_replacement_order(order_id, reason="Rule trigger: damaged item reported")
            if res["status"] == "success":
                response = (
                    f"SUCCESS [Rule Engine]: Replacement Issued.\n"
                    f"- Order ID: {res['replacement_order_id']}\n"
                    f"- Item: {res['item_name']}\n"
                    f"- Tracking: {res['expedited_tracking']}"
                )
            else:
                response = f"ERROR [Rule Engine]: {res['message']}"

        # Unmatched Intent Rule Branch
        else:
            response = (
                f"UNHANDLED INTENT: Detected Order ID '{order_id}', but could not map intent to predefined action keywords "
                f"(expected 'return', 'damaged', 'broken', or 'replacement').\n"
                f"No LLM is present to interpret human intent."
            )

        return {
            "paradigm": "Rule-Based Workflow (No LLM)",
            "query": user_query,
            "order_parsed": order_id,
            "has_private_data_access": True,
            "tools_used": tools_executed,
            "response": response,
            "limitations_noted": [
                "Rigid intent classification based purely on exact string matching",
                "Cannot handle complex edge cases or nuance not explicitly coded by developer",
                "Zero conversational intelligence or contextual explanation capability"
            ]
        }

if __name__ == "__main__":
    workflow = RuleBasedWorkflow()
    print("=== RULE-BASED WORKFLOW TEST 1 (Structured) ===")
    res1 = workflow.handle_request("COMMAND: RETURN ORD-9482")
    print(res1["response"])

    print("\n=== RULE-BASED WORKFLOW TEST 2 (Informal/Ambiguous) ===")
    res2 = workflow.handle_request("Hey there, my device is having issues. I bought it a while ago under ORD-9482.")
    print(res2["response"])
