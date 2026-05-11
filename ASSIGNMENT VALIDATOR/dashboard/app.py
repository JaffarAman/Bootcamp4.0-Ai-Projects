"""
Bootcamp Intelligence — Corporate Streamlit Dashboard
All emojis replaced with professional inline SVG icons (Lucide-style).
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

DOMAIN_MAP = {
    "69c538969d2f7dcce6f2df26": "AI",
    "69c538969d2f7dcce6f2df24": "Web",
    "69c2304ccfe658657f11a4fd": "UI/UX",
}

COLORS = {
    "violet":  "#6c63ff",
    "teal":    "#2dd4bf",
    "rose":    "#f43f5e",
    "amber":   "#f59e0b",
    "emerald": "#10b981",
    "purple":  "#e879f9",
    "blue":    "#60a5fa",
}
COLOR_SEQ = list(COLORS.values())

if "seen_notif_ids" not in st.session_state:
    st.session_state.seen_notif_ids = set()

st.set_page_config(
    page_title="Bootcamp Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><text y='20' font-size='20'>📊</text></svg>",
)

# ──────────────────────────────────────────────────────────────
# SVG ICON LIBRARY  (inline Lucide-style, 16×16 stroke icons)
# ──────────────────────────────────────────────────────────────
def ico(name, size=16, color="currentColor", cls=""):
    """Return an inline SVG icon string by name."""
    s = size
    c = color
    stroke = f'stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'
    fill   = 'fill="none"'
    base   = f'width="{s}" height="{s}" viewBox="0 0 24 24" {fill} {stroke} xmlns="http://www.w3.org/2000/svg"'
    klass  = f'class="{cls}"' if cls else ""

    paths = {
        # Navigation / brand
        "graduation": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
        "home":       '<path d="M3 9.5 12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21V12h6v9"/>',
        "user":       '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>',
        "clipboard":  '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M8 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-2"/><path d="M12 11h4M12 16h4M8 11h.01M8 16h.01"/>',
        "alert-tri":  '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        "upload":     '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
        # KPI icons
        "folder":     '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
        "users":      '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "check-sq":   '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
        "x-circle":   '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
        "trending":   '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
        "book-open":  '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 0 3-3h7z"/>',
        "bar-chart":  '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        # Cards / UI
        "bell":       '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
        "bell-off":   '<path d="M13.73 21a2 2 0 0 1-3.46 0"/><path d="M18.63 13A17.89 17.89 0 0 1 18 8"/><path d="M6.26 6.26A5.86 5.86 0 0 0 6 8c0 7-3 9-3 9h14"/><path d="M18 8a6 6 0 0 0-9.33-5"/><line x1="1" y1="1" x2="23" y2="23"/>',
        "calendar":   '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "clock":      '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "link":       '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
        "tag":        '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
        "shield":     '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        "search":     '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        "hash":       '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
        "alert-circ": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        "check-circ": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "mail":       '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        "x-sq":       '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>',
        "info":       '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
        "send":       '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
        "server":     '<rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
        "eye":        '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
        "play":       '<polygon points="5 3 19 12 5 21 5 3"/>',
        "loader":     '<line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>',
        "minus-circ": '<circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/>',
        "list":       '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
        "pie-chart":  '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
        "table":      '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
        "globe":      '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        "award":      '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
    }

    d = paths.get(name, '<circle cx="12" cy="12" r="4"/>')
    return f'<svg {klass} {base}>{d}</svg>'


def ico_box(name, size=18, bg="rgba(108,99,255,0.14)", color="#a78bfa", radius="9px", pad="10px"):
    """Icon inside a coloured rounded box — for KPI cards, section headers, etc."""
    return (
        f'<div style="width:38px;height:38px;border-radius:{radius};background:{bg};'
        f'display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
        f'{ico(name, size, color)}'
        f'</div>'
    )


# ──────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg:          #07070e;
    --surface:     #0e0e18;
    --card:        #13131f;
    --elevated:    #1a1a28;
    --border:      #20202e;
    --border-h:    #363650;
    --accent:      #6c63ff;
    --accent-glow: rgba(108,99,255,0.20);
    --teal:        #2dd4bf;
    --amber:       #f59e0b;
    --rose:        #f43f5e;
    --emerald:     #10b981;
    --text:        #eeedf8;
    --text-2:      #9a98b4;
    --text-3:      #4e4c64;
    --mono:        'IBM Plex Mono', monospace;
    --sans:        'Inter', sans-serif;
    --r:           10px;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
.main .block-container { padding: 2rem 2.6rem 3rem; max-width: 1480px; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { font-family: var(--sans) !important; }
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── Brand ── */
.brand {
    background: linear-gradient(135deg, #1e1b4b 0%, #1e3a8a 60%, #0c4a6e 100%);
    padding: 22px 20px 20px;
    margin-bottom: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.brand-logorow { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.brand-logo {
    width: 32px; height: 32px; border-radius: 8px;
    background: rgba(255,255,255,0.12);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.brand-name { font-size: 0.96rem; font-weight: 800; letter-spacing: -0.4px; color: #fff; line-height: 1.1; }
.brand-sub  {
    font-size: 0.59rem; color: rgba(255,255,255,0.45);
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 2px; text-transform: uppercase;
}

/* ── Sidebar nav ── */
.sb-label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.57rem; letter-spacing: 2px;
    text-transform: uppercase; color: var(--text-3);
    padding: 18px 14px 6px;
}
[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important; border: 1px solid transparent !important;
    border-radius: 8px !important; padding: 9px 13px !important;
    font-size: 0.81rem !important; font-weight: 500 !important;
    color: var(--text-2) !important; transition: all 0.15s !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--elevated) !important; color: var(--text) !important;
}
/* Nav item SVG icons */
.nav-item { display: flex; align-items: center; gap: 9px; }
.nav-item svg { opacity: 0.65; flex-shrink: 0; }

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: var(--elevated) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r) !important; color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.82rem !important;
    padding: 10px 13px !important; transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important; outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-3) !important; }
.stTextInput label {
    font-size: 0.72rem !important; color: var(--text-2) !important;
    font-weight: 600 !important; letter-spacing: 0.3px !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #6d28d9 100%) !important;
    border: none !important; border-radius: var(--r) !important;
    color: #fff !important; font-family: var(--sans) !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
    padding: 11px 22px !important; width: 100%;
    box-shadow: 0 4px 16px rgba(79,70,229,0.38) !important;
    transition: all 0.2s ease !important; letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(79,70,229,0.52) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r) !important; padding: 4px !important; gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: 1px solid transparent !important;
    border-radius: 7px !important; color: var(--text-2) !important;
    font-size: 0.77rem !important; font-weight: 600 !important;
    padding: 7px 15px !important; transition: all 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
.stTabs [aria-selected="true"] {
    background: var(--elevated) !important; border-color: var(--border) !important;
    color: var(--text) !important; box-shadow: 0 1px 6px rgba(0,0,0,0.5) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 1.2rem 0 0 !important; }
.tab-label { display: flex; align-items: center; gap: 7px; }
.tab-label svg { flex-shrink: 0; }

/* ── Progress ── */
.stProgress > div > div { background: var(--border) !important; border-radius: 20px !important; height: 6px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, #4f46e5, #2dd4bf) !important; border-radius: 20px !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--r) !important; overflow: hidden !important; }
[data-testid="stDataFrame"] table { background: var(--card) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.77rem !important; }

.stAlert { background: var(--card) !important; border-color: var(--border) !important; border-radius: var(--r) !important; font-size: 0.82rem !important; }
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── KPI Cards ── */
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap: 14px; margin-bottom: 2rem; }
.kpi {
    background: var(--card); border: 1px solid var(--border); border-radius: 13px;
    padding: 20px 22px 18px; position: relative; overflow: hidden;
    transition: border-color 0.2s, transform 0.18s; display: flex; align-items: flex-start; gap: 14px;
}
.kpi:hover { border-color: var(--border-h); transform: translateY(-2px); }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 13px 13px 0 0; }
.kpi.v::before { background: linear-gradient(90deg, #6c63ff, #a78bfa); }
.kpi.t::before { background: linear-gradient(90deg, #2dd4bf, #67e8f9); }
.kpi.r::before { background: linear-gradient(90deg, #f43f5e, #fb7185); }
.kpi.a::before { background: linear-gradient(90deg, #f59e0b, #fcd34d); }
.kpi.e::before { background: linear-gradient(90deg, #10b981, #6ee7b7); }
.kpi-body  { flex: 1; min-width: 0; }
.kpi-val   { font-size: 1.9rem; font-weight: 800; line-height: 1; color: var(--text); font-family: 'IBM Plex Mono', monospace; letter-spacing: -1px; }
.kpi-lbl   { font-size: 0.67rem; text-transform: uppercase; letter-spacing: 1.2px; color: var(--text-2); font-weight: 600; margin-top: 6px; }
.kpi-sub   { font-size: 0.65rem; color: var(--text-3); font-family: 'IBM Plex Mono', monospace; margin-top: 3px; }

/* ── Page Header ── */
.ph { display: flex; align-items: flex-end; gap: 16px; margin-bottom: 1.8rem; padding-bottom: 1.1rem; border-bottom: 1px solid var(--border); }
.ph-eye  { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 2.5px; text-transform: uppercase; color: var(--accent); margin-bottom: 5px; }
.ph-ttl  { font-size: 1.75rem; font-weight: 800; letter-spacing: -1px; color: var(--text); line-height: 1; }
.ph-icon {
    width: 44px; height: 44px; border-radius: 11px;
    background: rgba(108,99,255,0.14);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

/* ── Badges ── */
.badge { display: inline-flex; align-items: center; gap: 5px; padding: 2px 9px; border-radius: 5px; font-size: 0.64rem; font-family: 'IBM Plex Mono', monospace; font-weight: 600; letter-spacing: 0.3px; }
.bv { background: rgba(108,99,255,0.13); color: #a78bfa; border: 1px solid rgba(108,99,255,0.28); }
.bt { background: rgba(45,212,191,0.11);  color: #2dd4bf; border: 1px solid rgba(45,212,191,0.28); }
.br { background: rgba(244,63,94,0.11);   color: #f43f5e; border: 1px solid rgba(244,63,94,0.28); }
.be { background: rgba(16,185,129,0.11);  color: #10b981; border: 1px solid rgba(16,185,129,0.28); }
.ba { background: rgba(245,158,11,0.11);  color: #f59e0b; border: 1px solid rgba(245,158,11,0.28); }
.badge svg { flex-shrink: 0; }

/* ── Section label ── */
.slbl { font-family: 'IBM Plex Mono', monospace; font-size: 0.59rem; letter-spacing: 2px; text-transform: uppercase; color: var(--text-3); margin: 1.4rem 0 0.6rem; }

/* ── Empty State ── */
.empty { background: var(--card); border: 1px dashed var(--border-h); border-radius: 14px; padding: 52px 32px; text-align: center; margin-top: 1.5rem; }
.empty-iconbox { width: 56px; height: 56px; border-radius: 14px; background: var(--elevated); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.empty-ttl  { font-size: 1.02rem; font-weight: 700; color: var(--text); margin-bottom: 8px; }
.empty-sub  { font-size: 0.78rem; color: var(--text-3); font-family: 'IBM Plex Mono', monospace; }

/* ── API Status ── */
.status { display: flex; align-items: center; gap: 8px; font-family: 'IBM Plex Mono', monospace; font-size: 0.64rem; color: var(--text-3); padding: 12px 14px; border-top: 1px solid var(--border); margin-top: 8px; }
.dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; animation: blink 2.4s ease-in-out infinite; }
.dot.on  { background: #10b981; }
.dot.off { background: #f43f5e; animation: none; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── Identity Card ── */
.s-card {
    background: linear-gradient(135deg, rgba(79,70,229,0.10), rgba(45,212,191,0.05));
    border: 1px solid var(--border-h); border-radius: 14px;
    padding: 20px 24px; margin-bottom: 1.6rem;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.s-avatar {
    width: 48px; height: 48px; border-radius: 11px;
    background: linear-gradient(135deg, #3730a3, #6d28d9);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.s-name { font-size: 1.15rem; font-weight: 700; color: var(--text); letter-spacing: -0.3px; }
.s-id   { font-size: 0.68rem; font-family: 'IBM Plex Mono', monospace; color: var(--text-3); margin-top: 3px; word-break: break-all; }

/* ── Notification card ── */
.notif {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.20);
    border-left: 3px solid #f59e0b;
    border-radius: 9px; padding: 13px 16px; margin-bottom: 8px;
    display: flex; gap: 12px; align-items: flex-start;
}
.notif-icon { flex-shrink: 0; margin-top: 1px; }
.notif-msg  { font-size: 0.81rem; color: var(--text-2); line-height: 1.5; }
.notif-time { font-size: 0.64rem; font-family: 'IBM Plex Mono', monospace; color: var(--text-3); margin-top: 3px; display: flex; align-items: center; gap: 4px; }

/* ── Missed assignment item ── */
.missed-item {
    background: rgba(244,63,94,0.05);
    border: 1px solid rgba(244,63,94,0.16);
    border-left: 3px solid #f43f5e; border-radius: 9px;
    padding: 12px 16px; margin-bottom: 7px;
    display: flex; align-items: center; gap: 12px;
}
.missed-item-ico { flex-shrink: 0; }
.missed-item-title    { font-size: 0.84rem; font-weight: 600; color: var(--text); }
.missed-item-deadline { font-size: 0.67rem; font-family: 'IBM Plex Mono', monospace; color: var(--text-3); margin-top: 3px; display: flex; align-items: center; gap: 5px; }

/* ── Missing student card ── */
.miss-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 11px;
    padding: 14px 18px; margin-bottom: 8px;
    display: flex; align-items: flex-start; gap: 14px;
    transition: border-color 0.15s;
}
.miss-card:hover { border-color: var(--border-h); }
.miss-av {
    width: 36px; height: 36px; border-radius: 8px;
    background: rgba(244,63,94,0.12);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.miss-info     { flex: 1; min-width: 0; }
.miss-name     { font-size: 0.85rem; font-weight: 600; color: var(--text); }
.miss-email    { font-size: 0.69rem; font-family: 'IBM Plex Mono', monospace; color: var(--text-3); margin-top: 2px; display: flex; align-items: center; gap: 5px; }
.miss-id-block { margin-top: 7px; }
.miss-id-label { font-size: 0.57rem; font-family: 'IBM Plex Mono', monospace; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-3); margin-bottom: 2px; }
.miss-id-val   { font-size: 0.71rem; font-family: 'IBM Plex Mono', monospace; color: #a78bfa; word-break: break-all; }

/* ── Guidelines card ── */
.guide-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.guide-header { padding: 18px 22px 14px; border-bottom: 1px solid var(--border); }
.guide-eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.57rem; letter-spacing: 2px; text-transform: uppercase; color: var(--accent); margin-bottom: 4px; }
.guide-title { font-size: 0.98rem; font-weight: 700; color: var(--text); }
.guide-item { display: flex; align-items: flex-start; gap: 14px; padding: 14px 22px; border-bottom: 1px solid var(--border); }
.guide-item:last-child { border-bottom: none; }
.guide-ico { flex-shrink: 0; margin-top: 1px; }
.guide-lbl { font-size: 0.81rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.guide-desc { font-size: 0.75rem; color: var(--text-3); line-height: 1.65; }
.guide-pill { display: inline-block; background: rgba(108,99,255,0.12); color: #a78bfa; border: 1px solid rgba(108,99,255,0.24); border-radius: 4px; font-size: 0.63rem; font-family: 'IBM Plex Mono', monospace; padding: 1px 7px; margin: 2px 2px 0 0; }
.guide-pill.g { background: rgba(16,185,129,0.10); color: #10b981; border-color: rgba(16,185,129,0.22); }
.guide-pill.r { background: rgba(244,63,94,0.10);  color: #f43f5e; border-color: rgba(244,63,94,0.22); }

/* ── Submit result card ── */
.result-card { background: linear-gradient(135deg, rgba(16,185,129,0.07), rgba(45,212,191,0.04)); border: 1px solid rgba(16,185,129,0.22); border-radius: 12px; padding: 20px 24px; margin-top: 14px; }
.result-eyebrow { font-size: 0.59rem; font-family: 'IBM Plex Mono', monospace; letter-spacing: 2px; text-transform: uppercase; color: #10b981; margin-bottom: 14px; display: flex; align-items: center; gap: 7px; }
.result-grid { display: flex; gap: 28px; flex-wrap: wrap; }
.result-field-lbl { font-size: 0.63rem; color: var(--text-3); font-family: 'IBM Plex Mono', monospace; margin-bottom: 3px; }
.result-field-val { font-size: 0.88rem; font-weight: 700; color: var(--text); font-family: 'IBM Plex Mono', monospace; word-break: break-all; }
.result-field-val.teal { color: #2dd4bf; }

/* ── Sidebar platform list ── */
.platform-list { display: flex; flex-direction: column; gap: 5px; padding: 6px 4px 10px; }
.platform-item { display: flex; align-items: center; gap: 8px; font-size: 0.74rem; color: var(--text-3); }
.platform-item svg { flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PLOT THEME
# ──────────────────────────────────────────────────────────────
PLOT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color="#9a98b4", size=11),
    margin=dict(l=12, r=12, t=46, b=12),
    legend=dict(bgcolor="rgba(19,19,31,0.92)", bordercolor="#20202e",
                borderwidth=1, font=dict(size=10)),
    title_font=dict(size=13, color="#eeedf8", family="Inter, sans-serif"),
)
AX = dict(gridcolor="#1a1a28", linecolor="#20202e",
          tickfont=dict(size=10, family="IBM Plex Mono"), tickcolor="#20202e")


def ax(fig, xr=None, yr=None):
    fig.update_xaxes(**AX, **({"range": xr} if xr else {}))
    fig.update_yaxes(**AX, **({"range": yr} if yr else {}))


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def safe_get(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout)
        return r if r.ok else None
    except Exception:
        return None


def kpi(icon_name, icon_color, icon_bg, label, val, sub="", kind="v"):
    return f"""
    <div class="kpi {kind}">
        {ico_box(icon_name, 18, icon_bg, icon_color, "9px")}
        <div class="kpi-body">
            <div class="kpi-val">{val}</div>
            <div class="kpi-lbl">{label}</div>
            {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
        </div>
    </div>"""


def header(eye, title, icon_name="bar-chart"):
    st.markdown(f"""
    <div class="ph">
        <div class="ph-icon">{ico(icon_name, 22, "#a78bfa")}</div>
        <div>
            <div class="ph-eye">{eye}</div>
            <div class="ph-ttl">{title}</div>
        </div>
    </div>""", unsafe_allow_html=True)


def empty_state(icon_name, title, sub):
    st.markdown(f"""
    <div class="empty">
        <div class="empty-iconbox">{ico(icon_name, 26, "#4e4c64")}</div>
        <div class="empty-ttl">{title}</div>
        <div class="empty-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def fmt_deadline(raw):
    if not raw:
        return "—"
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00")) if isinstance(raw, str) else raw
        return dt.strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        return str(raw)


def render_missing_student_card(s):
    sname  = s.get("name",  "Unknown Student")
    semail = s.get("email", "—")
    sid    = s.get("studentId", "—")
    st.markdown(f"""
    <div class="miss-card">
        <div class="miss-av">{ico("user", 16, "#f43f5e")}</div>
        <div class="miss-info">
            <div class="miss-name">{sname}</div>
            <div class="miss-email">{ico("mail", 11, "#4e4c64")} {semail}</div>
            <div class="miss-id-block">
                <div class="miss-id-label">Student ID</div>
                <div class="miss-id-val">{sid}</div>
            </div>
        </div>
        <span class="badge br">{ico("x-circle", 11, "#f43f5e")} Not Submitted</span>
    </div>""", unsafe_allow_html=True)


def render_missed_assignment_item(m):
    if isinstance(m, dict):
        title   = m.get("title", m.get("assignmentName", "Unknown Assignment"))
        deadline = fmt_deadline(m.get("deadline", ""))
        dl_html = f'<div class="missed-item-deadline">{ico("clock", 11, "#4e4c64")} Deadline: {deadline}</div>'
    else:
        title   = str(m)
        dl_html = ""

    st.markdown(f"""
    <div class="missed-item">
        <div class="missed-item-ico">{ico("x-circle", 16, "#f43f5e")}</div>
        <div style="flex:1;">
            <div class="missed-item-title">{title}</div>
            {dl_html}
        </div>
    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="brand">
        <div class="brand-logorow">
            <div class="brand-logo">{ico("award", 18, "#93c5fd")}</div>
            <div>
                <div class="brand-name">Bootcamp Intelligence</div>
            </div>
        </div>
        <div class="brand-sub">Analytics Platform · v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "",
        ["Overview", "Students", "Assignments", "Missed", "Submit"],
        label_visibility="collapsed",
        format_func=lambda x: x,
    )

    # Render nav icons separately via markdown (radio labels can't contain HTML)
    nav_icons = {
        "Overview":     ("home",      "Dashboard"),
        "Students":     ("user",      "Student Analytics"),
        "Assignments":  ("clipboard", "Assignment Inspector"),
        "Missed":       ("alert-tri", "Missed Submissions"),
        "Submit":       ("upload",    "Submit Assignment"),
    }

    st.markdown('<div class="sb-label">Lookup</div>', unsafe_allow_html=True)

    student_id    = None
    assignment_id = None

    if page == "Students":
        student_id = st.text_input("Student ID", placeholder="MongoDB ObjectId…", key="sid")
        st.button("Load Student", key="rb_s")

    elif page == "Assignments":
        assignment_id = st.text_input("Assignment ID", placeholder="MongoDB ObjectId…", key="aid_a")
        st.button("Load Assignment", key="rb_a")

    elif page == "Missed":
        assignment_id = st.text_input("Assignment ID", placeholder="MongoDB ObjectId…", key="aid_m")
        st.button("Load Missing", key="rb_m")

    elif page == "Submit":
        st.markdown(f"""
        <div class="platform-list">
            <div class="platform-item">{ico("globe", 12, "#4e4c64")} Accepted platforms</div>
            <div class="platform-item">{ico("link", 11, "#6c63ff")} GitHub</div>
            <div class="platform-item">{ico("link", 11, "#6c63ff")} Vercel</div>
            <div class="platform-item">{ico("link", 11, "#6c63ff")} Streamlit</div>
            <div class="platform-item">{ico("link", 11, "#6c63ff")} Figma</div>
        </div>""", unsafe_allow_html=True)

    api_ok = safe_get(f"{API_BASE}/assignment-status", timeout=3) is not None
    st.markdown(f"""
    <div class="status">
        <span class="dot {'on' if api_ok else 'off'}"></span>
        <span>{"API · connected" if api_ok else "API · unreachable"}</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "Overview":
    header("SYSTEM OVERVIEW", "Dashboard", "bar-chart")

    res = safe_get(f"{API_BASE}/assignment-status")
    if res is None:
        st.error("Cannot reach the API. Make sure the FastAPI backend is running on port 8000.")
        st.stop()

    df = pd.DataFrame(res.json())
    for col in ("submitted", "missing", "total_students"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    total_a   = len(df)
    total_s   = int(df["submitted"].sum())
    total_m   = int(df["missing"].sum())
    total_stu = int(df["total_students"].sum()) if "total_students" in df.columns else total_s + total_m
    comp_rate = round(total_s / max(total_s + total_m, 1) * 100, 1)

    st.markdown(f"""
    <div class="kpi-row">
        {kpi("folder",    "#a78bfa", "rgba(108,99,255,0.14)", "Total Assignments", total_a,         "tracked",            "v")}
        {kpi("users",     "#2dd4bf", "rgba(45,212,191,0.12)", "Student Seats",     total_stu,       "across all domains", "t")}
        {kpi("check-sq",  "#10b981", "rgba(16,185,129,0.12)", "Submitted",         total_s,         f"{comp_rate}% rate", "e")}
        {kpi("x-circle",  "#f43f5e", "rgba(244,63,94,0.12)",  "Missing",           total_m,         "need follow-up",     "r")}
        {kpi("trending",  "#f59e0b", "rgba(245,158,11,0.12)", "Completion Rate",   f"{comp_rate}%", "submitted ÷ total",  "a")}
    </div>""", unsafe_allow_html=True)

    if "domain" in df.columns:
        dg = df.groupby("domain")[["submitted", "missing", "total_students"]].sum().reset_index()
        dg["pct"] = (dg["submitted"] / (dg["submitted"] + dg["missing"]).replace(0, 1) * 100).round(1)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Domain Breakdown", "Completion Rates", "Distribution", "Raw Data"
        ])

        with tab1:
            fig = go.Figure()
            fig.add_bar(x=dg["domain"], y=dg["submitted"], name="Submitted",
                        marker_color=COLORS["emerald"], marker_line_width=0,
                        text=dg["submitted"], textposition="outside",
                        textfont=dict(size=10, family="IBM Plex Mono"))
            fig.add_bar(x=dg["domain"], y=dg["missing"], name="Missing",
                        marker_color=COLORS["rose"], marker_line_width=0,
                        text=dg["missing"], textposition="outside",
                        textfont=dict(size=10, family="IBM Plex Mono"))
            fig.update_layout(**PLOT_BASE, barmode="group",
                              title="Submitted vs Missing by Domain", height=380)
            ax(fig)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig2 = go.Figure(go.Bar(
                x=dg["pct"], y=dg["domain"], orientation="h",
                marker=dict(color=dg["pct"],
                            colorscale=[[0, "#f43f5e"], [0.5, "#f59e0b"], [1, "#10b981"]],
                            showscale=True,
                            colorbar=dict(thickness=10, tickfont=dict(size=9, family="IBM Plex Mono"))),
                text=dg["pct"].astype(str) + "%", textposition="outside",
                textfont=dict(size=10, family="IBM Plex Mono"),
            ))
            fig2.update_layout(**PLOT_BASE, title="Completion Rate (%) by Domain", height=320)
            fig2.update_xaxes(**AX, range=[0, 120])
            fig2.update_yaxes(**AX)
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            col_l, col_r = st.columns(2)
            with col_l:
                fig3 = px.pie(dg, names="domain", values="submitted", hole=0.6,
                              color_discrete_sequence=COLOR_SEQ, title="Submitted by Domain")
                fig3.update_traces(textfont_size=11, textfont_color="#eeedf8",
                                   marker=dict(line=dict(color="#07070e", width=2)))
                fig3.update_layout(**PLOT_BASE, height=340)
                st.plotly_chart(fig3, use_container_width=True)
            with col_r:
                fig4 = px.pie(dg, names="domain", values="missing", hole=0.6,
                              color_discrete_sequence=[COLORS["rose"], COLORS["amber"], COLORS["purple"]],
                              title="Missing by Domain")
                fig4.update_traces(textfont_size=11, textfont_color="#eeedf8",
                                   marker=dict(line=dict(color="#07070e", width=2)))
                fig4.update_layout(**PLOT_BASE, height=340)
                st.plotly_chart(fig4, use_container_width=True)

        with tab4:
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE: STUDENTS
# ══════════════════════════════════════════════════════════════
elif page == "Students":
    header("STUDENT ANALYTICS", "Student Dashboard", "user")

    if not student_id:
        empty_state("user", "No student selected",
                    "Enter a Student ID in the sidebar and click Load Student")
        st.stop()

    res_prog = safe_get(f"{API_BASE}/student-progress/{student_id}")
    res_dash = safe_get(f"{API_BASE}/student-dashboard/{student_id}")

    if res_prog is None:
        st.error(f"Student `{student_id}` not found or API unreachable.")
        st.stop()

    dash_data   = res_dash.json() if res_dash else {}
    notifs      = dash_data.get("notifications", [])
    missed_list = dash_data.get("missed_assignments", [])

    for n in notifs:
        nid = str(n.get("_id", ""))
        if nid and nid not in st.session_state.seen_notif_ids:
            st.session_state.seen_notif_ids.add(nid)
            st.toast(f"Missed: {n.get('assignmentName', 'assignment')}", icon=None)

    p         = res_prog.json()
    name      = p.get("student", student_id)
    domain    = p.get("domain", "—")
    total     = int(p.get("total_assignments", 0))
    submitted = int(p.get("submitted", 0))
    missed    = int(p.get("missed", 0))
    pct       = round(submitted / max(total, 1) * 100, 1)
    on_track  = pct >= 70

    domain_cls   = "bt" if domain == "AI" else "bv" if domain == "Web" else "ba"
    status_badge = (
        f'<span class="badge be">{ico("check-circ", 11, "#10b981")} On Track</span>'
        if on_track else
        f'<span class="badge br">{ico("alert-circ", 11, "#f43f5e")} At Risk</span>'
    )

    st.markdown(f"""
    <div class="s-card">
        <div class="s-avatar">{ico("user", 22, "rgba(255,255,255,0.85)")}</div>
        <div style="flex:1;">
            <div class="s-name">{name}</div>
            <div class="s-id">ID &middot; {student_id}</div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
            <span class="badge {domain_cls}">{ico("tag", 11, "currentColor")} {domain}</span>
            {status_badge}
            <span class="badge bv">{ico("trending", 11, "#a78bfa")} {pct}% complete</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-row">
        {kpi("book-open", "#a78bfa", "rgba(108,99,255,0.14)", "Total Assignments", total,     "in domain",        "v")}
        {kpi("check-sq",  "#10b981", "rgba(16,185,129,0.12)", "Submitted",         submitted, f"{pct}% complete", "e")}
        {kpi("x-circle",  "#f43f5e", "rgba(244,63,94,0.12)",  "Missed",            missed,    "not submitted",    "r")}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slbl">Overall Completion</div>', unsafe_allow_html=True)
    st.progress(pct / 100)
    st.caption(f"{submitted} of {total} assignments submitted — {pct:.1f}%")

    tab_charts, tab_notif = st.tabs(["Progress Charts", "Notifications & Missed"])

    with tab_charts:
        col_l, col_r = st.columns(2)
        with col_l:
            fig = go.Figure(go.Pie(
                labels=["Submitted", "Missed"],
                values=[max(submitted, 0), max(missed, 0)],
                hole=0.62,
                marker=dict(colors=[COLORS["violet"], COLORS["rose"]],
                            line=dict(color="#07070e", width=2)),
                textfont=dict(size=11, color="#eeedf8"),
            ))
            fig.add_annotation(text=f"<b>{pct}%</b>", x=0.5, y=0.5,
                               font=dict(size=22, color="#eeedf8", family="IBM Plex Mono"),
                               showarrow=False)
            fig.update_layout(**PLOT_BASE, title="Assignment Status", height=330, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=pct,
                title={"text": "Completion %", "font": {"color": "#eeedf8", "size": 13, "family": "Inter"}},
                delta={"reference": 80, "suffix": "%", "font": {"size": 12, "family": "IBM Plex Mono"}},
                number={"suffix": "%", "font": {"color": COLORS["violet"], "size": 36, "family": "IBM Plex Mono"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#20202e",
                             "tickfont": {"size": 9, "family": "IBM Plex Mono"}},
                    "bar": {"color": COLORS["violet"], "thickness": 0.22},
                    "bgcolor": "#13131f", "borderwidth": 0,
                    "steps": [
                        {"range": [0,  50], "color": "rgba(244,63,94,0.08)"},
                        {"range": [50, 80], "color": "rgba(245,158,11,0.08)"},
                        {"range": [80,100], "color": "rgba(16,185,129,0.08)"},
                    ],
                    "threshold": {"line": {"color": COLORS["emerald"], "width": 2},
                                  "thickness": 0.75, "value": 80},
                },
            ))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=330,
                               margin=dict(t=36, b=10, l=20, r=20))
            st.plotly_chart(fig2, use_container_width=True)

    with tab_notif:
        if res_dash is None:
            st.warning("Could not load dashboard data for this student.")
        else:
            col_n, col_m = st.columns(2)
            with col_n:
                st.markdown('<div class="slbl">Recent Notifications</div>', unsafe_allow_html=True)
                if not notifs:
                    st.success("No notifications — all assignments are on track.")
                else:
                    for n in notifs:
                        msg     = n.get("message", "")
                        created = fmt_deadline(n.get("createdAt", ""))
                        n_type  = n.get("type", "")
                        ic      = ico("alert-circ", 14, "#f59e0b") if n_type == "deadline_passed" else ico("bell", 14, "#f59e0b")
                        st.markdown(f"""
                        <div class="notif">
                            <div class="notif-icon">{ic}</div>
                            <div>
                                <div class="notif-msg">{msg}</div>
                                <div class="notif-time">{ico("clock", 10, "#4e4c64")} {created}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)

            with col_m:
                st.markdown('<div class="slbl">Missed Assignments</div>', unsafe_allow_html=True)
                if not missed_list:
                    st.success("All assignments submitted — great work.")
                else:
                    for m in missed_list:
                        render_missed_assignment_item(m)


# ══════════════════════════════════════════════════════════════
# PAGE: ASSIGNMENTS
# ══════════════════════════════════════════════════════════════
elif page == "Assignments":
    header("ASSIGNMENT DEEP-DIVE", "Assignment Inspector", "clipboard")

    res_all = safe_get(f"{API_BASE}/assignment-status")
    if res_all is None:
        st.error("Cannot reach API.")
        st.stop()

    df_all = pd.DataFrame(res_all.json())
    for col in ("submitted", "missing", "total_students"):
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce").fillna(0).astype(int)

    if not assignment_id:
        st.markdown("""
        <div style="font-size:0.82rem; color:#9a98b4; margin-bottom:1.2rem;">
            Enter an <strong>Assignment ID</strong> in the sidebar for a deep-dive, or browse all assignments below.
        </div>""", unsafe_allow_html=True)
        if "domain" in df_all.columns:
            dg = df_all.groupby("domain")[["submitted", "missing"]].sum().reset_index()
            fig = go.Figure()
            fig.add_bar(x=dg["domain"], y=dg["submitted"], name="Submitted",
                        marker_color=COLORS["emerald"], marker_line_width=0)
            fig.add_bar(x=dg["domain"], y=dg["missing"],   name="Missing",
                        marker_color=COLORS["rose"],    marker_line_width=0)
            fig.update_layout(**PLOT_BASE, barmode="stack",
                              title="All Assignments — Submitted vs Missing by Domain", height=320)
            ax(fig)
            st.plotly_chart(fig, use_container_width=True)
        df_all["completion %"] = (
            df_all["submitted"] / (df_all["submitted"] + df_all["missing"]).replace(0, 1) * 100
        ).round(1)
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.stop()

    res_miss = safe_get(f"{API_BASE}/missed-students/{assignment_id}")
    if res_miss is None:
        st.error(f"Assignment `{assignment_id}` not found or API unreachable.")
        st.stop()

    miss_data = res_miss.json()

    if "message" in miss_data and "Deadline not passed" in miss_data.get("message", ""):
        a_name  = assignment_id
        m_list  = []
        m_count = 0
        st.info(f"Deadline for `{assignment_id}` has not passed yet — missing student list unavailable.")
    else:
        a_name  = miss_data.get("assignment", assignment_id)
        m_list  = miss_data.get("missing_students", [])
        m_count = int(miss_data.get("missing_count", 0))

    a_domain    = "—"
    a_submitted = 0
    a_total     = 0
    a_pct       = 0.0

    match = df_all[df_all["assignment"] == a_name]
    if not match.empty:
        row         = match.iloc[0]
        a_domain    = str(row.get("domain", "—"))
        a_submitted = int(row["submitted"])
        a_total     = a_submitted + m_count
        a_pct       = round(a_submitted / max(a_total, 1) * 100, 1)

    st.markdown(f"""
    <div class="s-card">
        <div class="s-avatar">{ico("clipboard", 22, "rgba(255,255,255,0.85)")}</div>
        <div style="flex:1;">
            <div class="s-name">{a_name}</div>
            <div class="s-id">ID &middot; {assignment_id}</div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
            <span class="badge bt">{ico("tag", 11, "#2dd4bf")} {a_domain}</span>
            <span class="badge {'be' if a_pct >= 70 else 'br'}">
                {ico("check-circ", 11, "#10b981") if a_pct >= 70 else ico("alert-circ", 11, "#f43f5e")}
                {"On Track" if a_pct >= 70 else "Needs Attention"}
            </span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-row">
        {kpi("users",    "#a78bfa", "rgba(108,99,255,0.14)", "Total Students", a_total,       "enrolled",         "v")}
        {kpi("check-sq", "#10b981", "rgba(16,185,129,0.12)", "Submitted",      a_submitted,   f"{a_pct}% rate",   "e")}
        {kpi("x-circle", "#f43f5e", "rgba(244,63,94,0.12)",  "Missing",        m_count,       "not submitted",    "r")}
        {kpi("trending", "#2dd4bf", "rgba(45,212,191,0.12)", "Completion",     f"{a_pct}%",   "submission rate",  "t")}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slbl">Submission Progress</div>', unsafe_allow_html=True)
    st.progress(a_pct / 100)
    st.caption(f"{a_submitted} submitted · {m_count} remaining · {a_pct}% complete")
    st.markdown("---")

    tab_chart, tab_miss, tab_ctx = st.tabs(["Charts", "Missing Students", "Domain Context"])

    with tab_chart:
        col_l, col_r = st.columns(2)
        with col_l:
            fig = go.Figure(go.Pie(
                labels=["Submitted", "Missing"],
                values=[a_submitted, m_count],
                hole=0.62,
                marker=dict(colors=[COLORS["violet"], COLORS["rose"]],
                            line=dict(color="#07070e", width=2)),
                textfont=dict(size=11, color="#eeedf8"),
            ))
            fig.add_annotation(text=f"<b>{a_pct}%</b>", x=0.5, y=0.5,
                               font=dict(size=22, color="#eeedf8", family="IBM Plex Mono"),
                               showarrow=False)
            fig.update_layout(**PLOT_BASE, title=f"Submission Rate — {a_name}", height=320)
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=a_pct,
                number={"suffix": "%", "font": {"color": COLORS["violet"], "size": 34, "family": "IBM Plex Mono"}},
                title={"text": "Completion Rate", "font": {"color": "#eeedf8", "size": 12, "family": "Inter"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#20202e",
                             "tickfont": {"size": 9, "family": "IBM Plex Mono"}},
                    "bar": {"color": COLORS["violet"], "thickness": 0.2},
                    "bgcolor": "#13131f", "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50],  "color": "rgba(244,63,94,0.08)"},
                        {"range": [50, 80], "color": "rgba(245,158,11,0.08)"},
                        {"range": [80,100], "color": "rgba(16,185,129,0.08)"},
                    ],
                    "threshold": {"line": {"color": COLORS["emerald"], "width": 2},
                                  "thickness": 0.75, "value": 80},
                },
            ))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=320,
                               margin=dict(t=36, b=10, l=20, r=20))
            st.plotly_chart(fig2, use_container_width=True)

    with tab_miss:
        if not m_list:
            st.success("All students have submitted this assignment.")
        else:
            search = st.text_input("", placeholder="Filter by name or email…",
                                   label_visibility="collapsed", key="miss_search")
            filtered = [s for s in m_list if
                        not search or
                        search.lower() in s.get("name", "").lower() or
                        search.lower() in s.get("email", "").lower()]
            st.markdown(f"<div class='slbl'>Showing {len(filtered)} of {m_count} missing students</div>",
                        unsafe_allow_html=True)
            for s in filtered:
                render_missing_student_card(s)
            if filtered:
                names = [s.get("name", "?") for s in filtered[:25]]
                fig_b = go.Figure(go.Bar(
                    y=names[::-1], x=[1] * len(names), orientation="h",
                    marker_color=COLORS["rose"], marker_line_width=0,
                    text=[s.get("email", "") for s in filtered[:25]][::-1],
                    textposition="inside",
                    textfont=dict(size=9, color="#eeedf8", family="IBM Plex Mono"),
                ))
                fig_b.update_layout(
                    **PLOT_BASE, title="Students Yet to Submit",
                    height=max(280, len(names) * 34), showlegend=False,
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                    yaxis=dict(**AX),
                )
                st.plotly_chart(fig_b, use_container_width=True)

    with tab_ctx:
        if a_domain != "—" and "domain" in df_all.columns:
            df_dom = df_all[df_all["domain"] == a_domain].copy()
            df_dom["pct"] = (
                df_dom["submitted"] /
                (df_dom["submitted"] + df_dom["missing"]).replace(0, 1) * 100
            ).round(1)
            clrs = [COLORS["violet"] if r == a_name else "#2a2a3e" for r in df_dom["assignment"]]
            fig_c = go.Figure(go.Bar(
                x=df_dom["assignment"], y=df_dom["pct"],
                marker_color=clrs, marker_line_width=0,
                text=df_dom["pct"].astype(str) + "%", textposition="outside",
                textfont=dict(size=10, family="IBM Plex Mono"),
            ))
            fig_c.update_layout(**PLOT_BASE,
                                title=f"Completion — {a_domain} Domain (all assignments)", height=340)
            ax(fig_c, yr=[0, 120])
            st.plotly_chart(fig_c, use_container_width=True)
            st.caption(f"Highlighted bar = {a_name} (currently selected)")
            st.dataframe(
                df_dom[["assignment", "submitted", "missing", "pct"]].rename(
                    columns={"pct": "completion %"}),
                use_container_width=True, hide_index=True)
        else:
            st.info("Domain information not available for this assignment.")


# ══════════════════════════════════════════════════════════════
# PAGE: MISSED SUBMISSIONS
# ══════════════════════════════════════════════════════════════
elif page == "Missed":
    header("FOLLOW-UP REQUIRED", "Missed Submissions", "alert-tri")

    if not assignment_id:
        empty_state("alert-tri", "No assignment selected",
                    "Enter an Assignment ID in the sidebar and click Load Missing")
        st.stop()

    res = safe_get(f"{API_BASE}/missed-students/{assignment_id}")
    if res is None:
        st.error(f"Assignment `{assignment_id}` not found or API unreachable.")
        st.stop()

    data = res.json()

    if "message" in data and "Deadline not passed" in data.get("message", ""):
        st.info(f"Deadline has not passed yet for `{assignment_id}`. No missed data yet.")
        st.stop()

    m_count = int(data.get("missing_count", 0))
    m_list  = data.get("missing_students", [])
    a_title = data.get("assignment", assignment_id)

    st.markdown(f"""
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1.4rem; align-items:center;">
        <span class="badge bv">{ico("clipboard", 11, "#a78bfa")} {a_title}</span>
        <span class="badge {'br' if m_count else 'be'}">
            {ico("x-circle" if m_count else "check-circ", 11, "#f43f5e" if m_count else "#10b981")}
            {m_count} missing students
        </span>
    </div>""", unsafe_allow_html=True)

    if not m_count or not m_list:
        st.success("Every student submitted this assignment — well done.")
        st.stop()

    st.markdown(f"""
    <div class="kpi-row">
        {kpi("x-circle", "#f43f5e", "rgba(244,63,94,0.12)", "Missing Students", m_count, "need follow-up", "r")}
    </div>""", unsafe_allow_html=True)

    tab_list, tab_chart = st.tabs(["Student List", "Visual Breakdown"])

    with tab_list:
        search = st.text_input("", placeholder="Filter by name or email…",
                               label_visibility="collapsed", key="m_search")
        filtered = [s for s in m_list if
                    not search or
                    search.lower() in s.get("name", "").lower() or
                    search.lower() in s.get("email", "").lower()]
        st.markdown(f"<div class='slbl'>{len(filtered)} of {m_count} students</div>",
                    unsafe_allow_html=True)
        for s in filtered:
            render_missing_student_card(s)

    with tab_chart:
        names = [s.get("name", "?") for s in m_list[:30]]
        fig_h = go.Figure(go.Bar(
            y=names[::-1], x=[1] * len(names), orientation="h",
            marker_color=COLORS["rose"], marker_line_width=0,
            text=[s.get("email", "") for s in m_list[:30]][::-1],
            textposition="inside",
            textfont=dict(size=9, color="#eeedf8", family="IBM Plex Mono"),
        ))
        fig_h.update_layout(
            **PLOT_BASE, title=f"Missing Students — {a_title}",
            height=max(300, len(names) * 36), showlegend=False,
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(**AX),
        )
        st.plotly_chart(fig_h, use_container_width=True)

        st.markdown(f"""
        <div style="background:rgba(244,63,94,0.07); border:1px solid rgba(244,63,94,0.18);
                    border-radius:10px; padding:16px 20px; margin-top:8px;
                    display:flex; align-items:center; gap:14px;">
            {ico_box("x-circle", 18, "rgba(244,63,94,0.14)", "#f43f5e", "9px")}
            <div>
                <div style="font-size:1.05rem; font-weight:700; color:#f43f5e;
                            font-family:'IBM Plex Mono',monospace;">{m_count} students</div>
                <div style="font-size:0.74rem; color:#4e4c64; margin-top:2px;">
                    have not submitted <strong style="color:#9a98b4;">{a_title}</strong>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: SUBMIT ASSIGNMENT
# ══════════════════════════════════════════════════════════════
elif page == "Submit":
    header("SUBMISSION PORTAL", "Submit Assignment", "upload")

    col_form, col_info = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown(f"""
        <div style="background:#13131f; border:1px solid #20202e; border-radius:14px; padding:28px 28px 32px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:18px;">
                {ico("send", 14, "#6c63ff")}
                <span style="font-size:0.6rem; font-family:'IBM Plex Mono',monospace; letter-spacing:2px;
                             text-transform:uppercase; color:#6c63ff;">Assignment Submission Form</span>
            </div>
        """, unsafe_allow_html=True)

        sub_sid  = st.text_input("Student ID",
                                 placeholder="MongoDB ObjectId of the student",   key="sub_sid")
        sub_aid  = st.text_input("Assignment ID",
                                 placeholder="MongoDB ObjectId of the assignment", key="sub_aid")
        sub_link = st.text_input("Submission Link",
                                 placeholder="https://github.com/you/project",    key="sub_link")

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; font-size:0.68rem; color:#4e4c64;
                    font-family:'IBM Plex Mono',monospace; margin-top:-6px; margin-bottom:18px;">
            {ico("link", 12, "#4e4c64")} Accepted: GitHub · Vercel · Streamlit · Figma
        </div>""", unsafe_allow_html=True)

        btn = st.button("Submit Assignment", key="sub_btn")
        st.markdown("</div>", unsafe_allow_html=True)

        if btn:
            if not sub_sid or not sub_aid or not sub_link:
                st.warning("All three fields are required.")
            else:
                payload = {
                    "studentId":    sub_sid.strip(),
                    "assignmentId": sub_aid.strip(),
                    "link":         sub_link.strip(),
                }
                with st.spinner("Validating and submitting…"):
                    try:
                        r = requests.post(f"{API_BASE}/submit", json=payload, timeout=60)
                    except Exception as e:
                        r = None
                        st.error(f"Network error: {e}")

                if r is not None:
                    if r.status_code == 200:
                        resp = r.json()
                        sim  = resp.get("similarity", 0)
                        st.success("Assignment submitted successfully.")
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="result-eyebrow">
                                {ico("check-circ", 13, "#10b981")} Submission Result
                            </div>
                            <div class="result-grid">
                                <div>
                                    <div class="result-field-lbl">STUDENT ID</div>
                                    <div class="result-field-val">{sub_sid}</div>
                                </div>
                                <div>
                                    <div class="result-field-lbl">ASSIGNMENT ID</div>
                                    <div class="result-field-val">{sub_aid}</div>
                                </div>
                                <div>
                                    <div class="result-field-lbl">SIMILARITY SCORE</div>
                                    <div class="result-field-val teal">{sim:.2%}</div>
                                </div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        try:
                            detail = r.json().get("detail", r.text)
                        except Exception:
                            detail = r.text
                        st.error(f"Submission failed ({r.status_code}): {detail}")

    with col_info:
        st.markdown(f"""
        <div class="guide-card">

            <div class="guide-header">
                <div class="guide-eyebrow">How it works</div>
                <div class="guide-title">Submission Guidelines</div>
            </div>

            <div class="guide-item">
                <div class="guide-ico">{ico("link", 16, "#a78bfa")}</div>
                <div>
                    <div class="guide-lbl">Accepted Platforms</div>
                    <div class="guide-desc">Your link must point to a publicly accessible project hosted on one of these platforms.</div>
                    <div style="margin-top:7px;">
                        <span class="guide-pill">GitHub</span>
                        <span class="guide-pill">Vercel</span>
                        <span class="guide-pill">Streamlit</span>
                        <span class="guide-pill">Figma</span>
                    </div>
                </div>
            </div>

            <div class="guide-item">
                <div class="guide-ico">{ico("tag", 16, "#2dd4bf")}</div>
                <div>
                    <div class="guide-lbl">Domain-Platform Rules</div>
                    <div class="guide-desc">Each domain only accepts submissions from specific platforms.</div>
                    <div style="margin-top:8px; display:flex; flex-direction:column; gap:5px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="badge bt" style="font-size:0.6rem; padding:2px 8px;">AI</span>
                            <span style="font-size:0.72rem; color:#4e4c64; font-family:'IBM Plex Mono',monospace;">GitHub &middot; Streamlit</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="badge bv" style="font-size:0.6rem; padding:2px 8px;">Web</span>
                            <span style="font-size:0.72rem; color:#4e4c64; font-family:'IBM Plex Mono',monospace;">GitHub &middot; Vercel</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="badge ba" style="font-size:0.6rem; padding:2px 8px;">UI/UX</span>
                            <span style="font-size:0.72rem; color:#4e4c64; font-family:'IBM Plex Mono',monospace;">Figma</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="guide-item">
                <div class="guide-ico">{ico("clock", 16, "#f59e0b")}</div>
                <div>
                    <div class="guide-lbl">Deadline is Strict</div>
                    <div class="guide-desc">Submissions are timestamped on arrival. Any submission after the deadline is automatically rejected — no exceptions.</div>
                </div>
            </div>

            <div class="guide-item">
                <div class="guide-ico">{ico("shield", 16, "#f43f5e")}</div>
                <div>
                    <div class="guide-lbl">Plagiarism Check</div>
                    <div class="guide-desc">Every submission is compared against your own previous work using content similarity scoring.</div>
                    <div style="margin-top:7px; display:flex; gap:6px; flex-wrap:wrap;">
                        <span class="guide-pill g">Below 60% — Accepted</span>
                        <span class="guide-pill r">60% or above — Rejected</span>
                    </div>
                </div>
            </div>

            <div class="guide-item">
                <div class="guide-ico">{ico("hash", 16, "#9a98b4")}</div>
                <div>
                    <div class="guide-lbl">Use Exact IDs</div>
                    <div class="guide-desc">Both Student ID and Assignment ID must be the exact 24-character MongoDB ObjectIds provided by your instructor. Partial or incorrect IDs will fail.</div>
                </div>
            </div>

        </div>""", unsafe_allow_html=True)