from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

SYSTEM_PROMPT = """
You are a financial assistant for a small business.
Convert the user's natural language input into a structured JSON command.

Allowed actions:
- add_expense: Record an expense
- add_sale: Record a sale/income
- get_summary: Get financial summary (daily/weekly/monthly/all)
- get_chart: Get chart data (monthly_sales, category_breakdown, profit_trend)
- get_transactions: List recent transactions
- unknown: If you cannot understand the request

Response format MUST be valid JSON only. No extra text.

Examples:

User: "Add expense 500 for electricity"
{"action": "add_expense", "amount": 500, "category": "electricity", "note": null}

User: "I earned 3000 from product sales"
{"action": "add_sale", "amount": 3000, "category": "product_sale", "note": null}

User: "How much did I spend this month?"
{"action": "get_summary", "period": "monthly"}

User: "Show me a pie chart of expenses"
{"action": "get_chart", "type": "category_breakdown"}

User: "What were my last transactions?"
{"action": "get_transactions", "limit": 10}

User: "What is my weekly profit?"
{"action": "get_summary", "period": "weekly"}
"""

async def parse_user_input(message: str) -> dict:
    """Send user message to Gemini and get structured JSON back."""
    
    if not GOOGLE_API_KEY:
        # Fallback: simple rule-based parser
        return rule_based_parser(message)

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        raw = response.text.strip()
        
        # Remove any potential markdown formatting (e.g. ```json ... ```)
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw)

    except Exception as e:
        print(f"AI parse error (Gemini): {e}")
        return rule_based_parser(message)


def rule_based_parser(message: str) -> dict:
    """Simple fallback parser without AI."""
    msg = message.lower()

    if any(w in msg for w in ["expense", "spent", "paid", "cost"]):
        words = msg.split()
        amount = next((float(w) for w in words if w.replace('.', '').isdigit()), 0)
        category = "other"
        for cat in ["electricity", "rent", "salaries", "supplies", "food", "transport", "marketing"]:
            if cat in msg:
                category = cat
                break
        return {"action": "add_expense", "amount": amount, "category": category, "note": None}

    elif any(w in msg for w in ["sale", "earned", "income", "revenue", "sold"]):
        words = msg.split()
        amount = next((float(w) for w in words if w.replace('.', '').isdigit()), 0)
        return {"action": "add_sale", "amount": amount, "category": "product_sale", "note": None}

    elif any(w in msg for w in ["summary", "report", "profit", "total"]):
        period = "monthly"
        if "week" in msg: period = "weekly"
        elif "day" in msg or "today" in msg: period = "daily"
        elif "all" in msg or "overall" in msg: period = "all"
        return {"action": "get_summary", "period": period}

    elif any(w in msg for w in ["chart", "graph", "pie", "visual"]):
        return {"action": "get_chart", "type": "category_breakdown"}

    elif any(w in msg for w in ["transaction", "history", "list", "recent"]):
        return {"action": "get_transactions", "limit": 10}

    return {"action": "unknown"}
