from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_connection
from models import (
    TransactionCreate, TransactionResponse,
    SummaryResponse, ChatRequest, ChatResponse
)
from ai_parser import parse_user_input

app = FastAPI(title="Finance Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    print("[OK] FastAPI Backend is live on port 7860")

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ─────────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────────

@app.post("/api/v1/transaction", response_model=TransactionResponse)
def add_transaction(tx: TransactionCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # Get or create category
    cursor.execute("SELECT id FROM categories WHERE name = %s", (tx.category.lower(),))
    row = cursor.fetchone()
    if row:
        cat_id = row["id"]
    else:
        cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (tx.category.lower(),))
        cat_id = cursor.fetchone()["id"]

    cursor.execute(
        "INSERT INTO transactions (type, amount, category_id, note) VALUES (%s, %s, %s, %s) RETURNING id",
        (tx.type, tx.amount, cat_id, tx.note)
    )
    tx_id = cursor.fetchone()["id"]
    conn.commit()

    cursor.execute("""
        SELECT t.id, t.type, t.amount, c.name as category, t.note, t.date
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id = %s
    """, (tx_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return TransactionResponse(
        id=result["id"],
        type=result["type"],
        amount=float(result["amount"]),
        category=result["category"],
        note=result["note"],
        date=result["date"].isoformat() if isinstance(result["date"], datetime) else result["date"]
    )


@app.get("/api/v1/transactions")
def get_transactions(limit: int = Query(20, ge=1, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.type, t.amount, c.name as category, t.note, t.date
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC
        LIMIT %s
    """, (limit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert result to JSON serializable list
    result = []
    for r in rows:
        d = dict(r)
        d["amount"] = float(d["amount"])
        if isinstance(d["date"], datetime):
            d["date"] = d["date"].isoformat()
        result.append(d)
    return result


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────

def get_date_filter(period: str):
    now = datetime.now()
    if period == "daily":
        return now.replace(hour=0, minute=0, second=0).isoformat()
    elif period == "weekly":
        return (now - timedelta(days=7)).isoformat()
    elif period == "monthly":
        return now.replace(day=1, hour=0, minute=0, second=0).isoformat()
    return None  # all time

@app.get("/api/v1/summary", response_model=SummaryResponse)
def get_summary(period: str = Query("monthly")):
    conn = get_connection()
    cursor = conn.cursor()
    date_filter = get_date_filter(period)

    query = "SELECT type, SUM(amount) as total, COUNT(*) as cnt FROM transactions"
    params = []
    if date_filter:
        query += " WHERE date >= %s"
        params.append(date_filter)
    query += " GROUP BY type"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    sales = 0.0
    expenses = 0.0
    count = 0
    for row in rows:
        if row["type"] == "sale":
            sales = float(row["total"])
        elif row["type"] == "expense":
            expenses = float(row["total"])
        count += row["cnt"]

    return SummaryResponse(
        period=period,
        total_sales=round(sales, 2),
        total_expenses=round(expenses, 2),
        profit=round(sales - expenses, 2),
        transaction_count=count
    )


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────

@app.get("/api/v1/charts")
def get_chart_data(type: str = Query("monthly_sales")):
    conn = get_connection()
    cursor = conn.cursor()

    if type == "category_breakdown":
        cursor.execute("""
            SELECT c.name, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense'
            GROUP BY c.name
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "type": "pie",
            "labels": [r["name"] for r in rows],
            "values": [round(float(r["total"]), 2) for r in rows]
        }

    elif type == "monthly_sales":
        cursor.execute("""
            SELECT to_char(date, 'YYYY-MM') as month,
                   SUM(CASE WHEN type='sale' THEN amount ELSE 0 END) as sales,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expenses
            FROM transactions
            GROUP BY month
            ORDER BY month
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "type": "bar",
            "labels": [r["month"] for r in rows],
            "sales": [round(float(r["sales"]), 2) for r in rows],
            "expenses": [round(float(r["expenses"]), 2) for r in rows]
        }

    elif type == "profit_trend":
        cursor.execute("""
            SELECT to_char(date, 'YYYY-MM-DD') as day,
                   SUM(CASE WHEN type='sale' THEN amount ELSE -amount END) as net
            FROM transactions
            GROUP BY day
            ORDER BY day
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        running = 0
        labels, values = [], []
        for r in rows:
            running += float(r["net"])
            labels.append(r["day"])
            values.append(round(running, 2))
        return {"type": "line", "labels": labels, "values": values}

    cursor.close()
    conn.close()
    raise HTTPException(status_code=400, detail=f"Unknown chart type: {type}")


@app.get("/api/v1/categories")
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r["name"] for r in rows]


# ─────────────────────────────────────────────
# CHAT (AI Entry Point)
# ─────────────────────────────────────────────

@app.post("/api/v1/parse")
async def parse_intent(req: ChatRequest):
    parsed = await parse_user_input(req.message)
    return parsed

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    parsed = await parse_user_input(req.message)
    action = parsed.get("action")

    if action == "add_expense":
        amount = parsed.get("amount", 0)
        if amount <= 0:
            return ChatResponse(reply="Please include a valid amount. e.g. 'Add expense 500 for rent'")
        tx = TransactionCreate(
            type="expense",
            amount=amount,
            category=parsed.get("category", "other"),
            note=parsed.get("note")
        )
        result = add_transaction(tx)
        return ChatResponse(
            reply=f"Expense of {amount} recorded under '{result.category}'.",
            action_taken="add_expense",
            data=result.dict()
        )

    elif action == "add_sale":
        amount = parsed.get("amount", 0)
        if amount <= 0:
            return ChatResponse(reply="Please include a valid amount. e.g. 'Sale of 2000 from products'")
        tx = TransactionCreate(
            type="sale",
            amount=amount,
            category=parsed.get("category", "product_sale"),
            note=parsed.get("note")
        )
        result = add_transaction(tx)
        return ChatResponse(
            reply=f"Sale of {amount} recorded under '{result.category}'.",
            action_taken="add_sale",
            data=result.dict()
        )

    elif action == "get_summary":
        period = parsed.get("period", "monthly")
        summary = get_summary(period)
        status = "Up" if summary.profit >= 0 else "Down"
        return ChatResponse(
            reply=(
                f"[{status}] **{period.capitalize()} Summary**\n"
                f"• Sales: {summary.total_sales}\n"
                f"• Expenses: {summary.total_expenses}\n"
                f"• Profit: {summary.profit}"
            ),
            action_taken="get_summary",
            data=summary.dict()
        )

    elif action == "get_chart":
        chart_type = parsed.get("type", "monthly_sales")
        data = get_chart_data(chart_type)
        return ChatResponse(
            reply=f"Chart data ready: {chart_type.replace('_', ' ').title()}",
            action_taken="get_chart",
            data=data
        )

    elif action == "get_transactions":
        limit = parsed.get("limit", 10)
        txs = get_transactions(limit)
        lines = [f"• {t['type'].upper()} {t['amount']} ({t['category']}) — {t['date'][:10]}" for t in txs[:5]]
        return ChatResponse(
            reply=f"Last {min(len(txs), 5)} transactions:\n" + "\n".join(lines),
            action_taken="get_transactions",
            data={"transactions": txs}
        )

    return ChatResponse(
        reply="I didn't understand that. Try:\n- 'Add expense 500 for rent'\n- 'Show monthly summary'\n- 'Show category chart'"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
