"""
Main CLI Application for Day 1 Task:
Comparing Plain Chatbot, Rule-Based Workflow, and AI Agent.
"""

import sys
import os
import json
from src.plain_chatbot import PlainChatbot
from src.rule_based_workflow import RuleBasedWorkflow
from src.ai_agent import AIAgent

def run_comparison(user_query: str):
    print("=" * 80)
    print(f"USER QUERY: \"{user_query}\"")
    print("=" * 80)

    # 1. Plain Chatbot
    print("\n" + "-" * 40)
    print("PARADIGM 1: PLAIN CHATBOT (LLM Alone)")
    print("-" * 40)
    chatbot = PlainChatbot()
    res_chat = chatbot.handle_request(user_query)
    print(f"Private Data Access: {res_chat['has_private_data_access']}")
    print(f"Tools Used:          {res_chat['tools_used']}")
    print(f"Response:\n{res_chat['response']}")

    # 2. Rule-Based Workflow
    print("\n" + "-" * 40)
    print("PARADIGM 2: RULE-BASED WORKFLOW (No LLM)")
    print("-" * 40)
    workflow = RuleBasedWorkflow()
    res_rule = workflow.handle_request(user_query)
    print(f"Private Data Access: {res_rule['has_private_data_access']}")
    print(f"Tools Executed:      {res_rule['tools_used']}")
    print(f"Response:\n{res_rule['response']}")

    # 3. AI Agent
    print("\n" + "-" * 40)
    print("PARADIGM 3: AI AGENT (LLM + Tools + Loop)")
    print("-" * 40)
    agent = AIAgent()
    res_agent = agent.handle_request(user_query)
    print(f"Private Data Access: {res_agent['has_private_data_access']}")
    print(f"Tools Used:          {res_agent['tools_used']}")
    print(f"Loop Iterations:     {res_agent['total_iterations']}")
    print("\nTrajectory:")
    for step in res_agent["trajectory"]:
        if step['action'] != "FINAL_ANSWER":
            print(f"  Loop {step['iteration']}: Thought -> {step['thought']}")
            print(f"           Action  -> {step['action']}")
            print(f"           Obs     -> {step['observation'].get('status', 'ok')}")
    print(f"\nFinal Response:\n{res_agent['final_response']}")
    print("=" * 80)

if __name__ == "__main__":
    test_queries = [
        "I bought an Ultra Wireless Headset under order #ORD-9482. Can I return it, what will my refund be, and can you initiate a return for me?",
        "My keyboard arrived broken yesterday! Order is ORD-7721. What should I do?"
    ]
    
    query = sys.argv[1] if len(sys.argv) > 1 else test_queries[0]
    run_comparison(query)
