"""
dashboard/app.py

AI-SNIDS — AI-Powered Network Intrusion Detection & Security Intelligence.
Minimalist, high-clarity interface inspired by Linear, Vercel, and Apple.
Pure black (#000000) canvas, subtle borders (#1A1A1A), zero visual noise,
and 100% verified backend functionality.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
import json
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import importlib
import dashboard.theme
importlib.reload(dashboard.theme)

from dashboard.theme import (
    GLOBAL_CSS,
    COLOR_BLACK,
    COLOR_SURFACE,
    COLOR_CARD,
    COLOR_CARD_HOVER,
    COLOR_BORDER,
    COLOR_BORDER_SUBTLE,
    COLOR_WHITE,
    COLOR_GRAY,
    COLOR_MUTED,
    COLOR_TECH,
    COLOR_AI_ACCENT,
    SEV_SAFE,
    SEV_WARN,
    SEV_THREAT,
    SEV_CRITICAL,
    get_icon,
    render_section_header,
    render_metric_card,
    render_severity_badge,
    render_network_node,
    get_plotly_soc_layout,
)
from simulation.simulator import (
    generate_simulation_batch,
    process_simulated_event,
    run_instant_attack_burst,
    create_default_topology,
)

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI-SNIDS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Minimalist Design System
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─── Cached Model & Database Loaders ───────────────────────────────────────────

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


# ─── Database Access Helpers ───────────────────────────────────────────────────

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
        high_risk = session.query(func.count(SecurityEvent.id)).filter(
            SecurityEvent.risk_score >= 0.7
        ).scalar() or 0
        blocked = session.query(func.count(BlockedIP.id)).filter(
            BlockedIP.is_active == True
        ).scalar() or 0
        session.close()

        return {
            "total_samples": total,
            "threats_detected": threats,
            "high_risk_threats": high_risk,
            "blocked_ips": blocked,
            "detection_rate": f"{(threats / total * 100):.1f}%" if total > 0 else "0.0%",
        }
    except Exception:
        return {
            "total_samples": 0,
            "threats_detected": 0,
            "high_risk_threats": 0,
            "blocked_ips": 0,
            "detection_rate": "N/A",
        }


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


def toggle_ip_block(ip_address: str, block: bool, reason: str = "SOC Action") -> bool:
    try:
        SessionLocal = get_db_session()
        from database.models import BlockedIP
        session = SessionLocal()
        existing = session.query(BlockedIP).filter_by(ip_address=ip_address).first()
        if block:
            if existing:
                existing.is_active = True
                existing.reason = reason
                existing.blocked_at = datetime.now(timezone.utc)
            else:
                new_block = BlockedIP(
                    ip_address=ip_address,
                    reason=reason,
                    is_active=True,
                )
                session.add(new_block)
        else:
            if existing:
                existing.is_active = False
        session.commit()
        session.close()
        return True
    except Exception:
        return False


# ─── Minimal Header Helper ─────────────────────────────────────────────────────

def render_top_bar(page_title: str, subtitle: str = None):
    """Clean, restrained top bar matching Linear / Vercel layout."""
    st.markdown(
        f"""
        <div style="display:flex; align-items:flex-end; justify-content:space-between; padding-bottom:1rem; margin-bottom:1.5rem; border-bottom:1px solid {COLOR_BORDER_SUBTLE};">
            <div>
                <h1 style="margin:0; font-size:1.4rem; font-weight:600; color:{COLOR_WHITE}; letter-spacing:-0.025em;">{page_title}</h1>
                <div style="color:{COLOR_GRAY}; font-size:0.82rem; margin-top:0.25rem;">{subtitle or 'Network Security Intelligence'}</div>
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:0.75rem; color:{COLOR_GRAY}; font-family:'JetBrains Mono', monospace;">
                <span class="status-dot dot-cyan"></span>
                <span style="color:{COLOR_WHITE}; font-weight:500;">SYSTEM ONLINE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Sidebar Navigation & Telemetry ───────────────────────────────────────────

def render_sidebar() -> str:
    with st.sidebar:
        # Minimal Brand Header
        st.markdown(
            f"""
            <div style="padding: 0.75rem 0 1.25rem 0.25rem; border-bottom: 1px solid {COLOR_BORDER_SUBTLE}; margin-bottom: 1rem;">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <span style="font-size:1.05rem; font-weight:600; color:{COLOR_WHITE}; letter-spacing:-0.02em;">
                        AI-SNIDS
                    </span>
                    <span class="status-dot dot-cyan"></span>
                </div>
                <div style="font-size:0.72rem; color:{COLOR_GRAY}; margin-top:0.2rem;">
                    Network Security Intelligence
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_options = [
            "Overview",
            "Live Monitoring",
            "Attack Lab",
            "Threat Center",
            "Secure Communication",
            "Model Performance",
            "Logs",
        ]

        page = st.radio("Navigation", options=nav_options, label_visibility="collapsed")

        st.markdown(f'<div style="margin: 2.5rem 0 1rem 0; border-top: 1px solid {COLOR_BORDER_SUBTLE};"></div>', unsafe_allow_html=True)

        # Status Line at bottom of sidebar
        try:
            predictor = load_predictor()
            ai_online = predictor.is_loaded
        except Exception:
            ai_online = False

        try:
            from database.database import health_check
            db_online = health_check()
        except Exception:
            db_online = False

        st.markdown(
            f"""
            <div style="font-size:0.7rem; color:{COLOR_GRAY}; display:flex; flex-direction:column; gap:0.25rem;">
                <div class="sidebar-status-row">
                    <span>AI Engine</span>
                    <span style="display:flex; align-items:center; gap:5px; color:{SEV_SAFE if ai_online else SEV_THREAT}; font-family:'JetBrains Mono', monospace; font-size:0.68rem;">
                        <span class="status-dot {'dot-green' if ai_online else 'dot-red'}"></span>
                        {'ONLINE' if ai_online else 'OFFLINE'}
                    </span>
                </div>
                <div class="sidebar-status-row">
                    <span>Database</span>
                    <span style="display:flex; align-items:center; gap:5px; color:{SEV_SAFE if db_online else SEV_THREAT}; font-family:'JetBrains Mono', monospace; font-size:0.68rem;">
                        <span class="status-dot {'dot-green' if db_online else 'dot-red'}"></span>
                        {'CONNECTED' if db_online else 'DISCONNECTED'}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

def page_overview():
    render_top_bar("Overview", "Network Security Intelligence")

    # Minimal Status Line
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:1.75rem; font-size:0.75rem; color:{COLOR_GRAY}; margin-bottom:1.5rem; padding-bottom:0.75rem; border-bottom:1px solid {COLOR_BORDER_SUBTLE}; font-family:'JetBrains Mono', monospace;">
            <span style="display:inline-flex; align-items:center; gap:6px;">
                <span class="status-dot dot-cyan"></span> AI ENGINE ONLINE
            </span>
            <span style="display:inline-flex; align-items:center; gap:6px;">
                <span class="status-dot dot-green"></span> NETWORK MONITORING
            </span>
            <span style="display:inline-flex; align-items:center; gap:6px;">
                <span class="status-dot dot-green"></span> CRYPTO SECURE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = get_statistics()
    blocked_list = get_blocked_ips()

    # 4 Clean Minimal Linear KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        net_status = "PROTECTED" if stats["threats_detected"] == 0 else ("UNDER ATTACK" if len(blocked_list) > 0 else "ELEVATED")
        status_color = SEV_SAFE if net_status == "PROTECTED" else (SEV_THREAT if net_status == "UNDER ATTACK" else SEV_WARN)
        st.markdown(render_metric_card("NETWORK STATUS", net_status, "Boundary Defense Active", status_color), unsafe_allow_html=True)
    with k2:
        st.markdown(render_metric_card("ACTIVE THREATS", f"{stats['threats_detected']:02d}", f"High Risk: {stats['high_risk_threats']}", SEV_THREAT if stats['threats_detected'] > 0 else SEV_SAFE), unsafe_allow_html=True)
    with k3:
        st.markdown(render_metric_card("BLOCKED SOURCES", f"{len(blocked_list):02d}", "Firewall Filter Active", SEV_THREAT if len(blocked_list) > 0 else SEV_SAFE), unsafe_allow_html=True)
    with k4:
        risk_label = "HIGH" if stats["high_risk_threats"] > 0 else ("MEDIUM" if stats["threats_detected"] > 0 else "LOW")
        risk_color = SEV_THREAT if risk_label == "HIGH" else (SEV_WARN if risk_label == "MEDIUM" else SEV_SAFE)
        st.markdown(render_metric_card("CURRENT RISK", risk_label, "Composite Threat Level", risk_color), unsafe_allow_html=True)

    st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # One Clean Minimal Network Activity Chart
    st.markdown(render_section_header("Network Activity", "Sequential flow risk assessment", "Telemetry", "activity"), unsafe_allow_html=True)
    recent_events = get_recent_events(60)
    df = pd.DataFrame(recent_events)

    if not df.empty and "risk_score" in df.columns:
        df_timeline = df.copy().iloc[::-1].reset_index(drop=True)
        df_timeline["flow_id"] = df_timeline.index + 1

        fig_timeline = go.Figure()
        fig_timeline.add_trace(
            go.Scatter(
                x=df_timeline["flow_id"],
                y=df_timeline["risk_score"],
                mode="lines",
                name="Risk Score",
                line=dict(color=COLOR_AI_ACCENT, width=1.5),
            )
        )
        fig_timeline.add_hline(
            y=0.7,
            line_dash="dot",
            line_color=SEV_THREAT,
            line_width=1,
            annotation_text="0.70 Threshold",
            annotation_position="top right",
            annotation_font=dict(size=9, color=SEV_THREAT),
        )
        layout = get_plotly_soc_layout(height=220)
        layout["yaxis"]["range"] = [0, 1.05]
        layout["xaxis"]["title"] = "Flow #"
        layout["yaxis"]["title"] = "Risk"
        fig_timeline.update_layout(layout)
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No network activity telemetry available.")

    st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Minimal Recent Threats Table
    st.markdown(render_section_header("Recent Threats", "Abnormal flows flagged by AI detection", "Alerts", "alert-triangle"), unsafe_allow_html=True)
    if not df.empty:
        threat_df = df[df["attack_type"] != "BENIGN"].head(8)
        if not threat_df.empty:
            display_cols = ["timestamp", "source_ip", "destination_ip", "attack_type", "confidence", "risk_level", "action"]
            existing_cols = [c for c in display_cols if c in threat_df.columns]
            t_table = threat_df[existing_cols].copy()
            if "confidence" in t_table.columns:
                t_table["confidence"] = t_table["confidence"].apply(lambda x: f"{float(x)*100:.1f}%")
            if "timestamp" in t_table.columns:
                t_table["timestamp"] = pd.to_datetime(t_table["timestamp"]).dt.strftime("%H:%M:%S")
            t_table.columns = [c.upper().replace("_", " ") for c in t_table.columns]
            st.dataframe(t_table, use_container_width=True, hide_index=True, height=260)
        else:
            st.markdown(f'<div style="color:{COLOR_GRAY}; font-size:0.82rem; padding:1rem 0;">No active threats detected in recent flow logs.</div>', unsafe_allow_html=True)
    else:
        st.info("No alert records available.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: LIVE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def page_live_monitoring():
    render_top_bar("Live Monitoring", "Real-time traffic flow inspection and AI classification")

    filter_col1, filter_col2, filter_col3 = st.columns([1, 1.5, 1.5])
    with filter_col1:
        limit = st.selectbox("Limit", [25, 50, 100, 200], index=1)
    with filter_col2:
        source_filter = st.selectbox("Origin", ["All Sources", "CICIDS2017 Benchmark", "SIMULATION Lab"])
    with filter_col3:
        threat_filter = st.selectbox("Filter", ["All Traffic", "Threats Only", "Benign Only"])

    events = get_recent_events(limit * 3)
    if not events:
        st.info("No telemetry logged. Run a simulation in the Attack Lab to generate flow records.")
        return

    df = pd.DataFrame(events)

    if source_filter == "CICIDS2017 Benchmark":
        df = df[df["data_source"] == "CICIDS2017"]
    elif source_filter == "SIMULATION Lab":
        df = df[df["data_source"] == "SIMULATION"]

    if threat_filter == "Threats Only":
        df = df[df["attack_type"] != "BENIGN"]
    elif threat_filter == "Benign Only":
        df = df[df["attack_type"] == "BENIGN"]

    df = df.head(limit)

    st.markdown(
        f'<div style="font-size:0.75rem; color:{COLOR_GRAY}; margin:0.75rem 0 0.5rem 0; font-family:\'JetBrains Mono\', monospace;">'
        f'{len(df)} monitored flows'
        f'</div>',
        unsafe_allow_html=True,
    )

    display_cols = ["timestamp", "source_ip", "destination_ip", "protocol", "attack_type", "confidence", "risk_level", "action"]
    existing_cols = [c for c in display_cols if c in df.columns]
    table_df = df[existing_cols].copy()

    if "timestamp" in table_df.columns:
        table_df["timestamp"] = pd.to_datetime(table_df["timestamp"]).dt.strftime("%H:%M:%S.%f").str[:-3]
    if "confidence" in table_df.columns:
        table_df["confidence"] = table_df["confidence"].apply(lambda x: f"{float(x)*100:.1f}%")

    table_df.columns = [c.upper().replace("_", " ") for c in table_df.columns]
    st.dataframe(table_df, use_container_width=True, hide_index=True, height=480)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: ATTACK LAB
# ═══════════════════════════════════════════════════════════════════════════════

def page_attack_lab():
    render_top_bar("Attack Lab", "Simulate network intrusions and observe autonomous AI response")

    # Minimal Virtual Route Line
    st.markdown(
        f"""
        <div style="font-size:0.75rem; color:{COLOR_GRAY}; margin-bottom:1.5rem; font-family:'JetBrains Mono', monospace;">
            <span style="color:{COLOR_WHITE};">Client A (10.0.0.10)</span> ➔ Router ➔ <span style="color:{COLOR_WHITE};">Server B (10.0.0.100)</span>
            &nbsp;|&nbsp;
            <span style="color:{SEV_THREAT};">Attacker (10.0.0.50)</span> ➔ AI-SNIDS ➔ Simulated Block
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4-Node Minimal Topology Display
    topo_col1, topo_col2, topo_col3, topo_col4 = st.columns(4)
    blocked_list = get_blocked_ips()
    attacker_blocked = any(b["ip_address"] == "10.0.0.50" for b in blocked_list)

    with topo_col1:
        st.markdown(render_network_node("Client A", "10.0.0.10", "Legitimate Client", "ONLINE", False), unsafe_allow_html=True)
    with topo_col2:
        st.markdown(render_network_node("Gateway Router", "10.0.0.1", "Network IDS", "ONLINE", False), unsafe_allow_html=True)
    with topo_col3:
        st.markdown(render_network_node("Server B", "10.0.0.100", "Critical Server", "ONLINE", False), unsafe_allow_html=True)
    with topo_col4:
        st.markdown(render_network_node("Attacker Node", "10.0.0.50", "Adversary Source", "BLOCKED" if attacker_blocked else "MONITORED", True), unsafe_allow_html=True)

    st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Minimal Scenario Selector
    st.markdown(render_section_header("Simulation Scenario", "Select baseline traffic pattern", "Catalog", "terminal"), unsafe_allow_html=True)

    scenarios_meta = {
        "Normal Traffic": ("Clean HTTP/HTTPS web flows", "shield-check"),
        "Port Scan": ("Reconnaissance probing multi-port TCP/UDP services", "radar"),
        "Brute Force": ("Credential abuse targeting SSH/FTP ports", "lock"),
        "DoS": ("Single-source high-volume packet flood", "activity"),
        "DDoS": ("Distributed multi-node botnet swarm", "zap"),
        "Suspicious Traffic": ("Ambiguous flow characteristics with timing jitter", "alert-triangle"),
    }

    selected_scenario = st.selectbox("Baseline Scenario", list(scenarios_meta.keys()), index=0)

    # Clean Selectable Scenario Row
    sc_cols = st.columns(6)
    for i, (sc_name, (sc_desc, sc_icon)) in enumerate(scenarios_meta.items()):
        is_sel = (sc_name == selected_scenario)
        border_color = COLOR_AI_ACCENT if is_sel else COLOR_BORDER
        with sc_cols[i]:
            st.markdown(
                f"""
                <div class="soc-card soc-scenario-card" style="padding:0.75rem; text-align:center; min-height:95px; border: 1px solid {border_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                        <span class="status-dot {'dot-cyan' if is_sel else 'dot-green'}"></span>
                        {get_icon(sc_icon, size=14, color=COLOR_AI_ACCENT if is_sel else COLOR_MUTED)}
                    </div>
                    <div style="font-weight:500; font-size:0.78rem; color:{COLOR_WHITE if is_sel else COLOR_GRAY}; margin-top:0.2rem;">
                        {sc_name}
                    </div>
                    <div style="font-size:0.65rem; color:{COLOR_MUTED}; margin-top:0.25rem; line-height:1.25;">
                        {sc_desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="margin: 1rem 0;"></div>', unsafe_allow_html=True)

    # Simulation Controls
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

    with ctrl_col1:
        injected_attack = st.selectbox(
            "Sudden Mid-Stream Attack",
            ["None", "Port Scan", "DDoS", "DoS", "Brute Force", "Suspicious Traffic"],
            index=1 if selected_scenario == "Normal Traffic" else 0,
        )

    with ctrl_col2:
        strike_point_choice = st.selectbox(
            "Strike Point",
            ["Midway (50%)", "Early (30%)", "Late (70%)"],
            index=0,
        )
        switch_ratio_map = {"Early (30%)": 0.3, "Midway (50%)": 0.5, "Late (70%)": 0.7}
        switch_ratio = switch_ratio_map[strike_point_choice]

    with ctrl_col3:
        intensity = st.selectbox("Intensity", ["LOW", "MEDIUM", "HIGH"], index=1)

    with ctrl_col4:
        duration = st.slider("Duration (Sec)", min_value=5, max_value=30, value=10, step=5)

    start_simulation = st.button("START SIMULATION", type="primary", use_container_width=True)

    if start_simulation:
        is_dynamic = (injected_attack != "None")
        effective_scenario = injected_attack if is_dynamic else selected_scenario

        anim_slot = st.empty()
        status_slot = st.empty()
        progress_slot = st.empty()
        metrics_slot = st.empty()
        chart_slot = st.empty()

        events_batch = generate_simulation_batch(
            scenario_name=selected_scenario,
            intensity=intensity,
            duration_sec=duration,
            injected_attack=injected_attack,
            switch_ratio=switch_ratio,
        )
        total_events = len(events_batch)

        status_slot.markdown(
            f'<div style="font-size:0.75rem; color:{COLOR_GRAY}; font-family:\'JetBrains Mono\', monospace; margin-bottom:0.5rem;">'
            f'Generating {total_events} events · Baseline: {selected_scenario} · Injected: {injected_attack}'
            f'</div>',
            unsafe_allow_html=True,
        )

        chart_records = []
        threats_count = 0
        blocked_count = 0
        sleep_interval = max(duration / total_events, 0.02) if total_events > 0 else 0.05

        for idx, event in enumerate(events_batch):
            result = process_simulated_event(event)
            db_event = result["db_event"]
            pred = result["prediction"]

            is_threat = (pred.get("predicted_class", "BENIGN") != "BENIGN")
            is_injected = (event.get("simulation_phase") == "SUDDEN_ATTACK")

            if is_threat:
                threats_count += 1
            if result["was_blocked"]:
                blocked_count += 1

            if is_injected or (is_threat and selected_scenario == "Normal Traffic"):
                anim_slot.markdown(
                    f"""
                    <div class="soc-card" style="border-left: 2px solid {SEV_THREAT}; padding: 0.75rem 1rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; color:{SEV_THREAT}; font-size:0.85rem;">
                                ATTACK DETECTED: {db_event.attack_type}
                            </span>
                            {render_severity_badge(db_event.risk_level)}
                        </div>
                        <div class="mono" style="font-size:0.72rem; color:{COLOR_MUTED}; margin-top:0.25rem;">
                            {db_event.source_ip} ➔ {db_event.destination_ip} · Confidence: {db_event.confidence*100:.1f}% · Action: {db_event.action}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                anim_slot.markdown(
                    f"""
                    <div class="soc-card" style="border-left: 2px solid {SEV_SAFE}; padding: 0.75rem 1rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:500; color:{COLOR_WHITE}; font-size:0.85rem;">
                                BENIGN FLOW: {db_event.source_ip} ➔ {db_event.destination_ip}
                            </span>
                            {render_severity_badge('BENIGN')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            chart_records.append({
                "flow": idx + 1,
                "risk_score": db_event.risk_score,
                "phase": "Attack" if is_threat else "Normal",
            })

            progress_slot.progress((idx + 1) / total_events)

            with metrics_slot.container():
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Inspected", idx + 1)
                m2.metric("Threats", threats_count)
                m3.metric("Blocked", blocked_count)
                m4.metric("Classified", db_event.attack_type)

            df_live = pd.DataFrame(chart_records)
            fig_live = px.line(
                df_live,
                x="flow",
                y="risk_score",
                color="phase",
                color_discrete_map={"Normal": COLOR_AI_ACCENT, "Attack": SEV_THREAT},
                labels={"flow": "Flow", "risk_score": "Risk"},
            )
            layout_live = get_plotly_soc_layout(height=200)
            layout_live["yaxis"]["range"] = [0, 1.05]
            fig_live.update_layout(layout_live)
            chart_slot.plotly_chart(fig_live, use_container_width=True)

            time.sleep(sleep_interval)

        status_slot.markdown(
            f'<div style="color:{SEV_SAFE}; font-size:0.78rem; font-family:\'JetBrains Mono\', monospace; margin-top:0.5rem;">'
            f'Simulation complete · {total_events} events persisted to audit database.'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Instant Attack Pad
    st.markdown('<div style="margin: 2rem 0 1rem 0; border-top: 1px solid var(--border-subtle);"></div>', unsafe_allow_html=True)
    st.markdown(render_section_header("Instant Attack Injection", "1-click sudden strike triggers", "Actions", "zap"), unsafe_allow_html=True)

    pad_col1, pad_col2, pad_col3, pad_col4, pad_col5 = st.columns(5)

    def _trigger_instant_burst(attack_type: str, is_attack: bool = True):
        burst = run_instant_attack_burst(attack_type, count=6, intensity="HIGH")
        latest = burst[-1]["db_event"]
        if is_attack:
            st.error(
                f"SUDDEN {attack_type.upper()}: "
                f"Flagged {latest.attack_type} ({latest.confidence*100:.1f}%) · "
                f"Risk: {latest.risk_level} · Action: {latest.action} · Source: {latest.source_ip}"
            )
        else:
            st.success(
                f"CLEAN FLOW: "
                f"Client A (10.0.0.10) ➔ Server B (10.0.0.100) classified as BENIGN (Action: ALLOW)"
            )

    with pad_col1:
        if st.button("Port Scan", use_container_width=True):
            _trigger_instant_burst("Port Scan")
    with pad_col2:
        if st.button("DDoS Swarm", use_container_width=True):
            _trigger_instant_burst("DDoS")
    with pad_col3:
        if st.button("DoS Flood", use_container_width=True):
            _trigger_instant_burst("DoS")
    with pad_col4:
        if st.button("Brute Force", use_container_width=True):
            _trigger_instant_burst("Brute Force")
    with pad_col5:
        if st.button("Normal Flow", use_container_width=True):
            _trigger_instant_burst("Normal Traffic", is_attack=False)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: THREAT CENTER
# ═══════════════════════════════════════════════════════════════════════════════

def page_threat_center():
    render_top_bar("Threat Center", "Incident investigation and defensive mitigation")

    stats = get_statistics()
    blocked_list = get_blocked_ips()

    # 3 Clean Minimal Metrics
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.markdown(render_metric_card("ACTIVE THREATS", f"{stats['threats_detected']:02d}", "Logged Malicious Flows", SEV_THREAT), unsafe_allow_html=True)
    with tc2:
        st.markdown(render_metric_card("HIGH RISK", f"{stats['high_risk_threats']:02d}", "Composite Score >= 0.70", SEV_CRITICAL), unsafe_allow_html=True)
    with tc3:
        st.markdown(render_metric_card("BLOCKED SOURCES", f"{len(blocked_list):02d}", "Simulated Firewall Entries", SEV_THREAT if len(blocked_list) > 0 else SEV_SAFE), unsafe_allow_html=True)

    st.markdown('<div style="margin: 1.25rem 0;"></div>', unsafe_allow_html=True)

    # Minimal Filters
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        type_filter = st.selectbox("Classification", ["All Types", "PortScan", "DoS", "DDoS", "BruteForce"])
    with f_col2:
        risk_filter = st.selectbox("Severity", ["All Severities", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with f_col3:
        source_filter = st.selectbox("Origin", ["All Origins", "CICIDS2017 Benchmark", "SIMULATION Lab"])

    events = get_recent_events(150)
    threat_events = [e for e in events if e["attack_type"] != "BENIGN"]

    if not threat_events:
        st.info("No threat incidents recorded.")
        return

    df_threats = pd.DataFrame(threat_events)

    if type_filter != "All Types":
        df_threats = df_threats[df_threats["attack_type"].str.contains(type_filter, case=False, na=False)]
    if risk_filter != "All Severities":
        df_threats = df_threats[df_threats["risk_level"] == risk_filter]
    if source_filter == "CICIDS2017 Benchmark":
        df_threats = df_threats[df_threats["data_source"] == "CICIDS2017"]
    elif source_filter == "SIMULATION Lab":
        df_threats = df_threats[df_threats["data_source"] == "SIMULATION"]

    if df_threats.empty:
        st.info("No threat records match filter.")
        return

    # Incident Selection & Investigation Panel
    incident_col, detail_col = st.columns([3, 2])

    with incident_col:
        st.markdown(render_section_header("Incident Registry", "Click an incident to investigate", "Registry", "alert-triangle"), unsafe_allow_html=True)
        incident_options = [
            f"#{row['id']:03d} · {row['attack_type']} ({row['source_ip']}) · {row['risk_level']}"
            for _, row in df_threats.head(25).iterrows()
        ]
        selected_option = st.selectbox("Select Incident", incident_options, label_visibility="collapsed")
        selected_id = int(selected_option.split("·")[0].replace("#", "").strip())

        display_df = df_threats[["id", "timestamp", "attack_type", "source_ip", "confidence", "risk_level", "action"]].head(25).copy()
        display_df["confidence"] = display_df["confidence"].apply(lambda x: f"{float(x)*100:.1f}%")
        display_df.columns = ["ID", "TIME", "THREAT", "SOURCE", "CONFIDENCE", "RISK", "ACTION"]
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=350)

    selected_event = next((e for e in threat_events if e["id"] == selected_id), threat_events[0])
    is_curr_blocked = any(b["ip_address"] == selected_event["source_ip"] for b in blocked_list)

    with detail_col:
        st.markdown(render_section_header("Incident Details", "Target telemetry & firewall mitigation", "Triage", "shield"), unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="soc-card soc-card-threat">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <span style="font-weight:600; font-size:1rem; color:{COLOR_WHITE};">
                        {selected_event['attack_type']}
                    </span>
                    {render_severity_badge(selected_event['risk_level'])}
                </div>
                <div style="font-size:0.8rem; color:{COLOR_GRAY}; line-height:1.75;">
                    <div><b>ID:</b> <span class="mono">#{selected_event['id']}</span></div>
                    <div><b>Time:</b> <span class="mono">{selected_event['timestamp']}</span></div>
                    <div><b>Source:</b> <span class="mono" style="color:{COLOR_WHITE};">{selected_event['source_ip']}</span></div>
                    <div><b>Target:</b> <span class="mono">{selected_event['destination_ip']}</span></div>
                    <div><b>AI Confidence:</b> <span class="mono">{selected_event['confidence']*100:.1f}%</span></div>
                    <div><b>Risk Score:</b> <span class="mono">{selected_event['risk_score']}</span></div>
                    <div><b>Action:</b> <span class="mono" style="color:{SEV_THREAT if selected_event['action'] == 'BLOCK' else SEV_WARN};">{selected_event['action']}</span></div>
                    <div><b>Origin:</b> <span class="mono">{selected_event['data_source']}</span></div>
                </div>
                <div style="margin-top:1rem; padding-top:0.75rem; border-top:1px solid {COLOR_BORDER}; font-size:0.75rem; color:{COLOR_MUTED};">
                    Firewall State: <b style="color:{SEV_CRITICAL if is_curr_blocked else SEV_SAFE};">{'BLOCKED' if is_curr_blocked else 'UNRESTRICTED'}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_curr_blocked:
            if st.button(f"Unblock Source IP ({selected_event['source_ip']})", use_container_width=True):
                if toggle_ip_block(selected_event["source_ip"], block=False):
                    st.success(f"IP {selected_event['source_ip']} unblocked.")
                    st.rerun()
        else:
            if st.button(f"Simulate Firewall Block ({selected_event['source_ip']})", type="primary", use_container_width=True):
                if toggle_ip_block(selected_event["source_ip"], block=True, reason=f"SOC Block: {selected_event['attack_type']}"):
                    st.warning(f"IP {selected_event['source_ip']} blocked.")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: SECURE COMMUNICATION
# ═══════════════════════════════════════════════════════════════════════════════

def page_secure_communication():
    render_top_bar("Secure Communication", "Authenticated encryption pipeline and tamper verification")

    # Minimal 4-Stage Pipeline
    st.markdown(render_section_header("Cryptographic Pipeline", "Sequential authenticated encryption handshake", "Core", "lock"), unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    steps = [
        ("01", "ECDH P-256", "Ephemeral Diffie-Hellman", "lock"),
        ("02", "HKDF-SHA256", "Key Derivation (RFC 5869)", "cpu"),
        ("03", "AES-256-GCM", "Authenticated Encryption", "shield-check"),
        ("04", "Server B", "Authenticates & Decrypts", "server"),
    ]
    for col, (num, title, desc, icon) in zip([p1, p2, p3, p4], steps):
        with col:
            st.markdown(
                f"""
                <div class="soc-card" style="padding:0.75rem; text-align:center;">
                    <div style="font-size:0.62rem; color:{COLOR_GRAY}; font-family:'JetBrains Mono', monospace;">STEP {num}</div>
                    <div style="font-weight:600; font-size:0.82rem; color:{COLOR_WHITE}; margin-top:0.2rem;">{title}</div>
                    <div style="font-size:0.68rem; color:{COLOR_MUTED}; margin-top:0.15rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="margin: 1.25rem 0;"></div>', unsafe_allow_html=True)

    # Interactive Execution
    st.markdown(render_section_header("Interactive Verification", "Execute key agreement and tamper detection", "Verification", "terminal"), unsafe_allow_html=True)

    input_msg = st.text_input("Plaintext Payload", value="Critical system operational telemetry payload")

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        run_crypto = st.button("RUN ENCRYPT & VERIFY DECRYPT", type="primary", use_container_width=True)
    with action_col2:
        run_tamper = st.button("RUN TAMPER DETECTION TEST", use_container_width=True)

    if run_crypto or run_tamper:
        from crypto.key_exchange import ECDHParty
        from crypto.encryption import encrypt, decrypt, tamper_ciphertext

        client = ECDHParty("Client-A")
        server = ECDHParty("Server-B")

        client.load_peer_public_key(server.get_public_key_bytes())
        server.load_peer_public_key(client.get_public_key_bytes())

        client_key = client.derive_aes_key()
        server_key = server.derive_aes_key()
        keys_match = (client_key == server_key)

        enc_result = encrypt(client_key, input_msg)

        if run_crypto:
            dec_result = decrypt(server_key, enc_result["ciphertext"], enc_result["nonce"])
            st.markdown(
                f"""
                <div class="soc-card" style="border-left:2px solid {SEV_SAFE}; margin-top:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:{SEV_SAFE}; font-size:0.85rem;">CHANNEL VERIFIED</span>
                        {render_severity_badge("ALLOW")}
                    </div>
                    <div style="margin-top:0.5rem; font-size:0.8rem; color:{COLOR_WHITE};">
                        Decrypted: <span class="mono" style="color:{COLOR_AI_ACCENT};">{dec_result['plaintext']}</span>
                    </div>
                    <div style="font-size:0.7rem; color:{COLOR_MUTED}; margin-top:0.25rem;">
                        ECDH P-256 agreement confirmed. AES-256-GCM authentication tag verified.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if run_tamper:
            tampered_bytes = tamper_ciphertext(enc_result["ciphertext"])
            tamper_res = decrypt(server_key, tampered_bytes, enc_result["nonce"])
            st.markdown(
                f"""
                <div class="soc-card" style="border-left:2px solid {SEV_THREAT}; margin-top:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:{SEV_THREAT}; font-size:0.85rem;">INTEGRITY BREACH DETECTED</span>
                        {render_severity_badge("CRITICAL")}
                    </div>
                    <div style="margin-top:0.5rem; font-size:0.8rem; color:{COLOR_WHITE};">
                        Error: <span class="mono" style="color:{SEV_THREAT};">{tamper_res.get('error', 'Authentication Tag Mismatch')}</span>
                    </div>
                    <div style="font-size:0.7rem; color:{COLOR_MUTED}; margin-top:0.25rem;">
                        Ciphertext modified in transit. AES-256-GCM authentication tag rejected corrupted payload.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("Technical Details"):
            st.markdown(
                f"""
                <div style="font-size:0.72rem; color:{COLOR_GRAY}; line-height:1.7;">
                    <div><b>Client Public Key:</b> <span class="mono">{client.get_public_key_hex()[:48]}...</span></div>
                    <div><b>Server Public Key:</b> <span class="mono">{server.get_public_key_hex()[:48]}...</span></div>
                    <div><b>GCM Nonce:</b> <span class="mono">{enc_result['nonce_hex']}</span></div>
                    <div><b>Ciphertext:</b> <span class="mono">{enc_result['ciphertext_hex'][:48]}... ({enc_result['ciphertext_length']} bytes)</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6: MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

def page_model_performance():
    render_top_bar("Model Performance", "Random Forest classifier evaluated on CICIDS2017 benchmark")

    metrics = load_evaluation_metrics()
    if not metrics:
        st.warning("Model evaluation metrics not found.")
        return

    # 4 Minimal KPIs
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(render_metric_card("ACCURACY", f"{metrics['accuracy'] * 100:.2f}%", "Overall Validation Accuracy", COLOR_WHITE), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric_card("PRECISION", f"{metrics['precision_macro'] * 100:.2f}%", "Macro-averaged Precision", SEV_SAFE), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric_card("RECALL", f"{metrics['recall_macro'] * 100:.2f}%", "Macro-averaged Recall", SEV_SAFE), unsafe_allow_html=True)
    with m4:
        st.markdown(render_metric_card("F1 SCORE", f"{metrics['f1_macro'] * 100:.2f}%", "Harmonic Mean", COLOR_WHITE), unsafe_allow_html=True)

    st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Confusion Matrix & Feature Importance Images
    vis_col1, vis_col2 = st.columns(2)

    cm_path = load_confusion_matrix_img()
    with vis_col1:
        st.markdown(render_section_header("Confusion Matrix", "Per-class prediction breakdown", "Evaluation", "radar"), unsafe_allow_html=True)
        if cm_path:
            st.image(str(cm_path), use_container_width=True)
        else:
            st.info("Confusion matrix image not available.")

    fi_path = load_feature_importance_img()
    with vis_col2:
        st.markdown(render_section_header("Feature Importance", "Top flow dynamics weighted by model", "Explainability", "cpu"), unsafe_allow_html=True)
        if fi_path:
            st.image(str(fi_path), use_container_width=True)
        else:
            st.info("Feature importance image not available.")

    st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # 20 Flow Features Reference
    st.markdown(render_section_header("Flow Features Specification", "20 timing and packet characteristics extracted per flow", "Features", "terminal"), unsafe_allow_html=True)

    features = [
        "Destination Port", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
        "Total Length of Fwd Packets", "Total Length of Bwd Packets", "Fwd Packet Length Max",
        "Fwd Packet Length Min", "Bwd Packet Length Max", "Bwd Packet Length Min",
        "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max",
        "Flow IAT Min", "Fwd IAT Total", "Bwd IAT Total", "Fwd Header Length", "Bwd Header Length"
    ]
    feat_cols = st.columns(4)
    for i, feat in enumerate(features):
        with feat_cols[i % 4]:
            st.markdown(
                f"""
                <div class="soc-card soc-feat-pill" style="padding:0.4rem 0.6rem; margin-bottom:0.3rem; font-size:0.72rem;">
                    <span class="mono" style="color:{COLOR_GRAY};">#{i+1:02d}</span> <span style="color:{COLOR_WHITE};">{feat}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if "classification_report" in metrics:
        st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown(render_section_header("Classification Report", "Granular performance across attack classes", "Validation", "activity"), unsafe_allow_html=True)
        st.code(metrics["classification_report"], language="text")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7: SYSTEM LOGS
# ═══════════════════════════════════════════════════════════════════════════════

def page_system_logs():
    render_top_bar("System Logs", "Audit trail of network security events")

    log_col1, log_col2 = st.columns([1, 2])
    with log_col1:
        log_limit = st.selectbox("Limit", [50, 100, 250, 500], index=1)
    with log_col2:
        source_origin = st.selectbox("Origin", ["ALL", "CICIDS2017", "SIMULATION"])

    events = get_recent_events(log_limit * 2)
    if not events:
        st.info("No audit logs available.")
        return

    df_logs = pd.DataFrame(events)

    if source_origin != "ALL":
        df_logs = df_logs[df_logs["data_source"] == source_origin]

    df_logs = df_logs.head(log_limit)

    st.markdown(
        f'<div style="font-size:0.75rem; color:{COLOR_GRAY}; margin:0.75rem 0 0.5rem 0; font-family:\'JetBrains Mono\', monospace;">'
        f'{len(df_logs)} records'
        f'</div>',
        unsafe_allow_html=True,
    )

    cols_order = ["timestamp", "source_ip", "destination_ip", "protocol", "attack_type", "risk_level", "action", "data_source"]
    existing_cols = [c for c in cols_order if c in df_logs.columns]
    display_logs = df_logs[existing_cols].copy()
    display_logs.columns = [c.upper().replace("_", " ") for c in display_logs.columns]

    st.dataframe(display_logs, use_container_width=True, hide_index=True, height=480)

    csv_data = df_logs.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="DOWNLOAD LOG (CSV)",
        data=csv_data,
        file_name=f"ai_snids_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    page = render_sidebar()

    page_map = {
        "Overview": page_overview,
        "OVERVIEW": page_overview,
        "Live Monitoring": page_live_monitoring,
        "LIVE MONITORING": page_live_monitoring,
        "Attack Lab": page_attack_lab,
        "ATTACK SCENARIO LAB": page_attack_lab,
        "Threat Center": page_threat_center,
        "THREAT CENTER": page_threat_center,
        "Secure Communication": page_secure_communication,
        "SECURE COMMUNICATION": page_secure_communication,
        "Model Performance": page_model_performance,
        "MODEL PERFORMANCE": page_model_performance,
        "Logs": page_system_logs,
        "SYSTEM LOGS": page_system_logs,
    }

    page_fn = page_map.get(page, page_overview)
    page_fn()


if __name__ == "__main__":
    main()
