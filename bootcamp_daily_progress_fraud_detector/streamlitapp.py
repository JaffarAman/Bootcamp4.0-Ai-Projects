import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bootcamp Progress Tracker",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=DM+Sans:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}



/* Dark background */
.stApp {
    background-color: #080d14;
    color: #dce8f5;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0f1724 !important;
    border-right: 1px solid #1e2d42;
}
[data-testid="stSidebar"] * { color: #dce8f5 !important; }

/* Main header */
h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 1px;
    color: #dce8f5 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #141e2e;
    border: 1px solid #1e2d42;
    border-radius: 8px;
    padding: 16px;
    border-top: 2px solid #0077ff;
}

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: #4e6580 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00c8ff !important;
    border-bottom-color: #00c8ff !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border: 1px solid #1e2d42 !important;
    border-radius: 8px;
}

/* Selectbox, inputs */
[data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTextInput"] {
    background: #0f1724 !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #141e2e !important;
    border: 1px solid #1e2d42 !important;
    border-radius: 8px !important;
}

/* Fraud badge */
.fraud-badge {
    background: rgba(255,61,87,0.15);
    color: #ff3d57;
    border: 1px solid rgba(255,61,87,0.3);
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
}
.clean-badge {
    background: rgba(0,230,118,0.1);
    color: #00e676;
    border: 1px solid rgba(0,230,118,0.3);
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
}
.mentor-badge {
    background: rgba(255,171,64,0.12);
    color: #ffab40;
    border: 1px solid rgba(255,171,64,0.3);
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
}

/* Stat accent colors */
.stat-red   [data-testid="metric-container"] { border-top-color: #ff3d57 !important; }
.stat-green [data-testid="metric-container"] { border-top-color: #00e676 !important; }
.stat-orange [data-testid="metric-container"] { border-top-color: #ffab40 !important; }
.stat-yellow [data-testid="metric-container"] { border-top-color: #ffe74c !important; }

/* Cards for fraud */
.fraud-card {
    background: #141e2e;
    border: 1px solid rgba(255,61,87,0.25);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}
.fraud-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,61,87,0.15);
}
.sim-score {
    font-family: 'Rajdhani', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #ff3d57;
}
.compare-col {
    background: #0f1724;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 13px;
    color: #8a9ab5;
    line-height: 1.5;
    min-height: 60px;
}
.col-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.label-red    { color: #ff3d57; }
.label-orange { color: #ffab40; }
</style>
""", unsafe_allow_html=True)


# ─── DB CONNECTION ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    from config import MONGODB_URL
    client = MongoClient(MONGODB_URL)
    return client["test"]

db        = get_db()
progress_col   = db["progresses"]
fraud_col      = db["fraud_updates"]
users_col      = db["users"]
bootcamps_col  = db["bootcamps"]
domains_col    = db["domains"]


# ─── HELPERS ────────────────────────────────────────────────────────────────────

def serialize(doc):
    result = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, datetime):
            result[k] = v
        else:
            result[k] = v
    return result


def get_bootcamps():
    return list(bootcamps_col.find())


def get_name_map():
    """Return {ObjectId: name} for users."""
    return {u["_id"]: u.get("name", str(u["_id"])) for u in users_col.find()}


def get_bootcamp_map():
    return {b["_id"]: b.get("name", str(b["_id"])) for b in bootcamps_col.find()}


def fmt_date(dt):
    if not dt:
        return "—"
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%d %b %Y")


def fmt_datetime(dt):
    if not dt:
        return "—"
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%d %b %Y, %H:%M")


def sim_color(s):
    if s is None:
        return "—"
    if s >= 75:
        return f"🔴 {s}%"
    if s >= 40:
        return f"🟠 {s}%"
    return f"🟢 {s}%"


def fraud_label(fraud):
    return "⚠️ FRAUD" if fraud else "✅ Clean"


# ─── STATS ──────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_stats():
    total    = progress_col.count_documents({})
    fraud    = progress_col.count_documents({"fraud": True})
    mentor   = progress_col.count_documents({"needMentor": True})
    reviewed = progress_col.count_documents({"grade": {"$ne": ""}})
    unique   = len(progress_col.distinct("studentId"))

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today    = progress_col.count_documents({"createdAt": {"$gte": today_start}})

    agg = list(progress_col.aggregate([{"$group": {"_id": None, "avg": {"$avg": "$hoursWorked"}}}]))
    avg_h = round(agg[0]["avg"], 1) if agg else 0

    fraud_rate = round(fraud / total * 100, 1) if total else 0
    return {
        "total": total, "fraud": fraud, "mentor": mentor,
        "reviewed": reviewed, "unique": unique, "today": today,
        "avg_hours": avg_h, "fraud_rate": fraud_rate,
    }


# ─── LOAD PROGRESSES ────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_progresses(bootcamp_id=None, fraud_only=False, need_mentor=False,
                    date_from=None, date_to=None):
    query = {}
    if bootcamp_id:
        query["bootcampId"] = ObjectId(bootcamp_id)
    if fraud_only:
        query["fraud"] = True
    if need_mentor:
        query["needMentor"] = True
    if date_from:
        query.setdefault("date", {})["$gte"] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        query.setdefault("date", {})["$lte"] = datetime.combine(date_to, datetime.max.time())

    pipeline = [
        {"$match": query},
        {"$sort": {"date": -1}},
        {"$lookup": {"from": "users",     "localField": "studentId",  "foreignField": "_id", "as": "student"}},
        {"$lookup": {"from": "bootcamps", "localField": "bootcampId", "foreignField": "_id", "as": "bootcamp"}},
        {"$addFields": {
            "studentName":  {"$arrayElemAt": ["$student.name",  0]},
            "studentEmail": {"$arrayElemAt": ["$student.email", 0]},
            "bootcampName": {"$arrayElemAt": ["$bootcamp.name", 0]},
        }},
        {"$project": {"student": 0, "bootcamp": 0}},
    ]

    docs = list(progress_col.aggregate(pipeline))
    return [serialize(d) for d in docs]


# ─── LOAD FRAUD ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_fraud():
    pipeline = [
        {"$sort": {"date": -1}},
        {"$lookup": {"from": "users", "localField": "studentId", "foreignField": "_id", "as": "student"}},
        {"$addFields": {
            "studentName":  {"$arrayElemAt": ["$student.name",  0]},
            "studentEmail": {"$arrayElemAt": ["$student.email", 0]},
        }},
        {"$project": {"student": 0}},
    ]
    docs = list(fraud_col.aggregate(pipeline))
    return [serialize(d) for d in docs]


# ─── LOAD BY DATE ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_by_date():
    pipeline = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
            "count":       {"$sum": 1},
            "fraud_count": {"$sum": {"$cond": ["$fraud", 1, 0]}},
            "avg_hours":   {"$avg": "$hoursWorked"},
        }},
        {"$sort": {"_id": 1}},
        {"$limit": 30},
    ]
    return list(progress_col.aggregate(pipeline))


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🚀 TRACKR")
    st.markdown("<small style='color:#4e6580;letter-spacing:2px'>BOOTCAMP OS</small>", unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate",
        ["📊 Overview", "📋 Submissions", "⚠️ Fraud Detection", "✦ Need Mentor"],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    stats = load_stats()
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#4e6580;margin-top:12px'>
        <div>● {stats['total']} total submissions</div>
        <div>⚠ {stats['fraud']} fraud cases</div>
        <div>✦ {stats['mentor']} need mentor</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📊 Overview":
    st.markdown("# 📊 Overview")

    # ── Stats row ──
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("Total Submissions", stats["total"])
    c2.metric("Today",             stats["today"])
    c3.metric("⚠️ Fraud",         stats["fraud"], f"{stats['fraud_rate']}%", delta_color="inverse")
    c4.metric("✦ Need Mentor",    stats["mentor"])
    c5.metric("Avg Hours",         stats["avg_hours"])
    c6.metric("Reviewed",          stats["reviewed"])
    c7.metric("Unique Students",   stats["unique"])

    st.divider()

    # ── Activity chart ──
    st.markdown("### 📅 Activity — Last 30 Days")
    chart_data = load_by_date()
    if chart_data:
        df_chart = pd.DataFrame(chart_data).rename(columns={"_id": "Date", "count": "Submissions", "fraud_count": "Fraud", "avg_hours": "Avg Hours"})
        df_chart["Date"] = pd.to_datetime(df_chart["Date"])
        df_chart = df_chart.set_index("Date")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Daily Submissions vs Fraud**")
            st.bar_chart(df_chart[["Submissions", "Fraud"]], color=["#0077ff", "#ff3d57"])
        with col_b:
            st.markdown("**Average Hours Worked**")
            st.area_chart(df_chart[["Avg Hours"]], color=["#00c8ff"])
    else:
        st.info("No activity data yet.")

    st.divider()

    # ── Recent 10 submissions ──
    st.markdown("### 🕐 Recent Submissions")
    rows = load_progresses()[:10]
    if rows:
        df = pd.DataFrame([{
            "Date":           fmt_date(r.get("date")),
            "Student":        r.get("studentName") or "—",
            "Bootcamp":       r.get("bootcampName") or "—",
            "Yesterday Work": (r.get("yesterdayWork") or "")[:80] + "…",
            "Hours":          r.get("hoursWorked", 0),
            "Similarity":     f"{r.get('similarity', 0)}%",
            "Fraud":          fraud_label(r.get("fraud")),
            "Grade":          r.get("grade") or "—",
        } for r in rows])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No submissions found.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: SUBMISSIONS
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📋 Submissions":
    st.markdown("# 📋 All Submissions")

    # ── Filters ──
    bootcamp_list = get_bootcamps()
    bootcamp_opts = {"All Bootcamps": None}
    for b in bootcamp_list:
        bootcamp_opts[b.get("name", str(b["_id"]))] = str(b["_id"])

    with st.expander("🔍 Filters", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        selected_bc  = col1.selectbox("Bootcamp",   list(bootcamp_opts.keys()))
        date_from    = col2.date_input("From Date",  value=None)
        date_to      = col3.date_input("To Date",    value=None)
        fraud_only   = col4.checkbox("⚠️ Fraud Only")
        need_mentor  = col5.checkbox("✦ Need Mentor")

    bc_id = bootcamp_opts[selected_bc]
    rows  = load_progresses(
        bootcamp_id=bc_id,
        fraud_only=fraud_only,
        need_mentor=need_mentor,
        date_from=date_from if date_from else None,
        date_to=date_to if date_to else None,
    )

    st.markdown(f"**{len(rows)} records found**")

    if rows:
        # Build display df
        df = pd.DataFrame([{
            "Date":           fmt_date(r.get("date")),
            "Student":        r.get("studentName") or "—",
            "Email":          r.get("studentEmail") or "—",
            "Bootcamp":       r.get("bootcampName") or "—",
            "Yesterday Work": (r.get("yesterdayWork") or "")[:80],
            "Today Plan":     (r.get("todayPlan") or "")[:60],
            "Blockers":       r.get("blockers") or "None",
            "Hours":          r.get("hoursWorked", 0),
            "Similarity %":   r.get("similarity", 0),
            "Fraud":          fraud_label(r.get("fraud")),
            "Need Mentor":    "✦ Yes" if r.get("needMentor") else "No",
            "Grade":          r.get("grade") or "—",
            "Feedback":       (r.get("feedback") or "")[:60],
            "GitHub":         r.get("githubLink") or "—",
        } for r in rows])

        # Color-code similarity column
        def style_sim(val):
            try:
                v = float(str(val).replace("%", ""))
                if v >= 75: return "color: #ff3d57; font-weight:600"
                if v >= 40: return "color: #ffab40"
                return "color: #00e676"
            except:
                return ""

        styled = df.style.applymap(style_sim, subset=["Similarity %"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=500)

        # ── Detail viewer ──
        st.divider()
        st.markdown("### 🔎 Submission Detail")
        student_names = [r.get("studentName") or f"Student {i+1}" for i, r in enumerate(rows)]
        sel_idx = st.selectbox("Select a submission to view details:", range(len(rows)),
                               format_func=lambda i: f"{student_names[i]} — {fmt_date(rows[i].get('date'))}")

        if sel_idx is not None:
            r = rows[sel_idx]
            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown("**Student Info**")
                st.write(f"👤 **Name:** {r.get('studentName') or '—'}")
                st.write(f"📧 **Email:** {r.get('studentEmail') or '—'}")
                st.write(f"🏕 **Bootcamp:** {r.get('bootcampName') or '—'}")
                st.write(f"📅 **Date:** {fmt_datetime(r.get('date'))}")
                st.write(f"⏱ **Hours Worked:** {r.get('hoursWorked', 0)}h")
                st.write(f"📌 **Blockers:** {r.get('blockers') or 'None'}")

            with col_r:
                st.markdown("**Review Info**")
                st.write(f"🎓 **Grade:** {r.get('grade') or '—'}")
                st.write(f"💬 **Feedback:** {r.get('feedback') or '—'}")
                st.write(f"🔍 **Similarity:** {sim_color(r.get('similarity'))}")
                st.write(f"⚠️ **Fraud:** {'YES — flagged' if r.get('fraud') else 'No'}")
                st.write(f"✦ **Need Mentor:** {'Yes' if r.get('needMentor') else 'No'}")
                if r.get("githubLink"):
                    st.markdown(f"🔗 **GitHub:** [{r['githubLink']}]({r['githubLink']})")

            st.markdown("**Yesterday's Work**")
            st.info(r.get("yesterdayWork") or "—")

            st.markdown("**Today's Plan**")
            st.info(r.get("todayPlan") or "—")

            # Show fraud match if applicable
            if r.get("fraud") and r.get("matched_id"):
                matched = progress_col.find_one({"_id": ObjectId(r["matched_id"])})
                if matched:
                    st.markdown("---")
                    st.markdown("### ⚠️ Fraud Match Details")
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        st.markdown(f"<div style='background:rgba(255,61,87,0.08);border:1px solid rgba(255,61,87,0.3);border-radius:8px;padding:12px'>"
                                    f"<div style='color:#ff3d57;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px'>▲ THIS SUBMISSION</div>"
                                    f"<div style='color:#8a9ab5;font-size:13px'>{r.get('yesterdayWork','')}</div></div>",
                                    unsafe_allow_html=True)
                    with mc2:
                        st.markdown(f"<div style='background:rgba(255,171,64,0.08);border:1px solid rgba(255,171,64,0.3);border-radius:8px;padding:12px'>"
                                    f"<div style='color:#ffab40;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px'>◆ MATCHED — {fmt_date(matched.get('date'))}</div>"
                                    f"<div style='color:#8a9ab5;font-size:13px'>{matched.get('yesterdayWork','')}</div></div>",
                                    unsafe_allow_html=True)
    else:
        st.warning("No submissions match your filters.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: FRAUD DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "⚠️ Fraud Detection":
    st.markdown("# ⚠️ Fraud Detection")

    fraud_rows = load_fraud()
    st.markdown(f"**{len(fraud_rows)} fraud cases detected**")

    if not fraud_rows:
        st.success("✅ No fraud detected. All submissions appear to be original.")
    else:
        # ── Summary metrics ──
        sim_values = [r.get("similarity", 0) for r in fraud_rows]
        avg_sim = round(sum(sim_values) / len(sim_values), 1) if sim_values else 0
        max_sim = max(sim_values) if sim_values else 0

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total Fraud Cases", len(fraud_rows))
        mc2.metric("Average Similarity", f"{avg_sim}%")
        mc3.metric("Highest Similarity", f"{max_sim}%")

        st.divider()

        # ── Fraud table summary ──
        st.markdown("### 📋 All Fraud Cases")
        df_fraud = pd.DataFrame([{
            "Date":       fmt_date(r.get("date")),
            "Student":    r.get("studentName") or str(r.get("studentId", "—")),
            "Email":      r.get("studentEmail") or "—",
            "Similarity": f"{r.get('similarity', 0)}%",
            "Submitted":  (r.get("yesterdayWork") or "")[:80],
            "Matched On": fmt_date(r.get("matched_date")),
            "Matched":    (r.get("matched_text") or "")[:80],
        } for r in fraud_rows])
        st.dataframe(df_fraud, use_container_width=True, hide_index=True)

        st.divider()

        # ── Individual fraud cards ──
        st.markdown("### 🔬 Side-by-Side Comparison")

        for r in fraud_rows:
            sim = r.get("similarity", 0)
            student = r.get("studentName") or str(r.get("studentId", "Unknown"))
            date    = fmt_datetime(r.get("date"))

            with st.expander(f"⚠️ {student} — {sim}% similarity — {date}", expanded=False):
                header_col, sim_col = st.columns([4, 1])
                with header_col:
                    st.markdown(f"**Student:** {student}")
                    st.markdown(f"**Email:** {r.get('studentEmail') or '—'}")
                    st.markdown(f"**Submitted on:** {date}")
                with sim_col:
                    st.markdown(f"<div style='text-align:center'>"
                                f"<div style='font-family:Rajdhani,sans-serif;font-size:38px;font-weight:700;color:#ff3d57;line-height:1'>{sim}%</div>"
                                f"<div style='font-size:10px;color:#4e6580;letter-spacing:1px;text-transform:uppercase'>SIMILARITY</div>"
                                f"</div>", unsafe_allow_html=True)

                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown("<div style='color:#ff3d57;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px'>▲ SUBMITTED TEXT</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background:#0f1724;border:1px solid rgba(255,61,87,0.3);border-radius:6px;padding:12px;color:#8a9ab5;font-size:13px;line-height:1.5'>"
                                f"{r.get('yesterdayWork','—')}</div>", unsafe_allow_html=True)
                with cc2:
                    st.markdown(f"<div style='color:#ffab40;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px'>◆ MATCHED TEXT ({fmt_date(r.get('matched_date'))})</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background:#0f1724;border:1px solid rgba(255,171,64,0.3);border-radius:6px;padding:12px;color:#8a9ab5;font-size:13px;line-height:1.5'>"
                                f"{r.get('matched_text','—')}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: NEED MENTOR
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "✦ Need Mentor":
    st.markdown("# ✦ Students Needing Mentor")

    mentor_rows = load_progresses(need_mentor=True)
    st.markdown(f"**{len(mentor_rows)} students flagged for mentor support**")

    if not mentor_rows:
        st.success("✅ No students have flagged for mentor support.")
    else:
        # Group by student
        student_map = {}
        for r in mentor_rows:
            name = r.get("studentName") or str(r.get("studentId", "Unknown"))
            student_map.setdefault(name, []).append(r)

        st.markdown(f"**{len(student_map)} unique students** across {len(mentor_rows)} submissions")
        st.divider()

        # ── Full table ──
        st.markdown("### 📋 All Mentor-Flagged Submissions")
        df_m = pd.DataFrame([{
            "Date":           fmt_date(r.get("date")),
            "Student":        r.get("studentName") or "—",
            "Email":          r.get("studentEmail") or "—",
            "Bootcamp":       r.get("bootcampName") or "—",
            "Blockers":       r.get("blockers") or "None",
            "Yesterday Work": (r.get("yesterdayWork") or "")[:80],
            "Hours":          r.get("hoursWorked", 0),
            "Fraud":          fraud_label(r.get("fraud")),
        } for r in mentor_rows])
        st.dataframe(df_m, use_container_width=True, hide_index=True)

        st.divider()

        # ── Per-student breakdown ──
        st.markdown("### 👤 Per Student Breakdown")
        for name, submissions in student_map.items():
            with st.expander(f"✦ {name} — {len(submissions)} submissions flagged"):
                for r in submissions:
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.write(f"📅 **Date:** {fmt_date(r.get('date'))}")
                        st.write(f"⏱ **Hours:** {r.get('hoursWorked', 0)}h")
                        st.write(f"🔍 **Similarity:** {sim_color(r.get('similarity'))}")
                        st.write(f"⚠️ **Fraud:** {'Yes' if r.get('fraud') else 'No'}")
                    with col_b:
                        st.write(f"🚧 **Blockers:** {r.get('blockers') or 'None'}")
                        st.write(f"📝 **Yesterday:** {(r.get('yesterdayWork') or '—')[:120]}")
                        st.write(f"📌 **Today Plan:** {(r.get('todayPlan') or '—')[:120]}")
                    st.markdown("---")
