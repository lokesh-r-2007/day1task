"""
Screenshot Generator for Day 1 Task
Renders high-definition visual terminal outputs for each paradigm into the Output/ directory.
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color Palette (Modern Dark Mode Terminal UI)
BG_COLOR = (15, 23, 42)          # Slate 900
PANEL_BG = (30, 41, 59)          # Slate 800
BORDER_COLOR = (51, 65, 85)      # Slate 700
HEADER_BG = (30, 41, 59)
TEXT_WHITE = (248, 250, 252)     # Slate 50
TEXT_MUTED = (148, 163, 184)    # Slate 400
TEXT_GREEN = (52, 211, 153)      # Emerald 400
TEXT_BLUE = (96, 165, 250)       # Blue 400
TEXT_AMBER = (251, 191, 36)      # Amber 400
TEXT_RED = (248, 113, 113)       # Red 400
TEXT_PURPLE = (192, 132, 252)    # Purple 400

def get_font(size=14, bold=False):
    """Loads system font or fallback default font."""
    font_names = ["consola.ttf", "consolas.ttf", "arial.ttf", "DejaVuSansMono.ttf"]
    if bold:
        font_names = ["consolab.ttf", "arialbd.ttf"] + font_names
    
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

FONT_TITLE = get_font(20, bold=True)
FONT_SUBTITLE = get_font(15, bold=True)
FONT_BODY = get_font(13, bold=False)
FONT_BOLD = get_font(13, bold=True)
FONT_SMALL = get_font(11, bold=False)

def create_terminal_window(title: str, query: str, content_lines: list, output_filename: str):
    """Renders a visually striking dark-mode terminal window screenshot."""
    width = 950
    header_height = 80
    line_height = 22
    padding = 25
    
    calc_height = header_height + (len(content_lines) * line_height) + (padding * 3) + 60
    height = max(calc_height, 580)
    
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Outer Panel
    panel_rect = [padding, padding, width - padding, height - padding]
    draw.rounded_rectangle(panel_rect, radius=12, fill=PANEL_BG, outline=BORDER_COLOR, width=2)
    
    # Window Control Buttons (Red, Yellow, Green window controls)
    draw.ellipse([padding + 15, padding + 15, padding + 27, padding + 27], fill=(239, 68, 68))
    draw.ellipse([padding + 35, padding + 15, padding + 47, padding + 27], fill=(245, 158, 11))
    draw.ellipse([padding + 55, padding + 15, padding + 67, padding + 27], fill=(16, 185, 129))
    
    # Window Title
    draw.text((padding + 85, padding + 12), title, font=FONT_TITLE, fill=TEXT_WHITE)
    
    # Divider line under title
    draw.line([padding, padding + 48, width - padding, padding + 48], fill=BORDER_COLOR, width=1)
    
    # Query Prompt Bar
    query_y = padding + 60
    draw.rectangle([padding + 15, query_y, width - padding - 15, query_y + 38], fill=BG_COLOR, outline=BORDER_COLOR)
    draw.text((padding + 25, query_y + 10), "USER QUERY: ", font=FONT_BOLD, fill=TEXT_AMBER)
    draw.text((padding + 130, query_y + 10), f'"{query}"', font=FONT_BODY, fill=TEXT_WHITE)
    
    # Render Output Content Lines
    content_y = query_y + 55
    for line in content_lines:
        color = TEXT_WHITE
        font = FONT_BODY
        
        if line.startswith("PARADIGM:") or line.startswith("==="):
            color = TEXT_BLUE
            font = FONT_SUBTITLE
        elif line.startswith("[TRAJECTORY]") or line.startswith("[THOUGHT]"):
            color = TEXT_PURPLE
            font = FONT_BOLD
        elif line.startswith("[TOOL EXECUTION]") or line.startswith("[ACTION]"):
            color = TEXT_AMBER
            font = FONT_BOLD
        elif line.startswith("[OBSERVATION]"):
            color = TEXT_GREEN
            font = FONT_BOLD
        elif line.startswith("[LIMITATION]") or line.startswith("ERROR") or line.startswith("DENIED"):
            color = TEXT_RED
            font = FONT_BOLD
        elif line.startswith("[SUCCESS]") or line.startswith("SUCCESS"):
            color = TEXT_GREEN
            font = FONT_BOLD
        elif line.startswith("  -") or line.startswith("   "):
            color = TEXT_MUTED
            
        draw.text((padding + 20, content_y), line, font=font, fill=color)
        content_y += line_height

    filepath = os.path.join(OUTPUT_DIR, output_filename)
    img.save(filepath)
    print(f"[OK] Generated screenshot: {filepath}")


def generate_all_screenshots():
    query1 = "I bought an Ultra Wireless Headset under order #ORD-9482. Can I return it, what will my refund be, and can you initiate a return for me?"
    
    # 1. Plain Chatbot Screenshot Content
    chatbot_lines = [
        "PARADIGM 1: PLAIN CHATBOT (LLM Alone)",
        "--------------------------------------------------------------------------------",
        "System Architecture: Large Language Model (Prompt-Only, Isolated Memory)",
        "Private Data Access: FALSE (No access to private_store_db.json)",
        "Available Tools:     NONE",
        "",
        "[SYSTEM GENERATED RESPONSE]",
        "Hello! Thank you for reaching out to TechGear Support.",
        "",
        "Regarding your request to return order #ORD-9482:",
        "As an AI chatbot, I do not have access to TechGear's internal database or your private",
        "account records. Therefore, I cannot look up order #ORD-9482, verify your purchase date,",
        "check your VIP refund policy, or initiate a return in our system.",
        "",
        "Generally, items can be returned within 30 days if in original packaging.",
        "Please visit our support portal manually or contact human support to process your return.",
        "",
        "[LIMITATION EVALUATION]",
        "  - Failed to access private database records for order ORD-9482.",
        "  - Unable to calculate VIP restocking fee waiver ($0.00 vs $20.00 standard).",
        "  - Cannot execute transactional database update or issue shipping label."
    ]
    create_terminal_window("TechGear Support System - Paradigm 1: Plain Chatbot", query1, chatbot_lines, "01_plain_chatbot_output.png")

    # 2. Rule-Based Workflow Screenshot Content
    rule_lines = [
        "PARADIGM 2: RULE-BASED WORKFLOW (No LLM)",
        "--------------------------------------------------------------------------------",
        "System Architecture: Procedural Rule Engine (Regex Matching + If/Else Trees)",
        "Private Data Access: TRUE (Direct DB Read/Write)",
        "Available Tools:     Predefined SQL/JSON Mutation Scripts",
        "",
        "[EXECUTION LOG]",
        "  1. Input Regex Match -> Extracted Order ID: 'ORD-9482'",
        "  2. Keyword Match     -> Detected Intent: 'RETURN'",
        "  3. Executing Tool    -> check_return_eligibility('ORD-9482')",
        "  4. Executing Tool    -> process_return_request('ORD-9482')",
        "",
        "[SUCCESS] WORKFLOW EXECUTION COMPLETE",
        "Order ORD-9482 processed.",
        "  - Item: Ultra Wireless Noise-Canceling Headset",
        "  - Delivery Status: 10 days elapsed (Within 30-day window)",
        "  - Restocking Fee: $0.00 (Customer Tier: VIP)",
        "  - Refund Queued: $199.99",
        "  - Return Tracking Label: TRK-RET-ORD-9482-99",
        "",
        "[LIMITATION EVALUATION]",
        "  - Success dependent on structured input containing 'RETURN' & 'ORD-XXXX'.",
        "  - Fails completely on informal queries like 'My headset is acting up, can I send it back?'"
    ]
    create_terminal_window("TechGear Support System - Paradigm 2: Rule-Based Workflow", query1, rule_lines, "02_rule_based_output.png")

    # 3. AI Agent Screenshot Content
    agent_lines = [
        "PARADIGM 3: AI AGENT (LLM + Tools + Loop)",
        "--------------------------------------------------------------------------------",
        "System Architecture: ReAct Agentic Loop (Reasoning + Autonomous Tool Calling)",
        "Private Data Access: TRUE (Dynamic tool invocation)",
        "Loop Iterations:     4 Steps to Completion",
        "",
        "[TRAJECTORY LOG]",
        "[THOUGHT 1] Parse user intent. Order #ORD-9482 mentioned. Call tool get_order_details.",
        "[ACTION 1]  get_order_details({'order_id': 'ORD-9482'})",
        "[OBSERVATION 1] Status: Delivered 2026-09-12 | Item: Ultra Wireless Headset | Price: $199.99",
        "",
        "[THOUGHT 2] Check return policy eligibility and customer VIP status.",
        "[ACTION 2]  check_return_eligibility({'order_id': 'ORD-9482'})",
        "[OBSERVATION 2] Eligible: True | Days Elapsed: 10 | Tier: VIP | Fee Waived: $0.00",
        "",
        "[THOUGHT 3] Policy approved. Execute database state update to initiate return.",
        "[ACTION 3]  process_return_request({'order_id': 'ORD-9482'})",
        "[OBSERVATION 3] Return Initiated | Refund: $199.99 | Label: TRK-RET-ORD-9482-99",
        "",
        "[THOUGHT 4] Task complete. Synthesize comprehensive natural language response.",
        "[FINAL ANSWER]",
        "Great news! I have processed your return request for ORD-9482.",
        "Summary: Item 'Ultra Wireless Headset' delivered 10 days ago (within 30-day policy).",
        "As a VIP member, your restocking fee is waived ($0.00). A refund of $199.99 has been",
        "queued, and pre-paid return label TRK-RET-ORD-9482-99 sent to your registered email."
    ]
    create_terminal_window("TechGear Support System - Paradigm 3: AI Agent (LLM + Tools + Loop)", query1, agent_lines, "03_ai_agent_output.png")

    # 4. Comparative Dashboard Screenshot
    create_summary_dashboard("04_comparative_summary.png")

def create_summary_dashboard(output_filename: str):
    """Renders a comparative visual matrix summarizing the 3 paradigms."""
    width = 1000
    height = 650
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Title Banner
    draw.text((30, 25), "PARADIGM COMPARATIVE DASHBOARD - DAY 1 TASK", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((30, 55), "Scenario: TechGear Private Store Customer & Order Management System", font=FONT_SUBTITLE, fill=TEXT_MUTED)
    draw.line([30, 85, width - 30, 85], fill=BORDER_COLOR, width=2)

    columns = [
        ("FEATURE / BASIS", 30, 220),
        ("PLAIN CHATBOT", 260, 220),
        ("RULE-BASED WORKFLOW", 500, 220),
        ("AI AGENT (LLM+Tools+Loop)", 740, 230)
    ]

    for title, x, w in columns:
        draw.rectangle([x, 100, x + w, 135], fill=PANEL_BG, outline=BORDER_COLOR)
        draw.text((x + 10, 108), title, font=FONT_BOLD, fill=TEXT_AMBER if "AGENT" in title else TEXT_WHITE)

    rows = [
        ("Architecture", "LLM Parametric Memory", "Predefined If/Else Rules", "LLM + Tools + Loop"),
        ("Private Data Access", "NO Access (Fails/Generic)", "Direct DB Access", "Dynamic Tool-Based DB Access"),
        ("Tool Usage", "None", "Hardcoded Functions", "Dynamic Function Selection"),
        ("Flexibility", "High (Conversational)", "Low (Rigid Syntax)", "High (Adaptive Intent)"),
        ("Decision-Making", "None (Text Only)", "Deterministic Hard Rules", "Autonomous Reasoning & Planning"),
        ("Multi-Step Execution", "None", "Linear Pipeline", "ReAct Trajectory Loop"),
        ("Reliability", "Low for Data Tasks", "High for Exact Syntax", "High for Complex Intent & Data")
    ]

    y = 145
    for feature, p1, p2, p3 in rows:
        row_h = 60
        # Column 0: Feature
        draw.rectangle([30, y, 250, y + row_h], fill=PANEL_BG, outline=BORDER_COLOR)
        draw.text((40, y + 20), feature, font=FONT_BOLD, fill=TEXT_BLUE)
        
        # Column 1: Plain Chatbot
        draw.rectangle([260, y, 480, y + row_h], fill=BG_COLOR, outline=BORDER_COLOR)
        draw.text((270, y + 20), p1, font=FONT_BODY, fill=TEXT_RED if "NO" in p1 or "None" in p1 else TEXT_WHITE)

        # Column 2: Rule-Based
        draw.rectangle([500, y, 720, y + row_h], fill=BG_COLOR, outline=BORDER_COLOR)
        draw.text((510, y + 20), p2, font=FONT_BODY, fill=TEXT_AMBER if "Rigid" in p2 or "Linear" in p2 else TEXT_WHITE)

        # Column 3: AI Agent
        draw.rectangle([740, y, 970, y + row_h], fill=PANEL_BG, outline=TEXT_GREEN, width=2)
        draw.text((750, y + 20), p3, font=FONT_BOLD, fill=TEXT_GREEN)

        y += row_h + 8

    filepath = os.path.join(OUTPUT_DIR, output_filename)
    img.save(filepath)
    print(f"[OK] Generated comparative summary screenshot: {filepath}")

if __name__ == "__main__":
    generate_all_screenshots()
