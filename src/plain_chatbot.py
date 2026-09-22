"""
Paradigm 1: Plain Chatbot (LLM Alone)

Characteristics:
- Uses ONLY an LLM prompt/parametric memory.
- NO access to private data (private_store_db.json).
- NO tools or API function calls.
- NO execution loop or state updates.
"""

import os
from typing import Dict, Any

class PlainChatbot:
    """
    A plain LLM chatbot that attempts to respond to user requests using generic language model outputs.
    Has no access to private customer or order databases and no tools to perform actions.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    def handle_request(self, user_query: str) -> Dict[str, Any]:
        """
        Processes a user query strictly using model text generation without private data or tools.
        """
        # Simulated responses demonstrating LLM-only capability vs private data limitation
        query_lower = user_query.lower()
        
        if "ord-9482" in query_lower:
            response = (
                "Hello! Thank you for reaching out to TechGear Support.\n\n"
                "Regarding your request to return order #ORD-9482:\n"
                "As an AI chatbot, I do not have access to TechGear's internal database or your private account records. "
                "Therefore, I cannot look up order #ORD-9482, verify your purchase date, check your VIP refund policy, or initiate a return in our system.\n\n"
                "Generally, items can be returned within 30 days if in original packaging. "
                "Please visit our support portal manually or contact human support to process your return."
            )
        elif "ord-7721" in query_lower or "broken" in query_lower or "damaged" in query_lower:
            response = (
                "I am so sorry to hear that your item arrived damaged!\n\n"
                "I am a generic AI assistant without access to order databases or shipping systems. "
                "I cannot look up order #ORD-7721 or send out a replacement item for you.\n\n"
                "I recommend taking photos of the damaged box and contacting claims@techgear.example.com."
            )
        else:
            response = (
                "Welcome to TechGear Customer Service!\n\n"
                "I can answer general questions about consumer electronics, warranty guidelines, and basic store FAQs. "
                "However, I cannot view private account data or execute transactions for you."
            )

        return {
            "paradigm": "Plain Chatbot (LLM Alone)",
            "query": user_query,
            "has_private_data_access": False,
            "tools_used": [],
            "loop_count": 1,
            "response": response,
            "limitations_noted": [
                "Cannot read private customer or order database",
                "Cannot perform database state updates or initiate returns",
                "May hallucinate or provide overly generic policy advice"
            ]
        }

if __name__ == "__main__":
    bot = PlainChatbot()
    res = bot.handle_request("I bought an Ultra Wireless Headset under order #ORD-9482. Can I return it, what will my refund be, and can you initiate a return for me?")
    print("=== PLAIN CHATBOT OUTPUT ===")
    print(res["response"])
