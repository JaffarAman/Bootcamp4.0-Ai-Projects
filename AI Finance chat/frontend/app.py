import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable if available, otherwise default to local FastAPI
API_BASE = os.getenv("FASTAPI_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Finance Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_post(path, data):
    try:
        r = requests.post(f"{API_BASE}{path}", json=data, timeout=30)
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

st.sidebar.title("Finance Agent")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["Chat", "Dashboard", "Add Transaction", "Transactions"])
st.sidebar.markdown("---")
st.sidebar.caption("Powered by FastAPI + Gemini AI")

# ─────────────────────────────────────────────
# CHAT PAGE
# ─────────────────────────────────────────────

if page == "Chat":
    st.title("AI Financial Assistant")
    st.caption("Talk to your finances in plain English")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your financial assistant. Try:\n- 'Add expense 500 for electricity'\n- 'Show monthly summary'\n- 'Show category breakdown chart'"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type a financial command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_post("/chat", {"message": prompt})
                if result:
                    reply = result.get("reply", "Something went wrong.")
                    st.markdown(reply)

                    # Show chart if action was get_chart
                    if result.get("action_taken") == "get_chart" and result.get("data"):
                        data = result["data"]
                        if data.get("type") == "pie":
                            fig = px.pie(
                                values=data["values"],
                                names=data["labels"],
                                title="Expense Category Breakdown"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        elif data.get("type") == "bar":
                            fig = go.Figure()
                            fig.add_trace(go.Bar(name="Sales", x=data["labels"], y=data["sales"], marker_color="green"))
                            fig.add_trace(go.Bar(name="Expenses", x=data["labels"], y=data["expenses"], marker_color="red"))
                            fig.update_layout(barmode="group", title="Monthly Sales vs Expenses")
                            st.plotly_chart(fig, use_container_width=True)

                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error("❌ Could not connect to backend. Is the FastAPI server running?")
                    st.info("💡 Run `python run_all.py` to start both frontend and backend.")

# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────

elif page == "Dashboard":
    st.title("Financial Dashboard")

    period = st.selectbox("Period", ["daily", "weekly", "monthly", "all"], index=2)

    summary = api_get("/summary", {"period": period})
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sales", f"PKR {summary['total_sales']:,.0f}")
        col2.metric("Total Expenses", f"PKR {summary['total_expenses']:,.0f}")
        profit = summary["profit"]
        col3.metric("Profit", f"PKR {profit:,.0f}", delta=f"{profit:,.0f}")
        col4.metric("Transactions", summary["transaction_count"])

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Monthly Sales vs Expenses")
        chart_data = api_get("/charts", {"type": "monthly_sales"})
        if chart_data and chart_data.get("labels"):
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Sales", x=chart_data["labels"], y=chart_data["sales"], marker_color="#00C853"))
            fig.add_trace(go.Bar(name="Expenses", x=chart_data["labels"], y=chart_data["expenses"], marker_color="#D32F2F"))
            fig.update_layout(barmode="group", height=350, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No chart data yet. Add some transactions!")

    with col_right:
        st.subheader("Expense Breakdown")
        pie_data = api_get("/charts", {"type": "category_breakdown"})
        if pie_data and pie_data.get("labels"):
            fig = px.pie(values=pie_data["values"], names=pie_data["labels"], height=350)
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data yet.")

    st.subheader("Cumulative Profit Trend")
    trend_data = api_get("/charts", {"type": "profit_trend"})
    if trend_data and trend_data.get("labels"):
        fig = px.line(x=trend_data["labels"], y=trend_data["values"], labels={"x": "Date", "y": "Cumulative Profit"})
        fig.update_traces(line_color="#1565C0", fill="tozeroy")
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data yet.")

# ─────────────────────────────────────────────
# ADD TRANSACTION PAGE
# ─────────────────────────────────────────────

elif page == "Add Transaction":
    st.title("Add Transaction")

    categories_raw = api_get("/categories") or []

    with st.form("add_tx_form"):
        tx_type = st.selectbox("Type", ["expense", "sale"])
        amount = st.number_input("Amount (PKR)", min_value=1.0, step=100.0)
        category = st.selectbox("Category", categories_raw if categories_raw else ["other"])
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            result = api_post("/transaction", {
                "type": tx_type,
                "amount": amount,
                "category": category,
                "note": note or None
            })
            if result:
                st.success(f"{tx_type.capitalize()} of PKR {amount} recorded under '{category}'!")
            else:
                st.error("Failed to add transaction.")

# ─────────────────────────────────────────────
# TRANSACTIONS PAGE
# ─────────────────────────────────────────────

elif page == "Transactions":
    st.title("Transaction History")

    limit = st.slider("Show last N transactions", 5, 100, 20)
    txs = api_get("/transactions", {"limit": limit})

    if txs:
        df = pd.DataFrame(txs)
        df["date"] = pd.to_datetime(df["date"], format='mixed').dt.strftime("%Y-%m-%d %H:%M")
        df["amount"] = df["amount"].apply(lambda x: f"PKR {x:,.2f}")

        # Color-coded type column
        def color_type(val):
            color = "green" if val == "sale" else "red"
            return f"color: {color}; font-weight: bold"

        styled = df.style.map(color_type, subset=["type"])
        st.dataframe(styled, use_container_width=True)

        # Export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", csv, "transactions.csv", "text/csv")
    else:
        st.info("No transactions found. Add some using the Chat or form!")
