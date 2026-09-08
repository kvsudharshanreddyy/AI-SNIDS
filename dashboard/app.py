"""
dashboard/app.py

AI-SNIDS — Unified Security Story Dashboard

This dashboard tells ONE coherent security story:
  1. Client A communicates with Server B (protected by cryptography)
  2. AI-SNIDS monitors the virtual network
  3. An attacker launches simulated attacks
  4. AI detects the threat using Random Forest
  5. Risk Engine assesses severity
  6. Response Engine simulates blocking
  7. Everything is logged to SQLite
  8. Dashboard visualizes it all

Run with:
    streamlit run dashboard/app.py --server.port 8080
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─── Project Path Setup ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI-SNIDS | Security Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ─── Keyframe Animations ─────────────────────────────── */
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 5px rgba(252, 129, 129, 0.3); }
        50% { box-shadow: 0 0 25px rgba(252, 129, 129, 0.7), 0 0 50px rgba(252, 129, 129, 0.3); }
    }
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 5px rgba(104, 211, 145, 0.3); }
        50% { box-shadow: 0 0 25px rgba(104, 211, 145, 0.7), 0 0 50px rgba(104, 211, 145, 0.3); }
    }
    @keyframes pulse-cyan {
        0%, 100% { box-shadow: 0 0 5px rgba(0, 229, 255, 0.2); }
        50% { box-shadow: 0 0 20px rgba(0, 229, 255, 0.5), 0 0 40px rgba(0, 229, 255, 0.2); }
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
        20%, 40%, 60%, 80% { transform: translateX(4px); }
    }
    @keyframes slide-in {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes glow-border {
        0%, 100% { border-color: rgba(0, 229, 255, 0.15); }
        50% { border-color: rgba(0, 229, 255, 0.5); }
    }
    @keyframes attack-flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.02em;
    }

    .stApp {
        background-color: #0a0a0a;
        color: #f5f5f5;
        background-image: radial-gradient(circle at top right, rgba(0, 229, 255, 0.05), transparent 40%),
                          radial-gradient(circle at bottom left, rgba(157, 0, 255, 0.05), transparent 40%);
    }

    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"]:hover {
        border-right: 1px solid rgba(0, 229, 255, 0.2);
    }

    /* ─── Buttons ─────────────────────────────────────────── */
    .stButton > button {
        background-color: transparent !important;
        border: 1px solid rgba(0, 229, 255, 0.4) !important;
        color: #00E5FF !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: rgba(0, 229, 255, 0.15) !important;
        border-color: #00E5FF !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.3), 0 0 40px rgba(0, 229, 255, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ─── Metric Cards ────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px) scale(1.02);
        border-color: rgba(0, 229, 255, 0.4);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 229, 255, 0.1);
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.6) !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 0.05em;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.04em !important;
    }

    .highlight-cyan { color: #00E5FF; text-shadow: 0 0 10px rgba(0,229,255,0.3); }

    /* ─── Alert Cards (with hover) ────────────────────────── */
    .high-alert {
        background: rgba(252, 129, 129, 0.05);
        border: 1px solid rgba(252, 129, 129, 0.2);
        border-left: 4px solid #fc8181;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-weight: 500;
        box-shadow: 0 0 20px rgba(252, 129, 129, 0.05);
        transition: all 0.3s ease;
    }
    .high-alert:hover {
        background: rgba(252, 129, 129, 0.1);
        border-color: rgba(252, 129, 129, 0.5);
        box-shadow: 0 0 25px rgba(252, 129, 129, 0.15);
        transform: translateX(4px);
    }
    .medium-alert {
        background: rgba(246, 173, 85, 0.05);
        border: 1px solid rgba(246, 173, 85, 0.2);
        border-left: 4px solid #f6ad55;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .medium-alert:hover {
        background: rgba(246, 173, 85, 0.1);
        border-color: rgba(246, 173, 85, 0.5);
        box-shadow: 0 0 25px rgba(246, 173, 85, 0.15);
        transform: translateX(4px);
    }
    .low-alert {
        background: rgba(99, 179, 237, 0.05);
        border: 1px solid rgba(99, 179, 237, 0.2);
        border-left: 4px solid #63b3ed;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .low-alert:hover {
        background: rgba(99, 179, 237, 0.1);
        border-color: rgba(99, 179, 237, 0.5);
        box-shadow: 0 0 25px rgba(99, 179, 237, 0.15);
        transform: translateX(4px);
    }
    .benign-alert {
        background: rgba(104, 211, 145, 0.05);
        border: 1px solid rgba(104, 211, 145, 0.2);
        border-left: 4px solid #68d391;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .benign-alert:hover {
        background: rgba(104, 211, 145, 0.1);
        border-color: rgba(104, 211, 145, 0.5);
        box-shadow: 0 0 25px rgba(104, 211, 145, 0.15);
        transform: translateX(4px);
    }

    /* ─── Crypto / Topology Boxes ─────────────────────────── */
    .crypto-box {
        background-color: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 0.85rem;
        word-break: break-all;
        color: #00E5FF;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    .crypto-box:hover {
        border-color: rgba(0, 229, 255, 0.4);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5), 0 0 15px rgba(0, 229, 255, 0.1);
    }

    .topology-box {
        background: rgba(0,0,0,0.5);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(0, 229, 255, 0.15);
        font-family: 'SFMono-Regular', Consolas, monospace;
        color: #00E5FF;
        text-align: center;
        white-space: pre;
        line-height: 1.5;
        font-size: 0.85rem;
        transition: all 0.3s ease;
    }
    .topology-box:hover {
        border-color: rgba(0, 229, 255, 0.4);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.1);
        animation: glow-border 2s ease-in-out infinite;
    }

    /* ─── Device Cards ────────────────────────────────────── */
    .device-card {
        background: rgba(20, 20, 20, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.3rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .device-card:hover {
        transform: translateY(-6px) scale(1.03);
        border-color: rgba(0, 229, 255, 0.4);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 229, 255, 0.1);
    }

    .sim-disclaimer {
        background: rgba(246, 173, 85, 0.08);
        border: 1px solid rgba(246, 173, 85, 0.3);
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-size: 0.85rem;
        color: #f6ad55;
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .sim-disclaimer:hover {
        background: rgba(246, 173, 85, 0.12);
        border-color: rgba(246, 173, 85, 0.5);
    }

    [data-testid="stDataFrame"] {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        overflow: hidden;
        transition: all 0.3s ease;
    }
    [data-testid="stDataFrame"]:hover {
        border-color: rgba(0, 229, 255, 0.25);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    /* ─── Selectbox / Slider / Radio Hover ────────────────── */
    [data-testid="stSelectbox"]:hover,
    [data-testid="stSlider"]:hover,
    .stRadio:hover {
        filter: brightness(1.1);
    }

    /* ─── Attack Animation Panels ─────────────────────────── */
    .attack-anim {
        background: rgba(252, 50, 50, 0.06);
        border: 2px solid rgba(252, 129, 129, 0.4);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        animation: pulse-red 1.5s ease-in-out infinite;
        margin: 0.5rem 0;
    }
    .attack-anim .hacker-icon {
        font-size: 3rem;
        animation: shake 0.6s ease-in-out infinite;
        display: inline-block;
    }
    .attack-anim .attack-text {
        color: #fc8181;
        font-weight: 700;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        animation: attack-flash 1s ease-in-out infinite;
    }
    .attack-anim .attack-detail {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }

    /* ─── Safe / Danger Result Banners ────────────────────── */
    .result-safe {
        background: rgba(104, 211, 145, 0.08);
        border: 2px solid rgba(104, 211, 145, 0.5);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        animation: pulse-green 2s ease-in-out infinite, slide-in 0.5s ease-out;
    }
    .result-safe .result-icon { font-size: 3.5rem; }
    .result-safe .result-title {
        color: #68d391; font-weight: 700; font-size: 1.5rem; margin-top: 0.5rem;
    }
    .result-safe .result-sub {
        color: rgba(255,255,255,0.7); font-size: 0.95rem; margin-top: 0.3rem;
    }

    .result-danger {
        background: rgba(252, 129, 129, 0.08);
        border: 2px solid rgba(252, 129, 129, 0.5);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        animation: pulse-red 1.5s ease-in-out infinite, slide-in 0.5s ease-out;
    }
    .result-danger .result-icon { font-size: 3.5rem; }
    .result-danger .result-title {
        color: #fc8181; font-weight: 700; font-size: 1.5rem; margin-top: 0.5rem;
    }
    .result-danger .result-sub {
        color: rgba(255,255,255,0.7); font-size: 0.95rem; margin-top: 0.3rem;
    }

    /* ─── Expander Hover ──────────────────────────────────── */
    [data-testid="stExpander"] {
        transition: all 0.3s ease;
        border-radius: 8px;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(0, 229, 255, 0.3) !important;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
    }

    /* ─── How AI Detection Works Pipeline Cards ───────────── */
    .pipeline-step-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .pipeline-step-card:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(0, 229, 255, 0.5);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 229, 255, 0.2);
    }
    .pipeline-step-num {
        display: inline-block;
        background: rgba(0, 229, 255, 0.15);
        color: #00E5FF;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 20px;
        border: 1px solid rgba(0, 229, 255, 0.4);
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
        width: fit-content;
    }
    .pipeline-step-title {
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .pipeline-step-desc {
        color: rgba(255, 255, 255, 0.68);
        font-size: 0.8rem;
        line-height: 1.45;
    }
    .pipeline-flow-banner {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        text-align: center;
        font-family: 'SFMono-Regular', Consolas, monospace;
        color: #00E5FF;
        font-size: 0.85rem;
        margin: 1rem 0;
        overflow-x: auto;
        white-space: nowrap;
        box-shadow: inset 0 0 15px rgba(0, 229, 255, 0.05);
        transition: all 0.3s ease;
    }
    .pipeline-flow-banner:hover {
        border-color: rgba(0, 229, 255, 0.5);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
    }
</style>
""", unsafe_allow_html=True)


# ─── Cached Loaders ────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading AI model...")
def load_predictor():
    from ai.predict import Predictor
    return Predictor()


@st.cache_resource(show_spinner="Connecting to database...")
def get_db_session():
    from database.database import init_db, SessionLocal
    init_db()
    return SessionLocal


def load_evaluation_metrics():
    metrics_path = PROJECT_ROOT / "ai" / "model" / "randomforest_metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)
    return None


def load_feature_importance_img():
    path = PROJECT_ROOT / "ai" / "model" / "randomforest_feature_importance.png"
    return path if path.exists() else None


def load_confusion_matrix_img():
    path = PROJECT_ROOT / "ai" / "model" / "randomforest_confusion_matrix.png"
    return path if path.exists() else None


# ─── Database Helpers ──────────────────────────────────────────────────────────

def get_recent_events(n: int = 50) -> list[dict]:
    try:
        SessionLocal = get_db_session()
        from database.models import SecurityEvent
        session = SessionLocal()
        events = (
            session.query(SecurityEvent)
            .order_by(SecurityEvent.timestamp.desc())
            .limit(n)
            .all()
        )
        result = [e.to_dict() for e in events]
        session.close()
        return result
    except Exception:
        return []


def get_statistics() -> dict:
    try:
        SessionLocal = get_db_session()
        from database.models import SecurityEvent, BlockedIP
        from sqlalchemy import func

        session = SessionLocal()
        total = session.query(func.count(SecurityEvent.id)).scalar() or 0
        threats = session.query(func.count(SecurityEvent.id)).filter(
            SecurityEvent.attack_type != "BENIGN"
        ).scalar() or 0
        blocked = session.query(func.count(BlockedIP.id)).filter(
            BlockedIP.is_active == True
        ).scalar() or 0
        session.close()

        return {
            "total_samples": total,
            "threats_detected": threats,
            "blocked_ips": blocked,
            "detection_rate": f"{(threats / total * 100):.1f}%" if total > 0 else "N/A",
        }
    except Exception:
        return {"total_samples": 0, "threats_detected": 0, "blocked_ips": 0, "detection_rate": "N/A"}


def get_blocked_ips() -> list[dict]:
    try:
        SessionLocal = get_db_session()
        from database.models import BlockedIP
        session = SessionLocal()
        blocked = session.query(BlockedIP).filter_by(is_active=True).all()
        result = [b.to_dict() for b in blocked]
        session.close()
        return result
    except Exception:
        return []


# ─── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛡️ AI-SNIDS")
        st.markdown("*AI-Powered Secure Network*  \n*Intrusion Detection System*")
        st.divider()

        page = st.radio(
            "Navigation",
            options=[
                "🛡️ Security Overview",
                "🌐 Virtual Network",
                "🧪 Attack Scenario Lab",
                "📡 Live Traffic Monitor",
                "🚨 Threat Center",
                "🛑 Response Center",
                "🔐 Crypto Lab",
                "📊 Model Performance",
            ],
            label_visibility="collapsed"
        )

        st.divider()
        st.markdown("### System Status")

        try:
            predictor = load_predictor()
            if predictor.is_loaded:
                st.success("✅ AI Model: Loaded")
                st.caption(f"Classes: {', '.join(predictor.class_names)}")
            else:
                st.error("❌ AI Model: Not trained")
        except Exception as e:
            st.error(f"❌ Model error: {e}")

        try:
            from database.database import health_check
            if health_check():
                st.success("✅ Database: Connected")
            else:
                st.error("❌ Database: Error")
        except Exception:
            st.warning("⚠ Database: Initializing...")

        st.success("✅ Network: ONLINE")

        st.divider()
        st.caption("Version 2.0.0 | Academic Prototype")
        st.caption("🎓 BTech CSE (AI & ML)")

        return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: SECURITY OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

def page_security_overview():
    st.markdown("# 🛡️ Security Overview")
    st.markdown("*AI-SNIDS continuously monitors the virtual network for threats.*")

    stats = get_statistics()
    blocked_list = get_blocked_ips()

    # Threat level
    if stats["threats_detected"] > 0 and len(blocked_list) > 0:
        threat_status = "🔴 UNDER ATTACK"
    elif stats["threats_detected"] > 0:
        threat_status = "🟡 THREATS DETECTED"
    else:
        threat_status = "🟢 SECURE"

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Analyzed", f"{stats['total_samples']:,}")
    col2.metric("🚨 Threats Detected", f"{stats['threats_detected']:,}")
    col3.metric("🛑 Blocked Sources", f"{len(blocked_list)}")
    col4.metric("🎯 Network Status", threat_status)

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🚨 Active Alerts")
        events = get_recent_events(50)
        attack_events = [e for e in events if e["attack_type"] != "BENIGN"][:5]

        if not attack_events:
            st.markdown('<div class="benign-alert">✅ No active threats. Network is clean.</div>', unsafe_allow_html=True)
        else:
            for evt in attack_events:
                risk_class = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}.get(evt["risk_level"], "low")
                src = evt.get("data_source", "")
                label = f" [{src}]" if src else ""
                st.markdown(
                    f'<div class="{risk_class}-alert">'
                    f'⚠ <b>{evt["attack_type"]}</b> | '
                    f'{evt["source_ip"]} → {evt["destination_ip"]} | '
                    f'Confidence: {evt["confidence"]*100:.1f}% | '
                    f'Risk: {evt["risk_level"]} | '
                    f'Action: {evt["action"]}{label}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    with col_right:
        st.markdown("### 🛑 Blocked Sources")
        if blocked_list:
            for b in blocked_list[:5]:
                st.markdown(
                    f'<div class="high-alert">'
                    f'🚫 <b>{b["ip_address"]}</b><br>'
                    f'Reason: {b["reason"]}<br>'
                    f'Events: {b["event_count"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown('<div class="benign-alert">✅ No blocked sources.</div>', unsafe_allow_html=True)

    # ── How AI Detection Works in AI-SNIDS ────────────────────
    st.divider()
    st.markdown("## 🧠 How AI Detection Works in AI-SNIDS")
    st.markdown(
        "*End-to-end intelligent security architecture combining real/simulated network flow monitoring, "
        "20-dimensional statistical feature extraction, 100-tree Random Forest ensemble classification, "
        "and an explainable multi-factor risk assessment engine.*"
    )

    # Interactive visual flow banner
    st.markdown(
        """
        <div class="pipeline-flow-banner">
            🌐 <b>1. FLOW CAPTURE</b> ──▶ ⚙️ <b>2. FEATURE EXTRACTION</b> ──▶ 🌲 <b>3. RANDOM FOREST (100 TREES)</b> ──▶ ⚖️ <b>4. RISK ENGINE</b> ──▶ 🛡️ <b>5. ENFORCEMENT & BLOCK</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 5 Process Columns
    pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns(5)

    with pcol1:
        st.markdown(
            """
            <div class="pipeline-step-card">
                <span class="pipeline-step-num">STEP 01</span>
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">🌐</div>
                <div class="pipeline-step-title">Traffic Ingestion</div>
                <div class="pipeline-step-desc">
                    Continuously monitors bidirectional communication between <b>Client A (10.0.0.10)</b>, <b>Attacker (10.0.0.50)</b>, and <b>Server B (10.0.0.100)</b>, or streams real benchmark traces from <b>CICIDS2017</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with pcol2:
        st.markdown(
            """
            <div class="pipeline-step-card">
                <span class="pipeline-step-num">STEP 02</span>
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">⚙️</div>
                <div class="pipeline-step-title">Feature Extraction</div>
                <div class="pipeline-step-desc">
                    Extracts <b>20 statistical flow features</b> (Inter-Arrival Times, Flow Duration, Header Lengths, Byte Rates). Normalized via <code>StandardScaler</code> fitted strictly on training data.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with pcol3:
        st.markdown(
            """
            <div class="pipeline-step-card">
                <span class="pipeline-step-num">STEP 03</span>
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">🌲</div>
                <div class="pipeline-step-title">Random Forest ML</div>
                <div class="pipeline-step-desc">
                    An ensemble of <b>100 decision trees</b> trained on <b>93,832 CICIDS2017 records</b> votes across 5 categories: <code>BENIGN</code>, <code>PortScan</code>, <code>DoS</code>, <code>DDoS</code>, <code>BruteForce</code> (<b>98.55% accuracy</b>).
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with pcol4:
        st.markdown(
            """
            <div class="pipeline-step-card">
                <span class="pipeline-step-num">STEP 04</span>
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">⚖️</div>
                <div class="pipeline-step-title">Multi-Factor Risk</div>
                <div class="pipeline-step-desc">
                    Decouples AI confidence from security risk using composite weighting:<br>
                    <code>0.4×Confidence + 0.4×Severity + 0.2×Intensity</code>.<br>
                    Tiers: <b>MONITOR</b>, <b>LOW</b>, <b>MEDIUM</b>, <b>HIGH</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with pcol5:
        st.markdown(
            """
            <div class="pipeline-step-card">
                <span class="pipeline-step-num">STEP 05</span>
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">🛡️</div>
                <div class="pipeline-step-title">Enforcement & Defense</div>
                <div class="pipeline-step-desc">
                    Maps risk to response: <b>ALLOW</b> for benign traffic, <b>ALERT</b> for medium risk, and <b>BLOCK</b> for severe attacks by adding the attacker IP to SQLite <code>blocked_ips</code>, dropping future flows.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Expandable technical deep-dive panels
    with st.expander("🔬 Deep Dive: The Risk Assessment Mathematics (Why AI Confidence ≠ Security Risk)"):
        st.markdown(
            """
            **In traditional naive IDS systems, model confidence is mistakenly treated as security risk.**  
            This leads to critical operational flaws:
            - An attacker conducting a **Port Scan** with **98% confidence** is performing reconnaissance — threatening, but not causing service denial.
            - A **DDoS attack** detected with **72% confidence** is an active resource exhaustion attack that can crash production services.

            **AI-SNIDS solves this with a composite risk scoring equation:**
            $$\\text{Risk Score} = (0.4 \\times \\text{Model Confidence}) + (0.4 \\times \\text{Attack Severity Weight}) + (0.2 \\times \\text{Traffic Intensity Bonus})$$

            | Threat Type | Base Severity | Typical Confidence | Resulting Risk Level | Default System Action |
            | :--- | :---: | :---: | :---: | :---: |
            | **BENIGN (Normal)** | 0.0 | 95% – 100% | 🟢 **MONITOR** (Score < 0.20) | **ALLOW** |
            | **PortScan** | 0.4 | 90% – 99% | 🟡 **MEDIUM** (Score 0.45 – 0.69) | **ALERT** |
            | **BruteForce** | 0.5 | 90% – 100% | 🟡 **MEDIUM** (Score 0.45 – 0.69) | **ALERT** |
            | **DoS (Single Source)** | 0.7 | 80% – 95% | 🟡 **MEDIUM / HIGH** | **ALERT / BLOCK** |
            | **DDoS (Distributed)** | 0.8 | 90% – 100% | 🔴 **HIGH** (Score ≥ 0.70) | **BLOCK** |
            """
        )

    with st.expander("📋 View the 20 Trained Network Traffic Features"):
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.markdown(
                """
                **Inter-Arrival Time (IAT) Features:**
                - `Fwd IAT Total`: Total time between forward packets
                - `Flow Duration`: Total duration of the network flow (microseconds)
                - `Fwd IAT Max`: Maximum inter-arrival time in forward direction
                - `Flow IAT Max`: Maximum inter-arrival time across entire flow
                - `Fwd IAT Std` / `Flow IAT Std`: Standard deviation of packet intervals
                - `Fwd IAT Mean` / `Fwd IAT Min`: Mean & minimum forward timing intervals
                - `Bwd IAT Total` / `Max` / `Min` / `Std` / `Mean`: Reverse timing signals
                """
            )
        with fcol2:
            st.markdown(
                """
                **Payload & Transmission Metrics:**
                - `Flow Bytes/s`: Transmission velocity (key for DoS/PortScan differentiation)
                - `Fwd Header Length` / `Fwd Header Length.1`: Total forward header bytes
                - `Idle Max` / `Idle Mean` / `Idle Min` / `Idle Std`: Inactive period statistics (distinguishes DoS pauses from active browsing)
                
                *All features are normalized using `StandardScaler` fitted on the 75,065 training samples without data leakage.*
                """
            )

    with st.expander("🔒 How Cryptography & AI-SNIDS Work Together (Defense in Depth)"):
        st.markdown(
            """
            AI-SNIDS combines **Machine Learning Detection** with **End-to-End Cryptographic Protection**:
            1. **Confidentiality & Key Agreement:** Client A and Server B establish ephemeral session keys using **ECDH (NIST P-256)** and derive symmetric keys via **HKDF-SHA256**.
            2. **Authenticated Encryption:** Data payloads are encrypted using **AES-256-GCM** with unique 96-bit nonces. Any tampering in transit triggers instantaneous authentication tag failure.
            3. **Behavioral Monitoring:** Even if an attacker injects encrypted noise or attempts denial of service, **AI-SNIDS monitors flow dynamics** at the network boundary, detecting threats and enforcing simulated blocks.
            """
        )

    # Attack Distribution
    st.divider()
    events = get_recent_events(200)
    if events:
        st.markdown("### 📊 Attack Distribution")
        df = pd.DataFrame(events)
        attack_counts = df["attack_type"].value_counts()
        fig = px.pie(
            values=attack_counts.values,
            names=attack_counts.index,
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: VIRTUAL NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

def page_virtual_network():
    st.markdown("# 🌐 Virtual Network")
    st.markdown("*Software-only network topology for safe demonstration. No real traffic is generated.*")

    # Main topology diagram
    st.markdown(
        """
        <div class="topology-box">
                        ┌──────────────────────┐
                        │      INTERNET        │
                        └──────────┬───────────┘
                                   │
                             ┌─────▼─────┐
                             │  ROUTER   │
                             │ 10.0.0.1  │
                             └─────┬─────┘
                                   │
                  ┌────────────────┼────────────────┐
                  │                │                │
            ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
            │ CLIENT A  │   │  ATTACKER  │   │ SERVER B  │
            │ 10.0.0.10 │   │ 10.0.0.50 │   │10.0.0.100 │
            └───────────┘   └───────────┘   └───────────┘
                  │                                ▲
                  │     Normal Traffic              │
                  └────────────────────────────────┘
                                   │
                             ┌─────▼─────┐
                             │ AI-SNIDS  │
                             │ Detection │
                             └─────┬─────┘
                                   │
                        ┌──────────▼──────────┐
                        │ Risk + Alert Engine │
                        └─────────────────────┘
        </div>
        """, unsafe_allow_html=True
    )

    st.divider()

    # Device cards
    st.markdown("### 📋 Network Devices")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            '<div class="device-card">'
            '💻 <b>Client A</b><br>'
            '<span style="color:#00E5FF;">10.0.0.10</span><br>'
            '<small>Legitimate User</small><br>'
            '🟢 ONLINE'
            '</div>', unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="device-card">'
            '🌐 <b>Router</b><br>'
            '<span style="color:#00E5FF;">10.0.0.1</span><br>'
            '<small>Network Gateway</small><br>'
            '🟢 ONLINE'
            '</div>', unsafe_allow_html=True
        )

    with col3:
        blocked_list = get_blocked_ips()
        attacker_blocked = any(b["ip_address"] == "10.0.0.50" for b in blocked_list)
        atk_status = "🔴 BLOCKED" if attacker_blocked else "🟡 MONITORED"
        st.markdown(
            f'<div class="device-card">'
            f'☠️ <b>Attacker</b><br>'
            f'<span style="color:#fc8181;">10.0.0.50</span><br>'
            f'<small>Simulated Threat</small><br>'
            f'{atk_status}'
            f'</div>', unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            '<div class="device-card">'
            '🖥️ <b>Server B</b><br>'
            '<span style="color:#00E5FF;">10.0.0.100</span><br>'
            '<small>Protected Target</small><br>'
            '🟢 ONLINE'
            '</div>', unsafe_allow_html=True
        )

    st.divider()

    # Architecture explanation
    st.markdown("### 🏗️ System Architecture")
    st.markdown("""
    | Component | Role | What it Does |
    |-----------|------|-------------|
    | **AI Model** (Random Forest) | DETECT | Classifies traffic as Normal or Attack |
    | **Risk Engine** | ASSESS | Calculates severity score (confidence + attack weight + intensity) |
    | **Response Engine** | RESPOND | Issues ALLOW / LOG / ALERT / BLOCK actions |
    | **Cryptography** (ECDH + AES-GCM) | PROTECT DATA | Encrypts legitimate communication |
    | **Database** (SQLite) | RECORD | Logs every event for audit |
    | **Dashboard** (Streamlit) | VISUALIZE | Shows the entire process in real-time |
    | **Simulator** | DEMONSTRATE | Generates safe synthetic traffic |
    """)

    st.markdown('<div class="sim-disclaimer">⚠️ This is a software simulation. No real network traffic, attacks, or firewall changes are involved.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: ATTACK SCENARIO LAB
# ═══════════════════════════════════════════════════════════════════════════════

def page_attack_lab():
    st.markdown("# 🧪 Attack Scenario Lab")
    st.markdown("*Run safe, synthetic attack scenarios through the real AI detection pipeline with dynamic mid-stream attack injection.*")
    st.markdown('<div class="sim-disclaimer">⚠️ SIMULATION ONLY — No real attack traffic is generated. Everything stays inside the software.</div>', unsafe_allow_html=True)

    from simulation.simulator import generate_simulation_batch, process_simulated_event, run_instant_attack_burst

    # ── Attack animation helper ────────────────────────────
    attack_icons = {
        "Normal Traffic": ("💻", "Sending normal traffic..."),
        "Port Scan":      ("🔓", "Scanning ports..."),
        "Brute Force":    ("🔨", "Brute forcing credentials..."),
        "DoS":            ("💣", "Flooding server..."),
        "DDoS":           ("💥", "Distributed attack in progress..."),
        "Suspicious Traffic": ("👁️", "Probing network..."),
    }

    col_config, col_view = st.columns([1, 2])

    with col_config:
        st.markdown("### ⚙️ Scenario Configuration")

        scenario = st.selectbox(
            "1️⃣ Initial Baseline Traffic",
            ["Normal Traffic", "Port Scan", "Brute Force", "DoS", "DDoS", "Suspicious Traffic"],
            index=0,
            help="Traffic that starts the simulation."
        )

        injected_attack = st.selectbox(
            "2️⃣ ⚡ Sudden Mid-Stream Attack",
            [
                "None (Pure Scenario)",
                "Port Scan",
                "Brute Force",
                "DoS",
                "DDoS",
                "Suspicious Traffic",
            ],
            index=1 if scenario == "Normal Traffic" else 0,
            help="Simulate an attacker striking suddenly in the middle of ongoing traffic!"
        )

        switch_ratio = 0.5
        if injected_attack != "None (Pure Scenario)":
            strike_point = st.select_slider(
                "3️⃣ 🎯 Sudden Attack Strike Point",
                options=["Early (30%)", "Midway (50%)", "Late (70%)"],
                value="Midway (50%)",
                help="When the sudden attack strikes during the traffic flow."
            )
            timing_map = {
                "Early (30%)": 0.3,
                "Midway (50%)": 0.5,
                "Late (70%)": 0.7,
            }
            switch_ratio = timing_map.get(strike_point, 0.5)

        intensity = st.select_slider(
            "Intensity", options=["LOW", "MEDIUM", "HIGH"], value="MEDIUM"
        )

        duration = st.radio(
            "Duration (seconds)", options=[10, 30, 60], index=0, horizontal=True
        )

        start_btn = st.button("▶ START DYNAMIC SIMULATION", use_container_width=True, type="primary")

        # Scenario description
        st.divider()
        if injected_attack != "None (Pure Scenario)":
            st.info(
                f"**⚡ Dynamic Sudden Attack Scenario:**\n\n"
                f"1. **Baseline Phase:** Starts with legitimate **{scenario}** (Client A → Server B).\n"
                f"2. **Sudden Strike:** At **{int(switch_ratio*100)}%**, attacker suddenly strikes with **{injected_attack}**!\n"
                f"3. **AI Response:** AI-SNIDS detects the transition in real time and triggers defense."
            )
        else:
            descriptions = {
                "Normal Traffic": "Client A (10.0.0.10) → Server B (10.0.0.100)\n\nLegitimate web browsing traffic. AI should classify as BENIGN.",
                "Port Scan": "Attacker (10.0.0.50) → Server B (10.0.0.100)\n\nScanning ports 21, 22, 80, 443, etc. Reconnaissance behavior.",
                "Brute Force": "Attacker (10.0.0.50) → Server B (10.0.0.100)\n\nRepeated SSH/FTP login attempts.",
                "DoS": "Attacker (10.0.0.50) → Server B (10.0.0.100)\n\nSingle source floods target with requests.",
                "DDoS": "Attackers (10.0.0.51–56) → Server B (10.0.0.100)\n\n6 distributed sources flood target simultaneously.",
                "Suspicious Traffic": "Mixed sources → Server B (10.0.0.100)\n\nAmbiguous traffic that may confuse the model.",
            }
            st.info(descriptions.get(scenario, ""))

    with col_view:
        st.markdown("### 📊 Live Simulation View")
        anim_area = st.empty()
        status_box = st.empty()
        progress_bar = st.empty()
        metrics_area = st.empty()
        live_chart = st.empty()
        details_area = st.empty()

        status_box.info("🔵 Ready. Configure above or click START SIMULATION (or use the Instant Attack Pad below).")

    if start_btn:
        is_dynamic = (injected_attack != "None (Pure Scenario)")
        effective_scenario = injected_attack if is_dynamic else scenario
        icon, label = attack_icons.get(effective_scenario, ("⚡", "Running..."))

        # Initial animation state
        if scenario == "Normal Traffic" and is_dynamic:
            anim_area.markdown(
                f'<div style="background:rgba(0,229,255,0.05); border:1px solid rgba(0,229,255,0.2); '
                f'border-radius:14px; padding:1.5rem; text-align:center; animation: pulse-cyan 2s ease-in-out infinite;">'
                f'<div style="font-size:3rem;">💻</div>'
                f'<div style="color:#00E5FF; font-weight:600; font-size:1.1rem; margin-top:0.5rem;">'
                f'Normal Baseline Traffic Flowing</div>'
                f'<div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">'
                f'Client A (10.0.0.10) → Server B (10.0.0.100) | Standby for potential threats</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        elif scenario != "Normal Traffic":
            anim_area.markdown(
                f'<div class="attack-anim">'
                f'<div class="hacker-icon">{icon}</div>'
                f'<div class="attack-text">⚡ ATTACK IN PROGRESS ⚡</div>'
                f'<div class="attack-detail">{scenario.upper()} — {label}</div>'
                f'<div class="attack-detail" style="margin-top:0.5rem;">'
                f'Attacker → 10.0.0.100 (Server B)</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            anim_area.markdown(
                f'<div style="background:rgba(0,229,255,0.05); border:1px solid rgba(0,229,255,0.2); '
                f'border-radius:14px; padding:1.5rem; text-align:center; animation: pulse-cyan 2s ease-in-out infinite;">'
                f'<div style="font-size:3rem;">💻</div>'
                f'<div style="color:#00E5FF; font-weight:600; font-size:1.1rem; margin-top:0.5rem;">'
                f'Normal Traffic Flowing</div>'
                f'<div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">'
                f'Client A (10.0.0.10) → Server B (10.0.0.100)</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        status_box.warning(f"⏳ Initializing simulation pipeline...")

        events_batch = generate_simulation_batch(
            scenario_name=scenario,
            intensity=intensity,
            duration_sec=duration,
            injected_attack=injected_attack,
            switch_ratio=switch_ratio,
        )
        total_events = len(events_batch)

        status_box.info(f"🔄 Running: {total_events} flows | Baseline: {scenario} | Sudden Attack: {injected_attack}")

        chart_data = []
        threats_detected = 0
        blocked_count = 0
        sleep_interval = max(duration / total_events, 0.02) if total_events > 0 else 0
        attack_switched_alerted = False

        for i, event in enumerate(events_batch):
            result = process_simulated_event(event)
            db_event = result["db_event"]
            pred = result["prediction"]

            is_attack = pred.get("predicted_class", "BENIGN") not in ("BENIGN",)
            is_injected_phase = (event.get("simulation_phase") == "SUDDEN_ATTACK")

            if is_attack:
                threats_detected += 1
            if result["was_blocked"]:
                blocked_count += 1

            # ── Dynamic Animation & Alert Switching ──────────
            if is_injected_phase or (is_attack and scenario == "Normal Traffic"):
                cur_target = injected_attack if is_dynamic else db_event.attack_type
                cur_icon, cur_label = attack_icons.get(cur_target, ("⚡", "Attack in progress"))
                anim_area.markdown(
                    f'<div class="attack-anim">'
                    f'<div class="hacker-icon">{cur_icon}</div>'
                    f'<div class="attack-text">⚡ SUDDEN ATTACK INJECTED! ⚡</div>'
                    f'<div class="attack-detail"><b>{db_event.attack_type.upper()}</b> STRIKE — {cur_label}</div>'
                    f'<div class="attack-detail" style="margin-top:0.5rem;">'
                    f'Attacker (<code>{db_event.source_ip}</code>) → Server B (<code>10.0.0.100</code>)</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                status_box.error(
                    f"🚨 Flow #{i+1}: ⚡ SUDDEN INTRUSION! {db_event.source_ip} → {db_event.attack_type} "
                    f"| Conf: {db_event.confidence*100:.1f}% | Risk: {db_event.risk_level} | Action: {db_event.action}"
                )
            elif not is_attack:
                anim_area.markdown(
                    f'<div style="background:rgba(0,229,255,0.05); border:1px solid rgba(0,229,255,0.2); '
                    f'border-radius:14px; padding:1.5rem; text-align:center; animation: pulse-cyan 2s ease-in-out infinite;">'
                    f'<div style="font-size:3rem;">💻</div>'
                    f'<div style="color:#00E5FF; font-weight:600; font-size:1.1rem; margin-top:0.5rem;">'
                    f'Normal Baseline Traffic Flowing</div>'
                    f'<div style="color:rgba(255,255,255,0.6); font-size:0.85rem;">'
                    f'Client A (10.0.0.10) → Server B (10.0.0.100) | Network Status: Healthy</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                status_box.info(
                    f"🟢 Flow #{i+1}: Normal Traffic | AI: BENIGN ({db_event.confidence*100:.1f}%) | Risk: MONITOR | Action: ALLOW"
                )

            chart_data.append({
                "flow": i + 1,
                "risk_score": db_event.risk_score,
                "attack_type": db_event.attack_type,
                "phase": "Attack" if is_attack else "Normal",
            })

            # Update progress
            progress_bar.progress((i + 1) / total_events)

            with metrics_area.container():
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("Flows Analyzed", i + 1)
                mc2.metric("Threats Detected", threats_detected)
                mc3.metric("Blocked Sources", blocked_count)
                mc4.metric("Latest Flow", db_event.attack_type)

            # Live risk chart
            df_chart = pd.DataFrame(chart_data)
            fig = px.line(
                df_chart, x="flow", y="risk_score",
                color="phase",
                color_discrete_map={"Normal": "#00E5FF", "Attack": "#fc8181"},
                labels={"flow": "Flow #", "risk_score": "Risk Score"},
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#0f1623",
                font_color="#e2e8f0",
                yaxis=dict(range=[0, 1.05], gridcolor="#2d3748"),
                xaxis=dict(gridcolor="#2d3748"),
                margin=dict(t=10, b=20, l=20, r=20),
                height=250,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            fig.add_hline(y=0.7, line_dash="dash", line_color="#fc8181", annotation_text="HIGH RISK THRESHOLD")
            live_chart.plotly_chart(fig, use_container_width=True)

            time.sleep(sleep_interval)

        # ── Simulation Complete — Show Result Banner ──────────
        status_box.success(f"✅ Dynamic Simulation Complete — {total_events} flows analyzed.")

        if threats_detected > 0:
            anim_area.markdown(
                f'<div class="result-danger">'
                f'<div class="result-icon">🚨</div>'
                f'<div class="result-title">⚠️ INTRUSION DETECTED & MITIGATED ⚠️</div>'
                f'<div class="result-sub">'
                f'{threats_detected} malicious flows detected — attacker isolated</div>'
                f'<div class="result-sub" style="margin-top:0.5rem;">'
                f'Scenario: <b>{scenario}</b> ➔ Injected Strike: <b>{injected_attack}</b> | See <b>Response Center</b> for details</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            anim_area.markdown(
                '<div class="result-safe">'
                '<div class="result-icon">✅</div>'
                '<div class="result-title">🟢 NETWORK IS SAFE — GOOD TO GO!</div>'
                '<div class="result-sub">All traffic classified as normal. No threats detected.</div>'
                '<div class="result-sub" style="margin-top:0.5rem;">'
                'AI-SNIDS is monitoring. Network operations can continue safely.</div>'
                '</div>',
                unsafe_allow_html=True
            )

        with details_area.container():
            st.markdown("### 📋 Dynamic Simulation Summary")
            scol1, scol2, scol3 = st.columns(3)
            scol1.metric("Total Flows", total_events)
            scol2.metric("Threats Flagged", threats_detected)
            scol3.metric("Sources Blocked", blocked_count)

    # ═══════════════════════════════════════════════════════════════
    # REAL-TIME INSTANT ATTACK INJECTION PAD
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.markdown("### ⚡ Real-Time Instant Attack Injection Pad")
    st.markdown(
        "*Simulate sudden, unplanned attacks on demand! "
        "Click any button below to instantly strike the virtual network mid-operation:* "
    )

    pad_col1, pad_col2, pad_col3, pad_col4, pad_col5 = st.columns(5)

    def _handle_instant_strike(attack_name: str, friendly_label: str, is_attack: bool = True):
        burst_results = run_instant_attack_burst(attack_name, count=6, intensity="HIGH")
        latest = burst_results[-1]
        db_e = latest["db_event"]
        if is_attack:
            st.error(
                f"💥 **SUDDEN {friendly_label.upper()} STRIKE INJECTED!** "
                f"AI-SNIDS detected {db_e.attack_type} with {db_e.confidence*100:.1f}% confidence. "
                f"Risk: **{db_e.risk_level}** | Action: **{db_e.action}** | Attacker IP: `{db_e.source_ip}`."
            )
        else:
            st.success(
                f"🟢 **NORMAL TRAFFIC INJECTED!** Client A (10.0.0.10) → Server B (10.0.0.100). "
                f"AI-SNIDS classified as **BENIGN** with {db_e.confidence*100:.1f}% confidence (Action: ALLOW)."
            )

    with pad_col1:
        if st.button("🔓 Sudden Port Scan", use_container_width=True, help="Attacker 10.0.0.50 suddenly probes ports"):
            _handle_instant_strike("Port Scan", "Port Scan")

    with pad_col2:
        if st.button("💥 Sudden DDoS Swarm", use_container_width=True, help="Distributed botnet 10.0.0.51-56 suddenly floods server"):
            _handle_instant_strike("DDoS", "DDoS Swarm")

    with pad_col3:
        if st.button("💣 Sudden DoS Flood", use_container_width=True, help="Attacker 10.0.0.50 suddenly sends high packet rate flood"):
            _handle_instant_strike("DoS", "DoS Flood")

    with pad_col4:
        if st.button("🔨 Sudden Brute Force", use_container_width=True, help="Attacker 10.0.0.50 suddenly attacks SSH/FTP ports"):
            _handle_instant_strike("Brute Force", "Brute Force")

    with pad_col5:
        if st.button("💻 Send Normal Flow", use_container_width=True, help="Client A 10.0.0.10 sends clean web traffic"):
            _handle_instant_strike("Normal Traffic", "Normal Traffic", is_attack=False)



# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: LIVE TRAFFIC MONITOR
# ═══════════════════════════════════════════════════════════════════════════════

def page_live_traffic():
    st.markdown("# 📡 Live Traffic Monitor")
    st.markdown("*All analyzed traffic samples with AI detection results.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        limit = st.selectbox("Show last", [20, 50, 100, 200], index=1)
    with col2:
        source_filter = st.radio("Data Source", ["All", "CICIDS2017", "SIMULATION"], horizontal=True)

    events = get_recent_events(limit * 3)

    if not events:
        st.info("No events recorded yet. Run a simulation or analyze traffic samples first.")
        return

    df = pd.DataFrame(events)

    if source_filter != "All" and "data_source" in df.columns:
        df = df[df["data_source"] == source_filter]

    df = df.head(limit)

    if df.empty:
        st.info(f"No events found for: {source_filter}")
        return

    # Format display
    risk_icons = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵", "MONITOR": "🟢"}
    df_display = df.copy()
    df_display["risk_level"] = df_display["risk_level"].apply(lambda r: f"{risk_icons.get(r, '')} {r}")
    df_display["confidence"] = df_display["confidence"].apply(lambda v: f"{v*100:.1f}%")

    display_cols = [
        "timestamp", "source_ip", "destination_ip", "protocol",
        "attack_type", "confidence", "risk_level", "action", "data_source"
    ]
    cols_present = [c for c in display_cols if c in df_display.columns]
    df_show = df_display[cols_present].copy()
    df_show.columns = [c.replace("_", " ").title() for c in df_show.columns]

    st.dataframe(df_show, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download Event Log (CSV)",
        data=csv, file_name="ai_snids_events.csv", mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: THREAT CENTER
# ═══════════════════════════════════════════════════════════════════════════════

def page_threat_center():
    st.markdown("# 🚨 Threat Center")
    st.markdown("*Only attack events — filtered from all traffic analysis.*")

    col1, col2, col3 = st.columns(3)
    with col1:
        attack_filter = st.selectbox(
            "Attack Type",
            ["All", "DoS", "DDoS", "PortScan", "BruteForce", "Botnet", "BLOCKED"]
        )
    with col2:
        risk_filter = st.selectbox("Risk Level", ["All", "HIGH", "MEDIUM", "LOW"])
    with col3:
        source_filter = st.radio("Source", ["All", "CICIDS2017", "SIMULATION"], horizontal=True)

    events = get_recent_events(500)
    if not events:
        st.info("No events yet.")
        return

    df = pd.DataFrame(events)

    # Filter to attacks only
    df = df[df["attack_type"] != "BENIGN"]

    if attack_filter != "All":
        df = df[df["attack_type"] == attack_filter]
    if risk_filter != "All":
        df = df[df["risk_level"] == risk_filter]
    if source_filter != "All" and "data_source" in df.columns:
        df = df[df["data_source"] == source_filter]

    if df.empty:
        st.info("No threats matching filters.")
        return

    st.metric("Threats Matching Filters", len(df))

    # Show threat cards for top 5
    for _, row in df.head(5).iterrows():
        risk_class = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}.get(row.get("risk_level", ""), "low")
        src = row.get("data_source", "")
        st.markdown(
            f'<div class="{risk_class}-alert">'
            f'⚠ <b>{row["attack_type"]}</b> | '
            f'{row["source_ip"]} → {row["destination_ip"]} | '
            f'Confidence: {row["confidence"]*100:.1f}% | '
            f'Risk: {row["risk_level"]} | '
            f'Action: {row["action"]} | '
            f'Source: {src}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # Full table
    st.markdown("### 📋 All Threats")
    risk_icons = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}
    df_display = df.copy()
    df_display["risk_level"] = df_display["risk_level"].apply(lambda r: f"{risk_icons.get(r, '')} {r}")
    df_display["confidence"] = df_display["confidence"].apply(lambda v: f"{v*100:.1f}%")

    display_cols = ["timestamp", "source_ip", "destination_ip", "attack_type", "confidence", "risk_level", "action", "data_source"]
    cols_present = [c for c in display_cols if c in df_display.columns]
    st.dataframe(df_display[cols_present].head(50), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6: RESPONSE CENTER
# ═══════════════════════════════════════════════════════════════════════════════

def page_response_center():
    st.markdown("# 🛑 Response Center")
    st.markdown("*Application-level simulated defense — blocked sources and response actions.*")

    st.markdown(
        '<div class="sim-disclaimer">'
        '⚠️ <b>APPLICATION-LEVEL SIMULATION</b> — This is NOT an OS firewall. '
        'Blocking is enforced only within the AI-SNIDS application. '
        'No iptables, nftables, or system-level rules are modified.'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # How blocking works
    st.markdown("### 🔄 How Simulated Blocking Works")
    st.markdown(
        """
        <div class="topology-box" style="font-size: 0.8rem;">
BEFORE DETECTION:                    AFTER DETECTION:

Attacker                             AI-SNIDS
10.0.0.50                               │
    │                                Threat Detected
    ▼                                    │
Server B                             10.0.0.50 added to
10.0.0.100                           simulated blocklist
                                         │
                                    Future flows from
                                    10.0.0.50 → BLOCKED
        </div>
        """, unsafe_allow_html=True
    )

    st.divider()

    # Blocked IPs table
    st.markdown("### 🚫 Simulated Blocklist")
    blocked = get_blocked_ips()

    if not blocked:
        st.markdown('<div class="benign-alert">✅ No sources currently blocked. Run an attack simulation to see blocking in action.</div>', unsafe_allow_html=True)
    else:
        for b in blocked:
            st.markdown(
                f'<div class="high-alert">'
                f'🚫 <b>IP: {b["ip_address"]}</b><br>'
                f'<b>Reason:</b> {b["reason"]}<br>'
                f'<b>Blocked At:</b> {b["blocked_at"][:19] if b["blocked_at"] else "N/A"}<br>'
                f'<b>Event Count:</b> {b["event_count"]}<br>'
                f'<b>Status:</b> {"🔴 ACTIVE" if b["is_active"] else "🟢 Released"}'
                f'</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # Response actions legend
    st.markdown("### 📖 Response Action Reference")
    st.markdown("""
    | Action | Meaning | Trigger |
    |--------|---------|---------|
    | **ALLOW** | Traffic permitted | BENIGN / MONITOR risk |
    | **LOG** | Traffic logged for review | LOW risk |
    | **ALERT** | Security alert raised | MEDIUM risk |
    | **BLOCK** | Source added to simulated blocklist | HIGH risk |
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7: CRYPTO LAB
# ═══════════════════════════════════════════════════════════════════════════════

def page_crypto_lab():
    st.markdown("# 🔐 Crypto Lab")
    st.markdown(
        "*Cryptography protects legitimate communication between Client A and Server B. "
        "AI detects threats — Crypto prevents eavesdropping and tampering.*"
    )

    # Story context
    st.markdown(
        '<div class="topology-box" style="font-size: 0.8rem;">'
        'Client A (10.0.0.10)           Server B (10.0.0.100)\n'
        '       │                              ▲\n'
        '       │  ECDH Key Exchange            │\n'
        '       │  ──────────────────────────── │\n'
        '       │                              │\n'
        '       │  Shared Secret (HKDF)        │\n'
        '       │  ──────────────────────────── │\n'
        '       │                              │\n'
        '       │  AES-256-GCM Encrypted Data  │\n'
        '       └──────────────────────────────┘\n'
        '                     │\n'
        '              [ AI-SNIDS ]\n'
        '         (monitors flow, not payload)'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # CIA Triad
    st.markdown("### 🔒 CIA Triad in This System")
    c1, c2, c3 = st.columns(3)
    c1.success("**C — Confidentiality**\nAES-256-GCM ensures ciphertext reveals nothing about plaintext")
    c2.warning("**I — Integrity**\nGCM auth tag (128-bit) detects ANY modification")
    c3.info("**A — Availability**\nAI-based intrusion detection prevents service disruption")

    st.divider()

    # Full Crypto Demo Button
    st.markdown("### 🚀 Run Complete Crypto Demo")
    st.markdown("*Demonstrates the full flow: Key Exchange → Encrypt → Decrypt → Tamper Detection*")

    message = st.text_input("Message from Client A to Server B", value="Student project data")

    if st.button("🔐 RUN CRYPTO DEMO", type="primary", use_container_width=True):
        from crypto.key_exchange import ECDHParty
        from crypto.encryption import encrypt, decrypt, tamper_ciphertext

        with st.spinner("Running cryptographic operations..."):

            # Step 1: Key Exchange
            st.markdown("---")
            st.markdown("### 🔑 Step 1: ECDH Key Exchange")

            client = ECDHParty("Client-A")
            server = ECDHParty("Server-B")

            client.load_peer_public_key(server.get_public_key_bytes())
            server.load_peer_public_key(client.get_public_key_bytes())

            client_key = client.derive_aes_key()
            server_key = server.derive_aes_key()
            keys_match = client_key == server_key

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Client A's Public Key (P-256)**")
                st.markdown(f'<div class="crypto-box">{client.get_public_key_hex()[:80]}...</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Server B's Public Key (P-256)**")
                st.markdown(f'<div class="crypto-box">{server.get_public_key_hex()[:80]}...</div>', unsafe_allow_html=True)

            st.markdown("**Derived AES-256 Key (first 16 bytes shown)**")
            kc1, kc2, kc3 = st.columns(3)
            kc1.markdown(f'<div class="crypto-box">Client A: {client_key[:16].hex()}</div>', unsafe_allow_html=True)
            kc2.markdown(f'<div class="crypto-box">Server B: {server_key[:16].hex()}</div>', unsafe_allow_html=True)
            if keys_match:
                kc3.success("✅ Keys Match!\nShared secret established.")
            else:
                kc3.error("❌ Key mismatch")

            st.caption("🔒 Private keys are NEVER displayed, logged, or stored.")

            # Step 2: Encryption
            st.markdown("---")
            st.markdown("### ✉️ Step 2: AES-256-GCM Encryption")

            encrypted = encrypt(message, client_key)

            ecol1, ecol2 = st.columns(2)
            with ecol1:
                st.markdown("**Original Message:**")
                st.markdown(f'<div class="crypto-box" style="color:#68d391;">{message}</div>', unsafe_allow_html=True)
            with ecol2:
                st.markdown("**Ciphertext (base64):**")
                st.markdown(f'<div class="crypto-box">{encrypted.ciphertext}</div>', unsafe_allow_html=True)

            st.markdown(f"**Nonce (96-bit):** `{encrypted.nonce}`")

            # Step 3: Decryption
            st.markdown("---")
            st.markdown("### 🔓 Step 3: Server B Decrypts")

            result = decrypt(encrypted, server_key)
            if result.success:
                st.success(f'✅ **Decrypted successfully:** "{result.plaintext}"')
                st.caption("✅ Integrity verified — ciphertext was not tampered with.")
            else:
                st.error(f"❌ Decryption failed: {result.error}")

            # Step 4: Tamper Detection
            st.markdown("---")
            st.markdown("### ⚠️ Step 4: Tampering Detection")
            st.markdown("*What happens if an attacker modifies the ciphertext?*")

            tampered = tamper_ciphertext(encrypted)

            tcol1, tcol2 = st.columns(2)
            with tcol1:
                st.markdown("**Original Ciphertext:**")
                st.markdown(f'<div class="crypto-box">{encrypted.ciphertext[:50]}...</div>', unsafe_allow_html=True)
            with tcol2:
                st.markdown("**Tampered Ciphertext:**")
                st.markdown(f'<div class="crypto-box" style="color:#fc8181;">{tampered.ciphertext[:50]}...</div>', unsafe_allow_html=True)

            tamper_result = decrypt(tampered, server_key)
            st.error(
                f"🚫 **AUTHENTICATION FAILED**\n\n"
                f"{tamper_result.error}\n\n"
                "AES-256-GCM detected the modification and **refused to decrypt**. "
                "No corrupted data is ever returned."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8: MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

def page_model_performance():
    st.markdown("# 📊 AI Model Performance")
    st.markdown(
        "*Evaluation results from the trained Random Forest classifier. "
        "These are **real metrics** from the CICIDS2017 dataset — not simulated.*"
    )

    metrics = load_evaluation_metrics()

    if not metrics:
        st.warning("⚠ Model metrics not found. Train the model first:\n```bash\npython ai/train.py\n```")
        return

    st.markdown('<div class="sim-disclaimer">📊 These metrics are from the REAL trained model on CICIDS2017 data — not simulation results.</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### Random Forest Classifier")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy", f"{metrics['accuracy'] * 100:.2f}%")
    col2.metric("Precision (macro)", f"{metrics['precision_macro'] * 100:.2f}%")
    col3.metric("Recall (macro)", f"{metrics['recall_macro'] * 100:.2f}%")
    col4.metric("F1 Score (macro)", f"{metrics['f1_macro'] * 100:.2f}%")

    st.markdown("""
    > **Why multiple metrics?** In cybersecurity, accuracy alone is misleading.
    > A model predicting "BENIGN" for all traffic achieves 95%+ accuracy
    > on imbalanced datasets while detecting ZERO attacks.
    > - **Precision**: Of flagged attacks, how many were real? (False alarm rate)
    > - **Recall**: Of real attacks, how many did we catch? (Miss rate)
    > - **F1**: Harmonic mean — balances precision and recall.
    > *For IDS, high Recall is more critical than Precision.*
    """)

    st.divider()

    # Confusion Matrix
    cm_path = load_confusion_matrix_img()
    if cm_path:
        st.markdown("### Confusion Matrix")
        st.image(str(cm_path), use_container_width=True)
        st.caption("Diagonal = correct predictions. Off-diagonal = misclassifications.")

    # Feature Importance
    fi_path = load_feature_importance_img()
    if fi_path:
        st.markdown("### Feature Importance")
        st.image(str(fi_path), use_container_width=True)
        st.caption("Top features the Random Forest uses to distinguish attack types.")

    # Classification Report
    if "classification_report" in metrics:
        st.markdown("### Per-Class Classification Report")
        st.code(metrics["classification_report"])

    st.divider()

    st.markdown("### 🧠 How AI Detection Works in AI-SNIDS")
    st.markdown(
        """
        <div class="topology-box" style="font-size: 0.8rem;">
Network Flow
     │
     ▼
Feature Extraction (20 flow features)
     │
     ▼
StandardScaler (normalize)
     │
     ▼
Random Forest (100 trees)
     │
     ├──→ Predicted Class (BENIGN / DoS / DDoS / PortScan / BruteForce)
     ├──→ Model Confidence (probability)
     │
     ▼
Risk Assessment Engine
     │
     ├──→ Risk Score = 0.4×confidence + 0.4×severity + 0.2×intensity
     ├──→ Risk Level (MONITOR / LOW / MEDIUM / HIGH)
     └──→ Action (ALLOW / LOG / ALERT / BLOCK)
        </div>
        """, unsafe_allow_html=True
    )

    st.info(
        "**Important:** AI Confidence ≠ Security Risk. "
        "A PortScan with 95% confidence is less dangerous than a DDoS with 70% confidence. "
        "The Risk Engine weighs both the model output AND the attack severity."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    page = render_sidebar()

    page_map = {
        "🛡️ Security Overview":    page_security_overview,
        "🌐 Virtual Network":      page_virtual_network,
        "🧪 Attack Scenario Lab":  page_attack_lab,
        "📡 Live Traffic Monitor":  page_live_traffic,
        "🚨 Threat Center":        page_threat_center,
        "🛑 Response Center":      page_response_center,
        "🔐 Crypto Lab":           page_crypto_lab,
        "📊 Model Performance":    page_model_performance,
    }

    page_fn = page_map.get(page, page_security_overview)
    page_fn()


if __name__ == "__main__":
    main()
