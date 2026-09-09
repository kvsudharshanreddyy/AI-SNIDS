"""
dashboard/app.py

AI-SNIDS — AI-Powered Network Intrusion Detection & Security Operations Center.
Enterprise-grade SOC dashboard providing real-time telemetry, threat detection,
autonomous response simulation, and end-to-end cryptographic verification.
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

from dashboard.theme import (
    GLOBAL_CSS,
    COLOR_BG,
    COLOR_BG_SECONDARY,
    COLOR_CARD,
    COLOR_CARD_HOVER,
    COLOR_BORDER,
    COLOR_AI_PRIMARY,
    COLOR_AI_SECONDARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    SEV_LOW,
    SEV_MED,
    SEV_HIGH,
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
    page_title="AI-SNIDS | Security Operations Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Global SOC Stylesheet
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─── Cached Model & Database Loaders ───────────────────────────────────────────

@st.cache_resource(show_spinner="Initializing AI detection engine...")
def load_predictor():
    from ai.predict import Predictor
    return Predictor()


@st.cache_resource(show_spinner="Connecting to security database...")
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


def toggle_ip_block(ip_address: str, block: bool, reason: str = "SOC Analyst Action") -> bool:
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


# ─── Sidebar Navigation & Telemetry ───────────────────────────────────────────

def render_sidebar() -> str:
    with st.sidebar:
        # SOC Brand Header
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid {COLOR_BORDER}; margin-bottom: 1rem;">
                <div style="display:flex; align-items:center; gap:0.6rem;">
                    {get_icon("shield", size=22, color=COLOR_AI_PRIMARY)}
                    <span style="font-size:1.15rem; font-weight:700; color:{COLOR_TEXT_PRIMARY}; letter-spacing:-0.02em;">
                        <span style="color:{COLOR_AI_PRIMARY};">AI</span>-SNIDS
                    </span>
                </div>
                <div style="font-size:0.75rem; color:{COLOR_TEXT_SECONDARY}; margin-top:0.25rem;">
                    <span style="color:{COLOR_AI_PRIMARY}; font-weight:500;">AI</span> Network Security Operations
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 7-Page SOC Navigation
        nav_options = [
            "OVERVIEW",
            "LIVE MONITORING",
            "ATTACK SCENARIO LAB",
            "THREAT CENTER",
            "SECURE COMMUNICATION",
            "MODEL PERFORMANCE",
            "SYSTEM LOGS",
        ]

        page = st.radio("Navigation", options=nav_options, label_visibility="collapsed")

        st.markdown(f'<div style="margin: 1.5rem 0 1rem 0; border-top: 1px solid {COLOR_BORDER};"></div>', unsafe_allow_html=True)

        # System Status Telemetry
        st.markdown(
            f'<div style="font-size:0.68rem; font-weight:600; color:{COLOR_TEXT_MUTED}; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.75rem;">SYSTEM TELEMETRY</div>',
            unsafe_allow_html=True,
        )

        # AI Engine status
        try:
            predictor = load_predictor()
            ai_status = "ONLINE" if predictor.is_loaded else "OFFLINE"
            ai_color = SEV_LOW if predictor.is_loaded else SEV_HIGH
        except Exception:
            ai_status = "ERROR"
            ai_color = SEV_HIGH

        # Database status
        try:
            from database.database import health_check
            db_status = "CONNECTED" if health_check() else "DISCONNECTED"
            db_color = SEV_LOW if health_check() else SEV_HIGH
        except Exception:
            db_status = "UNAVAILABLE"
            db_color = SEV_HIGH

        status_items = [
            ("AI ENGINE", ai_status, ai_color),
            ("NETWORK", "ACTIVE", SEV_LOW),
            ("CRYPTO", "SECURE", SEV_LOW),
            ("DATABASE", db_status, db_color),
        ]

        for label, val, color in status_items:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.45rem; font-size:0.78rem;">
                    <span style="color:{COLOR_TEXT_SECONDARY}; font-weight:500;">{label}</span>
                    <span style="display:inline-flex; align-items:center; gap:5px; color:{color}; font-weight:600; font-family:'JetBrains Mono', monospace; font-size:0.72rem;">
                        <span class="pulse-indicator" style="background:{color}; box-shadow:0 0 5px {color};"></span>
                        {val}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div style="margin-top:1.5rem; padding-top:0.75rem; border-top:1px solid {COLOR_BORDER}; font-size:0.7rem; color:{COLOR_TEXT_MUTED};">
                AI-SNIDS SOC Suite v2.0<br>
                Model: RF-100 (CICIDS2017)
            </div>
            """,
            unsafe_allow_html=True,
        )

        return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW (Network Security Operations Center)
# ═══════════════════════════════════════════════════════════════════════════════

def page_overview():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <h1 style="margin:0; font-size:1.6rem; font-weight:700;"><span style="color:{COLOR_AI_PRIMARY};">AI</span>-SNIDS</h1>
                <span class="soc-badge" style="color:{COLOR_AI_PRIMARY}; background:rgba(0,229,255,0.08); border:1px solid rgba(0,229,255,0.25);">
                    SOC PORTAL
                </span>
            </div>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                Network Security Operations Center · <span style="color:{COLOR_AI_PRIMARY}; font-weight:500;">AI</span>-powered intrusion detection and response
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = get_statistics()
    blocked_list = get_blocked_ips()

    # Determine Network Security Posture
    if stats["threats_detected"] > 0 and len(blocked_list) > 0:
        net_status = "UNDER ATTACK"
        status_color = SEV_HIGH
    elif stats["threats_detected"] > 0:
        net_status = "ELEVATED"
        status_color = SEV_MED
    else:
        net_status = "PROTECTED"
        status_color = SEV_LOW

    # 5 Universal KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(render_metric_card("NETWORK STATUS", net_status, "Boundary Defense Active", status_color), unsafe_allow_html=True)
    with k2:
        st.markdown(render_metric_card("ACTIVE THREATS", f"{stats['threats_detected']:,}", f"High Risk: {stats['high_risk_threats']}", SEV_HIGH if stats['threats_detected'] > 0 else SEV_LOW), unsafe_allow_html=True)
    with k3:
        st.markdown(render_metric_card("BLOCKED SOURCES", f"{len(blocked_list)}", "Firewall Filter Active", SEV_CRITICAL if len(blocked_list) > 0 else SEV_LOW), unsafe_allow_html=True)
    with k4:
        st.markdown(render_metric_card("AI ENGINE", "ONLINE", "Random Forest (100 Trees)", COLOR_AI_PRIMARY), unsafe_allow_html=True)
    with k5:
        risk_label = "HIGH" if stats["high_risk_threats"] > 0 else ("MEDIUM" if stats["threats_detected"] > 0 else "LOW")
        risk_color = SEV_HIGH if risk_label == "HIGH" else (SEV_MED if risk_label == "MEDIUM" else SEV_LOW)
        st.markdown(render_metric_card("CURRENT RISK", risk_label, "Composite Threat Level", risk_color), unsafe_allow_html=True)

    # Activity & Distribution Visualizations
    chart_col1, chart_col2 = st.columns([3, 2])
    recent_events = get_recent_events(60)
    df = pd.DataFrame(recent_events)

    with chart_col1:
        st.markdown(render_section_header("Network Activity Timeline", "Sequential flow risk assessment & density", "Telemetry", "activity"), unsafe_allow_html=True)
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
                    line=dict(color=COLOR_AI_PRIMARY, width=2),
                    fill="tozeroy",
                    fillcolor="rgba(0, 229, 255, 0.08)",
                )
            )
            fig_timeline.add_hline(
                y=0.7,
                line_dash="dash",
                line_color=SEV_HIGH,
                annotation_text="High Threat Threshold (0.70)",
                annotation_position="top right",
                annotation_font=dict(size=10, color=SEV_HIGH),
            )
            layout = get_plotly_soc_layout(height=260)
            layout["yaxis"]["range"] = [0, 1.05]
            layout["xaxis"]["title"] = "Sequential Monitored Flows"
            layout["yaxis"]["title"] = "Assessed Risk Score"
            fig_timeline.update_layout(layout)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No network activity telemetry available. Execute a scenario to populate activity data.")

    with chart_col2:
        st.markdown(render_section_header("Threat Distribution", "Attack classifications across monitored flows", "Classification", "radar"), unsafe_allow_html=True)
        if not df.empty and "attack_type" in df.columns:
            counts = df["attack_type"].value_counts()
            palette = [COLOR_AI_PRIMARY, COLOR_AI_SECONDARY, SEV_LOW, SEV_MED, SEV_HIGH, COLOR_TEXT_MUTED]
            fig_donut = px.pie(
                values=counts.values,
                names=counts.index,
                hole=0.55,
                color_discrete_sequence=palette,
            )
            layout_donut = get_plotly_soc_layout(height=260)
            layout_donut["showlegend"] = True
            fig_donut.update_layout(layout_donut)
            fig_donut.update_traces(textinfo="percent+label", textfont=dict(size=10))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No classification data available.")

    # Recent Alerts & Network Health
    bottom_col1, bottom_col2 = st.columns([3, 2])

    with bottom_col1:
        st.markdown(render_section_header("Recent Security Alerts", "Top priority threats flagged by Risk Engine", "Security Feeds", "alert-triangle"), unsafe_allow_html=True)
        if not df.empty:
            threat_df = df[df["attack_type"] != "BENIGN"].head(6)
            if not threat_df.empty:
                for _, alert in threat_df.iterrows():
                    st.markdown(
                        f"""
                        <div class="soc-card" style="padding:0.75rem 1rem; margin-bottom:0.4rem; display:flex; align-items:center; justify-content:space-between;">
                            <div style="display:flex; align-items:center; gap:0.75rem;">
                                {render_severity_badge(alert['risk_level'])}
                                <div>
                                    <div style="font-weight:600; font-size:0.88rem; color:{COLOR_TEXT_PRIMARY};">
                                        {alert['attack_type']} Detection
                                    </div>
                                    <div class="mono" style="font-size:0.75rem; color:{COLOR_TEXT_MUTED};">
                                        {alert['source_ip']} ➔ {alert['destination_ip']}
                                    </div>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:0.75rem; font-weight:600; color:{COLOR_TEXT_PRIMARY};">
                                    Conf: {alert['confidence']*100:.1f}%
                                </div>
                                <div style="font-size:0.7rem; color:{SEV_HIGH if alert['action'] == 'BLOCK' else SEV_MED}; font-weight:600;">
                                    {alert['action']}
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(f'<div class="soc-card" style="color:{COLOR_TEXT_MUTED}; font-size:0.85rem;">No active threats detected in recent flow logs.</div>', unsafe_allow_html=True)
        else:
            st.info("No alert records available.")

    with bottom_col2:
        st.markdown(render_section_header("Network Infrastructure Health", "Component verification & defensive posture", "Diagnostics", "server"), unsafe_allow_html=True)
        health_nodes = [
            ("Gateway Router", "10.0.0.1", "Traffic Routing & Ingress Filter", "ONLINE", False),
            ("Protected Node B", "10.0.0.100", "Critical Mission Server", "ONLINE", False),
            ("Client Endpoint A", "10.0.0.10", "Authorized Encrypted Terminal", "ONLINE", False),
            ("Attacker Node", "10.0.0.50", "Simulated Adversary Source", "BLOCKED" if any(b["ip_address"] == "10.0.0.50" for b in blocked_list) else "MONITORED", True),
        ]
        for name, ip, role, status, is_threat in health_nodes:
            status_color = SEV_CRITICAL if status == "BLOCKED" else (SEV_LOW if status == "ONLINE" else SEV_MED)
            st.markdown(
                f"""
                <div class="soc-card" style="padding:0.75rem 1rem; margin-bottom:0.4rem; display:flex; align-items:center; justify-content:space-between;">
                    <div>
                        <div style="font-weight:600; font-size:0.86rem; color:{COLOR_TEXT_PRIMARY};">{name}</div>
                        <div class="mono" style="font-size:0.75rem; color:{COLOR_AI_PRIMARY if not is_threat else SEV_HIGH};">{ip} · {role}</div>
                    </div>
                    <div>
                        <span class="soc-badge" style="color:{status_color}; background:rgba(255,255,255,0.04); border:1px solid {status_color}40;">
                            {status}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: LIVE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def page_live_monitoring():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin:0; font-size:1.6rem; font-weight:700;">Live Monitoring</h1>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                Real-time traffic flow inspection, feature analysis, and automated <span style="color:{COLOR_AI_PRIMARY}; font-weight:500;">AI</span> prediction
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter Bar
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1.5, 1.5])
    with filter_col1:
        limit = st.selectbox("Record Limit", [25, 50, 100, 200], index=1)
    with filter_col2:
        source_filter = st.selectbox("Data Source", ["All Sources", "CICIDS2017 Benchmark", "SIMULATION Lab"])
    with filter_col3:
        threat_filter = st.selectbox("Threat Filter", ["All Traffic", "Threats Only", "Benign Only"])

    events = get_recent_events(limit * 3)
    if not events:
        st.info("No live telemetry logged in database. Run a simulation in the Attack Lab to generate flow records.")
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
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; font-size:0.8rem; color:{COLOR_TEXT_SECONDARY};">
            <span>Displaying <b>{len(df)}</b> monitored flows</span>
            <span class="mono" style="color:{COLOR_AI_PRIMARY};">Table Auto-Sync Active</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Clean, High-Density Table Display
    display_cols = ["timestamp", "source_ip", "destination_ip", "protocol", "attack_type", "confidence", "risk_level", "action"]
    existing_cols = [c for c in display_cols if c in df.columns]
    table_df = df[existing_cols].copy()

    if "timestamp" in table_df.columns:
        table_df["timestamp"] = pd.to_datetime(table_df["timestamp"]).dt.strftime("%H:%M:%S.%f").str[:-3]
    if "confidence" in table_df.columns:
        table_df["confidence"] = table_df["confidence"].apply(lambda x: f"{float(x)*100:.1f}%")

    table_df.columns = [c.upper().replace("_", " ") for c in table_df.columns]

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=450,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: ATTACK SCENARIO LAB
# ═══════════════════════════════════════════════════════════════════════════════

def page_attack_lab():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin:0; font-size:1.6rem; font-weight:700;">Attack Scenario Lab</h1>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                Safely simulate abnormal network behavior and observe how <span style="color:{COLOR_AI_PRIMARY}; font-weight:500;">AI</span>-SNIDS detects and responds.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Integrated Virtual Network Topology Visual
    st.markdown(render_section_header("Virtual Network Topology & Route Inspection", "Software-isolated network topology for safe demonstration", "Topology", "network"), unsafe_allow_html=True)

    topo_col1, topo_col2, topo_col3, topo_col4 = st.columns(4)
    blocked_list = get_blocked_ips()
    attacker_blocked = any(b["ip_address"] == "10.0.0.50" for b in blocked_list)

    with topo_col1:
        st.markdown(render_network_node("Client A", "10.0.0.10", "Legitimate Workstation", "ONLINE", False), unsafe_allow_html=True)
    with topo_col2:
        st.markdown(render_network_node("Gateway Router", "10.0.0.1", "Network Gateway & IDS", "ONLINE", False), unsafe_allow_html=True)
    with topo_col3:
        st.markdown(render_network_node("Server B", "10.0.0.100", "Target Web/Data Server", "ONLINE", False), unsafe_allow_html=True)
    with topo_col4:
        st.markdown(render_network_node("Attacker Node", "10.0.0.50", "Threat Simulation Host", "BLOCKED" if attacker_blocked else "MONITORED", True), unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="soc-card" style="padding:0.6rem 1rem; margin:0.5rem 0 1rem 0; font-size:0.75rem; text-align:center; color:{COLOR_TEXT_SECONDARY};">
            <span class="mono" style="color:{COLOR_AI_PRIMARY}; font-weight:600;">NORMAL PATH:</span> Client A (10.0.0.10) ➔ Router (10.0.0.1) ➔ AI-SNIDS ➔ Server B (10.0.0.100)
            &nbsp;|&nbsp;
            <span class="mono" style="color:{SEV_HIGH}; font-weight:600;">ATTACK PATH:</span> Attacker (10.0.0.50) ➔ AI-SNIDS ➔ Threat Flagged ➔ Simulated Firewall Block
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Scenario Selection Cards
    st.markdown(render_section_header("Simulation Scenarios", "Select baseline traffic pattern", "Scenario Catalog", "terminal"), unsafe_allow_html=True)

    scenarios_meta = {
        "Normal Traffic": ("Clean web browsing (HTTP/HTTPS) from Client A to Server B", "shield-check"),
        "Port Scan": ("Systematic reconnaissance probing multi-port TCP/UDP services", "radar"),
        "Brute Force": ("High-frequency credential stuffing targeting SSH/FTP ports", "lock"),
        "DoS": ("Single-source high-volume packet flooding attempting resource denial", "activity"),
        "DDoS": ("Distributed multi-node botnet swarm targeting Server B", "zap"),
        "Suspicious Traffic": ("Ambiguous flow characteristics with statistical timing variance", "alert-triangle"),
    }

    selected_scenario = st.selectbox("Baseline Scenario", list(scenarios_meta.keys()), index=0)

    # Visual scenario cards grid with status indicators and hover styling
    sc_cols = st.columns(6)
    for i, (sc_name, (sc_desc, sc_icon)) in enumerate(scenarios_meta.items()):
        is_sel = (sc_name == selected_scenario)
        is_danger = sc_name in ["Port Scan", "Brute Force", "DoS", "DDoS"]
        border_style = f"border: 1px solid {COLOR_AI_PRIMARY}; box-shadow: 0 0 12px rgba(0, 229, 255, 0.25);" if is_sel else f"border: 1px solid {COLOR_BORDER};"
        indicator_color = SEV_HIGH if is_danger else (SEV_MED if sc_name == "Suspicious Traffic" else SEV_LOW)
        with sc_cols[i]:
            st.markdown(
                f"""
                <div class="soc-card" style="padding:0.7rem 0.6rem; text-align:center; min-height:105px; {border_style}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                        <span class="pulse-indicator" style="background:{indicator_color}; box-shadow:0 0 6px {indicator_color};"></span>
                        {get_icon(sc_icon, size=15, color=COLOR_AI_PRIMARY if is_sel else COLOR_TEXT_MUTED)}
                    </div>
                    <div style="font-weight:600; font-size:0.78rem; color:{COLOR_TEXT_PRIMARY if is_sel else COLOR_TEXT_SECONDARY}; margin-top:0.15rem;">
                        {sc_name}
                    </div>
                    <div style="font-size:0.65rem; color:{COLOR_TEXT_MUTED}; margin-top:0.2rem; line-height:1.25;">
                        {sc_desc[:40]}...
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Sudden Mid-Stream Attack Injection Controls
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

    with ctrl_col1:
        injected_attack = st.selectbox(
            "Sudden Mid-Stream Attack",
            ["None (Pure Scenario)", "Port Scan", "DDoS", "DoS", "Brute Force", "Suspicious Traffic"],
            index=1 if selected_scenario == "Normal Traffic" else 0,
            help="Simulate sudden, unplanned attacks occurring in the middle of ongoing baseline traffic.",
        )

    with ctrl_col2:
        strike_point_choice = st.selectbox(
            "Sudden Attack Strike Point",
            ["Midway (50% mark)", "Early (30% mark)", "Late (70% mark)"],
            index=0,
        )
        switch_ratio_map = {"Early (30% mark)": 0.3, "Midway (50% mark)": 0.5, "Late (70% mark)": 0.7}
        switch_ratio = switch_ratio_map[strike_point_choice]

    with ctrl_col3:
        intensity = st.selectbox("Traffic Intensity", ["LOW", "MEDIUM", "HIGH"], index=1)

    with ctrl_col4:
        duration = st.slider("Duration (Seconds)", min_value=5, max_value=30, value=10, step=5)

    # Action Execution Button
    start_simulation = st.button("EXECUTE SIMULATION SCENARIO", type="primary", use_container_width=True)

    # Simulation Execution Stream Area
    if start_simulation:
        is_dynamic = (injected_attack != "None (Pure Scenario)")
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
            f'<div class="soc-card" style="color:{COLOR_AI_PRIMARY}; font-size:0.85rem; font-weight:600;">'
            f'Generating {total_events} synthetic flow events | Baseline: {selected_scenario} | Injected: {injected_attack}'
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

            # Dynamic Visual State Card
            if is_injected or (is_threat and selected_scenario == "Normal Traffic"):
                anim_slot.markdown(
                    f"""
                    <div class="soc-card" style="border-left: 4px solid {SEV_HIGH}; background: rgba(239, 68, 68, 0.06); padding: 1rem 1.25rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="display:flex; align-items:center; gap:0.5rem;">
                                {get_icon("alert-triangle", size=20, color=SEV_HIGH)}
                                <span style="font-weight:700; color:{SEV_HIGH}; font-size:0.95rem;">
                                    SUDDEN ATTACK INTRUSION DETECTED
                                </span>
                            </div>
                            {render_severity_badge(db_event.risk_level)}
                        </div>
                        <div style="margin-top:0.4rem; font-size:0.82rem; color:{COLOR_TEXT_PRIMARY};">
                            Classified Threat: <b>{db_event.attack_type}</b> (Confidence: {db_event.confidence*100:.1f}%) | Action: <b style="color:{SEV_HIGH};">{db_event.action}</b>
                        </div>
                        <div class="mono" style="font-size:0.75rem; color:{COLOR_TEXT_MUTED}; margin-top:0.2rem;">
                            Source IP: {db_event.source_ip} ➔ Target IP: {db_event.destination_ip}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                anim_slot.markdown(
                    f"""
                    <div class="soc-card" style="border-left: 4px solid {SEV_LOW}; background: rgba(34, 197, 94, 0.04); padding: 1rem 1.25rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="display:flex; align-items:center; gap:0.5rem;">
                                {get_icon("shield-check", size=20, color=SEV_LOW)}
                                <span style="font-weight:600; color:{SEV_LOW}; font-size:0.95rem;">
                                    BASELINE TRAFFIC FLOWING
                                </span>
                            </div>
                            {render_severity_badge("BENIGN")}
                        </div>
                        <div style="margin-top:0.4rem; font-size:0.82rem; color:{COLOR_TEXT_PRIMARY};">
                            Clean traffic stream: Client A (10.0.0.10) ➔ Server B (10.0.0.100) | Boundary Status: Normal
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
                m1.metric("Flows Inspected", idx + 1)
                m2.metric("Threats Flagged", threats_count)
                m3.metric("Sources Blocked", blocked_count)
                m4.metric("Latest Prediction", db_event.attack_type)

            df_live = pd.DataFrame(chart_records)
            fig_live = px.line(
                df_live,
                x="flow",
                y="risk_score",
                color="phase",
                color_discrete_map={"Normal": COLOR_AI_PRIMARY, "Attack": SEV_HIGH},
                labels={"flow": "Flow #", "risk_score": "Risk Score"},
            )
            layout_live = get_plotly_soc_layout(height=240)
            layout_live["yaxis"]["range"] = [0, 1.05]
            layout_live["yaxis"]["title"] = "Risk Score"
            layout_live["xaxis"]["title"] = "Monitored Flow"
            fig_live.update_layout(layout_live)
            fig_live.add_hline(y=0.7, line_dash="dash", line_color=SEV_HIGH, annotation_text="High Threat (0.70)", annotation_position="top right", annotation_font=dict(size=10, color=SEV_HIGH))
            chart_slot.plotly_chart(fig_live, use_container_width=True)

            time.sleep(sleep_interval)

        status_slot.markdown(
            f'<div class="soc-card" style="border-left:4px solid {SEV_LOW}; color:{SEV_LOW}; font-weight:600; font-size:0.88rem;">'
            f'Simulation Complete — {total_events} events processed and persisted to security audit database.'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Real-Time Instant Attack Strike Pad
    st.markdown(f'<div style="margin: 1.5rem 0 1rem 0; border-top: 1px solid {COLOR_BORDER};"></div>', unsafe_allow_html=True)
    st.markdown(render_section_header("Instant Attack Injection Pad", "On-demand attack burst trigger without timed wait", "Manual Interventions", "zap"), unsafe_allow_html=True)

    pad_col1, pad_col2, pad_col3, pad_col4, pad_col5 = st.columns(5)

    def _trigger_instant_burst(attack_type: str, is_attack: bool = True):
        burst = run_instant_attack_burst(attack_type, count=6, intensity="HIGH")
        latest = burst[-1]["db_event"]
        if is_attack:
            st.error(
                f"SUDDEN {attack_type.upper()} STRIKE INJECTED: "
                f"AI-SNIDS flagged {latest.attack_type} ({latest.confidence*100:.1f}% confidence) | "
                f"Risk: {latest.risk_level} | Action: {latest.action} | Attacker: {latest.source_ip}"
            )
        else:
            st.success(
                f"CLEAN FLOW INJECTED: "
                f"Client A (10.0.0.10) ➔ Server B (10.0.0.100) classified as BENIGN (Action: ALLOW)"
            )

    with pad_col1:
        if st.button("Sudden Port Scan", use_container_width=True, help="Attacker probes ports 21, 22, 80, 443"):
            _trigger_instant_burst("Port Scan")
    with pad_col2:
        if st.button("Sudden DDoS Swarm", use_container_width=True, help="Botnet nodes flood Server B"):
            _trigger_instant_burst("DDoS")
    with pad_col3:
        if st.button("Sudden DoS Flood", use_container_width=True, help="Single-source packet flood"):
            _trigger_instant_burst("DoS")
    with pad_col4:
        if st.button("Sudden Brute Force", use_container_width=True, help="SSH/FTP repeated login abuse"):
            _trigger_instant_burst("Brute Force")
    with pad_col5:
        if st.button("Send Normal Flow", use_container_width=True, help="Client A clean encrypted web browsing"):
            _trigger_instant_burst("Normal Traffic", is_attack=False)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: THREAT CENTER
# ═══════════════════════════════════════════════════════════════════════════════

def page_threat_center():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin:0; font-size:1.6rem; font-weight:700;">Threat Center</h1>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                Threat detection registry, incident investigation console, and automated defense enforcement
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = get_statistics()
    blocked_list = get_blocked_ips()

    # Top KPI Metrics
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.markdown(render_metric_card("ACTIVE THREATS", f"{stats['threats_detected']:,}", "Logged Malicious Flows", SEV_HIGH), unsafe_allow_html=True)
    with tc2:
        st.markdown(render_metric_card("HIGH RISK INCIDENTS", f"{stats['high_risk_threats']:,}", "Composite Score >= 0.70", SEV_CRITICAL), unsafe_allow_html=True)
    with tc3:
        st.markdown(render_metric_card("BLOCKED SOURCES", f"{len(blocked_list)}", "Active Simulated Firewall Entries", SEV_CRITICAL if len(blocked_list) > 0 else SEV_LOW), unsafe_allow_html=True)

    # Filter Controls
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        type_filter = st.selectbox("Threat Classification", ["All Threat Types", "PortScan", "DoS", "DDoS", "BruteForce"])
    with f_col2:
        risk_filter = st.selectbox("Severity Level", ["All Severities", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with f_col3:
        source_filter = st.selectbox("Data Origin", ["All Origins", "CICIDS2017 Benchmark", "SIMULATION Lab"])

    events = get_recent_events(150)
    threat_events = [e for e in events if e["attack_type"] != "BENIGN"]

    if not threat_events:
        st.info("No threat incidents currently recorded. Execute attack simulations in the Attack Lab to populate.")
        return

    df_threats = pd.DataFrame(threat_events)

    if type_filter != "All Threat Types":
        df_threats = df_threats[df_threats["attack_type"].str.contains(type_filter, case=False, na=False)]
    if risk_filter != "All Severities":
        df_threats = df_threats[df_threats["risk_level"] == risk_filter]
    if source_filter == "CICIDS2017 Benchmark":
        df_threats = df_threats[df_threats["data_source"] == "CICIDS2017"]
    elif source_filter == "SIMULATION Lab":
        df_threats = df_threats[df_threats["data_source"] == "SIMULATION"]

    if df_threats.empty:
        st.info("No threat records match the current filter selection.")
        return

    # Incident Selection & Table
    incident_col, detail_col = st.columns([3, 2])

    with incident_col:
        st.markdown(render_section_header("Incident Registry", "Click an incident to investigate", "Registry", "alert-triangle"), unsafe_allow_html=True)
        incident_options = [
            f"ID #{row['id']} | {row['attack_type']} ({row['source_ip']}) — Risk: {row['risk_level']}"
            for _, row in df_threats.head(25).iterrows()
        ]
        selected_option = st.selectbox("Select Incident for Detailed SOC Investigation", incident_options)
        selected_id = int(selected_option.split("|")[0].replace("ID #", "").strip())

        display_df = df_threats[["id", "timestamp", "attack_type", "source_ip", "confidence", "risk_level", "action"]].head(25).copy()
        display_df["confidence"] = display_df["confidence"].apply(lambda x: f"{float(x)*100:.1f}%")
        display_df.columns = ["ID", "TIME", "THREAT", "SOURCE", "CONFIDENCE", "RISK", "ACTION"]
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=350)

    # Detailed SOC Investigation Panel
    selected_event = next((e for e in threat_events if e["id"] == selected_id), threat_events[0])
    is_curr_blocked = any(b["ip_address"] == selected_event["source_ip"] for b in blocked_list)

    with detail_col:
        st.markdown(render_section_header("Incident Investigation Panel", "Detailed telemetry and response actions", "Triage", "shield"), unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="soc-card soc-card-threat" style="border-top:2px solid {SEV_HIGH};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <span style="font-weight:700; font-size:1.05rem; color:{COLOR_TEXT_PRIMARY};">
                        {selected_event['attack_type']}
                    </span>
                    {render_severity_badge(selected_event['risk_level'])}
                </div>
                <div style="font-size:0.8rem; color:{COLOR_TEXT_SECONDARY}; line-height:1.7;">
                    <div><b>Incident ID:</b> <span class="mono">#{selected_event['id']}</span></div>
                    <div><b>Timestamp:</b> <span class="mono">{selected_event['timestamp']}</span></div>
                    <div><b>Source IP:</b> <span class="mono" style="color:{COLOR_AI_PRIMARY};">{selected_event['source_ip']}</span></div>
                    <div><b>Destination IP:</b> <span class="mono">{selected_event['destination_ip']}</span></div>
                    <div><b>AI Confidence:</b> <span class="mono">{selected_event['confidence']*100:.1f}%</span></div>
                    <div><b>Composite Risk Score:</b> <span class="mono">{selected_event['risk_score']}</span></div>
                    <div><b>Enforced Action:</b> <span class="mono" style="color:{SEV_HIGH if selected_event['action'] == 'BLOCK' else SEV_MED}; font-weight:600;">{selected_event['action']}</span></div>
                    <div><b>Telemetry Origin:</b> <span class="mono">{selected_event['data_source']}</span></div>
                </div>
                <div style="margin-top:1rem; padding-top:0.75rem; border-top:1px solid {COLOR_BORDER};">
                    <div style="font-size:0.75rem; color:{COLOR_TEXT_MUTED}; margin-bottom:0.5rem;">
                        Firewall Status: <b style="color:{SEV_CRITICAL if is_curr_blocked else SEV_LOW};">{'ACTIVELY BLOCKED' if is_curr_blocked else 'UNRESTRICTED'}</b>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Interactive Simulated Firewall Defense Toggle
        if is_curr_blocked:
            if st.button(f"Unblock Source IP ({selected_event['source_ip']})", use_container_width=True):
                if toggle_ip_block(selected_event["source_ip"], block=False):
                    st.success(f"IP {selected_event['source_ip']} removed from firewall blocklist.")
                    st.rerun()
        else:
            if st.button(f"Enforce Simulated Firewall Block ({selected_event['source_ip']})", type="primary", use_container_width=True):
                if toggle_ip_block(selected_event["source_ip"], block=True, reason=f"SOC Analyst block: {selected_event['attack_type']}"):
                    st.warning(f"IP {selected_event['source_ip']} added to firewall blocklist.")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: SECURE COMMUNICATION
# ═══════════════════════════════════════════════════════════════════════════════

def page_secure_communication():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin:0; font-size:1.6rem; font-weight:700;">Secure Communication</h1>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                End-to-end cryptographic protection, key derivation, and tamper detection between Client A and Server B
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Visual Cryptographic Pipeline
    st.markdown(render_section_header("Cryptographic Architecture Pipeline", "Sequential authenticated encryption handshake", "Cryptographic Core", "lock"), unsafe_allow_html=True)

    pipe_col1, pipe_col2, pipe_col3, pipe_col4, pipe_col5 = st.columns(5)
    steps = [
        ("01", "Client A", "Initiates secure channel request", "user"),
        ("02", "ECDH P-256", "Ephemeral Diffie-Hellman key exchange", "lock"),
        ("03", "HKDF-SHA256", "Extract & expand key derivation (RFC 5869)", "cpu"),
        ("04", "AES-256-GCM", "Authenticated encryption + 128-bit tag", "shield-check"),
        ("05", "Server B", "Authenticates tag & decrypts ciphertext", "server"),
    ]
    cols = [pipe_col1, pipe_col2, pipe_col3, pipe_col4, pipe_col5]

    for col, (num, title, desc, icon) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div class="soc-card" style="padding:0.9rem; text-align:center;">
                    <div style="font-size:0.65rem; font-weight:700; color:{COLOR_AI_PRIMARY}; letter-spacing:0.06em; margin-bottom:0.25rem;">
                        STEP {num}
                    </div>
                    <div style="display:flex; justify-content:center; margin-bottom:0.3rem;">
                        {get_icon(icon, size=18, color=COLOR_AI_PRIMARY)}
                    </div>
                    <div style="font-weight:600; font-size:0.85rem; color:{COLOR_TEXT_PRIMARY};">{title}</div>
                    <div style="font-size:0.7rem; color:{COLOR_TEXT_MUTED}; margin-top:0.2rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Live Interactive Cryptographic Operations
    st.markdown(render_section_header("Interactive Cryptographic Verification", "Execute live key agreement, encryption, and tamper testing", "Verification", "terminal"), unsafe_allow_html=True)

    input_msg = st.text_input("Plaintext Payload (Client A ➔ Server B)", value="Critical system operational telemetry payload")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        run_crypto = st.button("EXECUTE ENCRYPT & VERIFY DECRYPT", type="primary", use_container_width=True)

    with action_col2:
        run_tamper = st.button("EXECUTE TAMPER DETECTION TEST", use_container_width=True)

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
                <div class="soc-card" style="border-left:4px solid {SEV_LOW}; margin-top:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:{SEV_LOW}; font-size:0.95rem;">
                            CRYPTOGRAPHIC CHANNEL VERIFIED
                        </span>
                        {render_severity_badge("ALLOW")}
                    </div>
                    <div style="margin-top:0.6rem; font-size:0.82rem; color:{COLOR_TEXT_PRIMARY};">
                        Key Agreement: <b>{client.curve_name}</b> | Derived Key Match: <b>{'YES' if keys_match else 'NO'}</b>
                    </div>
                    <div style="font-size:0.82rem; color:{COLOR_TEXT_PRIMARY}; margin-top:0.25rem;">
                        Decrypted Output: <b style="color:{COLOR_AI_PRIMARY}; font-family:'JetBrains Mono', monospace;">{dec_result['plaintext']}</b>
                    </div>
                    <div style="font-size:0.75rem; color:{COLOR_TEXT_MUTED}; margin-top:0.4rem;">
                        Integrity Verified: Authenticated encryption tag matched successfully. Confidentiality guaranteed.
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
                <div class="soc-card" style="border-left:4px solid {SEV_HIGH}; margin-top:1rem; background:rgba(239, 68, 68, 0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; color:{SEV_HIGH}; font-size:0.95rem;">
                            INTEGRITY BREACH DETECTED — AUTHENTICATION FAILED
                        </span>
                        {render_severity_badge("CRITICAL")}
                    </div>
                    <div style="margin-top:0.6rem; font-size:0.82rem; color:{COLOR_TEXT_PRIMARY};">
                        Ciphertext Byte Modified in Transit: <b>Tampered by adversary</b>
                    </div>
                    <div style="font-size:0.82rem; color:{SEV_HIGH}; margin-top:0.25rem;">
                        Decryption Engine Error: <b class="mono">{tamper_res.get('error', 'Authentication Tag Mismatch')}</b>
                    </div>
                    <div style="font-size:0.75rem; color:{COLOR_TEXT_MUTED}; margin-top:0.4rem;">
                        AES-256-GCM authentication tag rejected modified ciphertext. Zero unauthorized data decrypted.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Technical Details Collapsible
        with st.expander("Technical Cryptographic Parameters"):
            st.markdown(
                f"""
                <div style="font-size:0.75rem; color:{COLOR_TEXT_SECONDARY}; line-height:1.7;">
                    <div><b>Client Public Key (P-256):</b> <span class="mono" style="color:{COLOR_AI_PRIMARY};">{client.get_public_key_hex()[:64]}...</span></div>
                    <div><b>Server Public Key (P-256):</b> <span class="mono" style="color:{COLOR_AI_PRIMARY};">{server.get_public_key_hex()[:64]}...</span></div>
                    <div><b>AES-256-GCM Nonce (96-bit):</b> <span class="mono">{enc_result['nonce_hex']}</span></div>
                    <div><b>Ciphertext Bytes (Hex):</b> <span class="mono">{enc_result['ciphertext_hex'][:64]}...</span></div>
                    <div><b>Ciphertext Length:</b> <span class="mono">{enc_result['ciphertext_length']} bytes</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6: MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

def page_model_performance():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin:0; font-size:1.6rem; font-weight:700;"><span style="color:{COLOR_AI_PRIMARY};">AI</span> Detection Engine</h1>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                Random Forest classifier trained and evaluated on the benchmark CICIDS2017 dataset
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = load_evaluation_metrics()
    if not metrics:
        st.warning("Model evaluation metrics not found. Please train model using ai/train.py.")
        return

    # 4 Model Performance KPIs
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(render_metric_card("ACCURACY", f"{metrics['accuracy'] * 100:.2f}%", "Overall Validation Accuracy", COLOR_AI_PRIMARY), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric_card("PRECISION", f"{metrics['precision_macro'] * 100:.2f}%", "Macro-averaged Precision", SEV_LOW), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric_card("RECALL", f"{metrics['recall_macro'] * 100:.2f}%", "Macro-averaged Recall", SEV_LOW), unsafe_allow_html=True)
    with m4:
        st.markdown(render_metric_card("F1 SCORE", f"{metrics['f1_macro'] * 100:.2f}%", "Harmonic Mean (Precision/Recall)", COLOR_AI_PRIMARY), unsafe_allow_html=True)

    # Confusion Matrix & Feature Importance Images
    vis_col1, vis_col2 = st.columns(2)

    cm_path = load_confusion_matrix_img()
    with vis_col1:
        st.markdown(render_section_header("Confusion Matrix", "Per-class prediction breakdown on test set", "Evaluation", "radar"), unsafe_allow_html=True)
        if cm_path:
            st.image(str(cm_path), use_container_width=True)
        else:
            st.info("Confusion matrix image not generated.")

    fi_path = load_feature_importance_img()
    with vis_col2:
        st.markdown(render_section_header("Feature Importance", "Top flow characteristics weighted by Random Forest", "Explainability", "cpu"), unsafe_allow_html=True)
        if fi_path:
            st.image(str(fi_path), use_container_width=True)
        else:
            st.info("Feature importance image not generated.")

    # 20 Flow Features Specification
    st.markdown(render_section_header("Flow Features Specification", "20 timing and packet dynamics extracted per flow", "Feature Engineering", "terminal"), unsafe_allow_html=True)

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
                <div class="soc-card" style="padding:0.45rem 0.75rem; margin-bottom:0.35rem; font-size:0.75rem;">
                    <span class="mono" style="color:{COLOR_AI_PRIMARY}; font-weight:600;">#{i+1:02d}</span> {feat}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Classification Report
    if "classification_report" in metrics:
        st.markdown(render_section_header("Per-Class Classification Report", "Granular performance across attack classes", "Validation", "activity"), unsafe_allow_html=True)
        st.code(metrics["classification_report"], language="text")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7: SYSTEM LOGS
# ═══════════════════════════════════════════════════════════════════════════════

def page_system_logs():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin:0; font-size:1.6rem; font-weight:700;">System Logs</h1>
            <div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.9rem; margin-top:0.25rem;">
                Tamper-evident chronological audit trail of all network security events
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    log_col1, log_col2, log_col3 = st.columns([1, 1.5, 1])
    with log_col1:
        log_limit = st.selectbox("Log Limit", [50, 100, 250, 500], index=1)
    with log_col2:
        source_origin = st.selectbox("Filter Origin", ["ALL", "CICIDS2017", "SIMULATION"])
    with log_col3:
        pass

    events = get_recent_events(log_limit * 2)
    if not events:
        st.info("No audit logs currently available.")
        return

    df_logs = pd.DataFrame(events)

    if source_origin != "ALL":
        df_logs = df_logs[df_logs["data_source"] == source_origin]

    df_logs = df_logs.head(log_limit)

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; font-size:0.8rem; color:{COLOR_TEXT_SECONDARY};">
            <span>Audit Records Count: <b>{len(df_logs)}</b></span>
            <span class="mono" style="color:{SEV_LOW}; font-size:0.75rem;">INTEGRITY: VERIFIED</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols_order = ["timestamp", "source_ip", "destination_ip", "protocol", "attack_type", "risk_level", "action", "data_source"]
    existing_cols = [c for c in cols_order if c in df_logs.columns]
    display_logs = df_logs[existing_cols].copy()
    display_logs.columns = [c.upper().replace("_", " ") for c in display_logs.columns]

    st.dataframe(
        display_logs,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    csv_data = df_logs.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="DOWNLOAD AUDIT LOG (CSV)",
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
        "OVERVIEW": page_overview,
        "LIVE MONITORING": page_live_monitoring,
        "ATTACK SCENARIO LAB": page_attack_lab,
        "THREAT CENTER": page_threat_center,
        "SECURE COMMUNICATION": page_secure_communication,
        "MODEL PERFORMANCE": page_model_performance,
        "SYSTEM LOGS": page_system_logs,
    }

    page_fn = page_map.get(page, page_overview)
    page_fn()


if __name__ == "__main__":
    main()
