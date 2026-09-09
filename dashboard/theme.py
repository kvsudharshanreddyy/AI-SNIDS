"""
dashboard/theme.py

AI-SNIDS Visual Design System & Component Library.
Maximally dark AI Cybersecurity SOC theme (#050505 canvas, #0D0D0D cards, #00E5FF electric cyan accent).
Provides color tokens, global CSS variables, Lucide-style SVG vector icons, and reusable
components with refined hover transitions and zero emojis.
"""

# ─── Color Palette Tokens (Maximally Dark SOC Aesthetic) ───────────────────────
COLOR_BG = "#050505"                # Maximally dark / near-black primary canvas
COLOR_BG_SECONDARY = "#0A0A0A"      # Secondary background / panels
COLOR_BG_SIDEBAR = "#030303"        # Deep black sidebar canvas
COLOR_BORDER_SIDEBAR = "#1A1A1A"    # Sidebar border
COLOR_CARD = "#0D0D0D"              # Card surface
COLOR_CARD_HOVER = "#141414"        # Card hover elevation
COLOR_BORDER = "#1F1F1F"            # Global subtle borders

COLOR_AI_PRIMARY = "#00E5FF"        # Electric Cyan - Primary AI accent & monitoring
COLOR_AI_SECONDARY = "#3B82F6"      # Electric Blue - Supporting AI & neural core

COLOR_TEXT_PRIMARY = "#FFFFFF"      # White for important headings & focal points
COLOR_TEXT_SECONDARY = "#A1A1AA"    # Neutral gray for labels and secondary text
COLOR_TEXT_MUTED = "#71717A"        # Muted gray for timestamps and technical keys
COLOR_TEXT_TECH = "#D4D4D8"         # Technical telemetry monospace text

# Universal Security Severity Palette
SEV_LOW = "#22C55E"                 # Normal / Safe / Low
SEV_MED = "#F59E0B"                 # Medium / Warning
SEV_HIGH = "#EF4444"                # High threat / Block alerts
SEV_CRITICAL = "#DC2626"            # Critical volumetric flood / emergency
SEV_BLOCKED = "#EF4444"             # Blocked indicator

# ─── Lucide SVG Icons ──────────────────────────────────────────────────────────
ICONS = {
    "shield": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    ),
    "shield-check": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="m9 12 2 2 4-4"/></svg>'
    ),
    "network": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/>'
        '<rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/>'
        '<path d="M12 12V8"/></svg>'
    ),
    "cpu": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>'
        '<path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/>'
        '<path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>'
    ),
    "activity": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    ),
    "alert-triangle": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    ),
    "server": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="20" height="8" x="2" y="2" rx="2" ry="2"/>'
        '<rect width="20" height="8" x="2" y="14" rx="2" ry="2"/>'
        '<line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>'
    ),
    "user": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/></svg>'
    ),
    "lock": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
    ),
    "database": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5V19A9 3 0 0 0 21 19V5"/>'
        '<path d="M3 12A9 3 0 0 0 21 12"/></svg>'
    ),
    "ban": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/></svg>'
    ),
    "radar": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/>'
        '<path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/>'
        '<path d="M16.24 7.76A6 6 0 1 0 8.23 16.24"/>'
        '<path d="M12 12h.01"/><path d="m12 12 5-5"/></svg>'
    ),
    "filter": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>'
    ),
    "terminal": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/></svg>'
    ),
    "arrow-right": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'
    ),
    "check": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="20 6 9 17 4 12"/></svg>'
    ),
    "zap": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
    ),
}


def get_icon(name: str, size: int = 16, color: str = COLOR_AI_PRIMARY) -> str:
    """Return raw inline SVG string for the requested Lucide icon."""
    template = ICONS.get(name, ICONS["shield"])
    return template.format(size=size, color=color)


# ─── Global CSS Stylesheet ─────────────────────────────────────────────────────
GLOBAL_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ─── CSS Custom Properties (Theme Tokens) ─── */
    :root {{
        --bg-primary: {COLOR_BG};
        --bg-secondary: {COLOR_BG_SECONDARY};
        --bg-sidebar: {COLOR_BG_SIDEBAR};
        --bg-card: {COLOR_CARD};
        --bg-hover: {COLOR_CARD_HOVER};
        --border: {COLOR_BORDER};
        --border-sidebar: {COLOR_BORDER_SIDEBAR};
        --accent: {COLOR_AI_PRIMARY};
        --accent-secondary: {COLOR_AI_SECONDARY};
        --accent-glow: rgba(0, 229, 255, 0.16);
        --accent-glow-strong: rgba(0, 229, 255, 0.38);
        --text-primary: {COLOR_TEXT_PRIMARY};
        --text-secondary: {COLOR_TEXT_SECONDARY};
        --text-muted: {COLOR_TEXT_MUTED};
        --text-tech: {COLOR_TEXT_TECH};
        --success: {SEV_LOW};
        --warning: {SEV_MED};
        --danger: {SEV_HIGH};
        --critical: {SEV_CRITICAL};
    }}

    /* Base Reset & Typography */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.011em;
        color: var(--text-primary);
        background-color: var(--bg-primary) !important;
    }}

    .stApp {{
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }}

    header[data-testid="stHeader"] {{
        background-color: var(--bg-primary) !important;
        border-bottom: 1px solid var(--border) !important;
    }}

    /* Sidebar Styling (Maximally Black #030303) */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-sidebar) !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background-color: var(--bg-sidebar) !important;
    }}

    /* Sidebar Radio Navigation Override */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
        gap: 4px;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        background: transparent;
        border: 1px solid transparent;
        border-left: 2px solid transparent;
        padding: 0.55rem 0.85rem;
        border-radius: 6px;
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        cursor: pointer;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background-color: #121212 !important;
        border-left: 2px solid rgba(0, 229, 255, 0.4) !important;
        color: var(--accent) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
        background-color: var(--bg-secondary) !important;
        border-left: 2px solid var(--accent) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
        box-shadow: inset 4px 0 10px rgba(0, 229, 255, 0.15) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] input {{
        accent-color: var(--accent) !important;
    }}

    /* Typography Hierarchy */
    h1, h2, h3, h4 {{
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
    }}

    code, kbd, samp, pre, .mono {{
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
        color: var(--text-tech);
    }}

    /* Standardized Button System */
    .stButton > button {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 1.1rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
    }}
    .stButton > button:hover {{
        background-color: var(--bg-hover) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        box-shadow: 0 0 14px var(--accent-glow) !important;
        transform: translateY(-1px);
    }}
    .stButton > button:active {{
        transform: scale(0.98) !important;
    }}

    /* Primary Accent Button */
    .stButton > button[kind="primary"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--accent) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #000000 !important;
        box-shadow: 0 0 20px var(--accent-glow-strong) !important;
        transform: translateY(-1px);
    }}

    /* Native Metric Cards Override */
    [data-testid="metric-container"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 1.1rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    [data-testid="metric-container"]:hover {{
        background-color: var(--bg-hover) !important;
        border-color: rgba(0, 229, 255, 0.4) !important;
        box-shadow: 0 0 16px var(--accent-glow) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        letter-spacing: -0.02em !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.06em !important;
        font-weight: 600 !important;
    }}

    /* Dataframe / Tables */
    [data-testid="stDataFrame"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }}

    /* Inputs, Selectbox & Radios */
    [data-testid="stSelectbox"] > div > div {{
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }}
    [data-testid="stSelectbox"] > div > div:hover {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 10px var(--accent-glow) !important;
    }}

    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {{
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }}
    [data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 10px var(--accent-glow) !important;
    }}

    /* Dropdown Popover Menus */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
    }}
    li[data-baseweb="menu-item"] {{
        color: var(--text-primary) !important;
        transition: all 0.15s ease !important;
    }}
    li[data-baseweb="menu-item"]:hover {{
        background-color: var(--bg-hover) !important;
        color: var(--accent) !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        transition: border-color 0.2s ease;
    }}
    [data-testid="stExpander"]:hover {{
        border-color: rgba(0, 229, 255, 0.35) !important;
    }}

    /* Minimal Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border);
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--accent);
    }}

    /* Custom Reusable SOC Classes */
    .soc-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .soc-card:hover {{
        border-color: rgba(0, 229, 255, 0.4);
        background-color: var(--bg-hover);
        box-shadow: 0 0 16px var(--accent-glow);
        transform: translateY(-1px);
    }}

    .soc-card-threat:hover {{
        border-color: rgba(239, 68, 68, 0.6) !important;
        background-color: var(--bg-hover) !important;
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.2) !important;
        transform: translateY(-1px);
    }}

    .soc-node {{
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .soc-node:hover {{
        background-color: var(--bg-hover);
        box-shadow: 0 0 18px var(--accent-glow);
        border-color: var(--accent);
        transform: translateY(-2px);
    }}
    .soc-node-threat:hover {{
        background-color: var(--bg-hover);
        box-shadow: 0 0 18px rgba(239, 68, 68, 0.3) !important;
        border-color: var(--danger) !important;
        transform: translateY(-2px);
    }}

    .soc-badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }}

    .pulse-indicator {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        display: inline-block;
    }}
</style>
"""


# ─── Reusable HTML Components ──────────────────────────────────────────────────

def render_section_header(title: str, subtitle: str = None, category: str = None, icon_name: str = "shield") -> str:
    """Render a clean SOC section header with electric cyan category badge."""
    icon_svg = get_icon(icon_name, size=18, color=COLOR_AI_PRIMARY)
    category_html = (
        f'<div style="font-size:0.68rem; font-weight:700; letter-spacing:0.08em; '
        f'color:{COLOR_AI_PRIMARY}; text-transform:uppercase; margin-bottom:0.15rem;">'
        f'{category}</div>'
    ) if category else ""

    sub_html = (
        f'<div style="color:{COLOR_TEXT_SECONDARY}; font-size:0.82rem; margin-top:0.2rem;">'
        f'{subtitle}</div>'
    ) if subtitle else ""

    highlighted_title = (
        title.replace("AI-SNIDS", f'<span style="color:{COLOR_AI_PRIMARY};">AI</span>-SNIDS')
        .replace(" AI ", f' <span style="color:{COLOR_AI_PRIMARY};">AI</span> ')
    )

    return f"""
    <div style="margin: 0.8rem 0 0.8rem 0;">
        {category_html}
        <div style="display:flex; align-items:center; gap:0.5rem;">
            {icon_svg}
            <h3 style="margin:0; font-size:1.15rem; font-weight:600; color:{COLOR_TEXT_PRIMARY};">{highlighted_title}</h3>
        </div>
        {sub_html}
    </div>
    """


def render_metric_card(label: str, value: str, subtitle: str = None, status_color: str = None) -> str:
    """Render a SOC metric card matching maximally dark aesthetic with hover elevation and cyan glow."""
    dot_html = (
        f'<span class="pulse-indicator" style="background:{status_color}; '
        f'box-shadow: 0 0 8px {status_color}; margin-right:6px;"></span>'
    ) if status_color else ""

    sub_html = (
        f'<div style="color:{COLOR_TEXT_MUTED}; font-size:0.72rem; margin-top:0.35rem;">{subtitle}</div>'
    ) if subtitle else ""

    return f"""
    <div class="soc-card" style="padding:1.1rem 1.2rem; margin-bottom:0.5rem;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <span style="color:{COLOR_TEXT_SECONDARY}; font-size:0.7rem; font-weight:600; letter-spacing:0.06em; text-transform:uppercase;">
                {label}
            </span>
            <div>{dot_html}</div>
        </div>
        <div style="font-size:1.65rem; font-weight:600; color:{COLOR_TEXT_PRIMARY}; margin-top:0.3rem; letter-spacing:-0.02em;">
            {value}
        </div>
        {sub_html}
    </div>
    """


def render_severity_badge(level: str) -> str:
    """Render a severity badge (LOW, MEDIUM, HIGH, CRITICAL, BLOCKED) using universal color tokens."""
    lvl = str(level).upper().strip()
    color_map = {
        "LOW": (SEV_LOW, "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)"),
        "BENIGN": (SEV_LOW, "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)"),
        "NORMAL": (SEV_LOW, "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)"),
        "SAFE": (SEV_LOW, "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)"),
        "ALLOW": (SEV_LOW, "rgba(34, 197, 94, 0.1)", "rgba(34, 197, 94, 0.3)"),
        "MONITOR": (COLOR_AI_PRIMARY, "rgba(0, 229, 255, 0.1)", "rgba(0, 229, 255, 0.3)"),
        "LOG": (COLOR_AI_PRIMARY, "rgba(0, 229, 255, 0.1)", "rgba(0, 229, 255, 0.3)"),
        "MEDIUM": (SEV_MED, "rgba(245, 158, 11, 0.1)", "rgba(245, 158, 11, 0.3)"),
        "WARNING": (SEV_MED, "rgba(245, 158, 11, 0.1)", "rgba(245, 158, 11, 0.3)"),
        "ALERT": (SEV_MED, "rgba(245, 158, 11, 0.1)", "rgba(245, 158, 11, 0.3)"),
        "HIGH": (SEV_HIGH, "rgba(239, 68, 68, 0.12)", "rgba(239, 68, 68, 0.35)"),
        "CRITICAL": (SEV_CRITICAL, "rgba(220, 38, 38, 0.15)", "rgba(220, 38, 38, 0.45)"),
        "BLOCK": (SEV_CRITICAL, "rgba(220, 38, 38, 0.15)", "rgba(220, 38, 38, 0.45)"),
        "BLOCKED": (SEV_HIGH, "rgba(239, 68, 68, 0.12)", "rgba(239, 68, 68, 0.35)"),
    }
    fg, bg, border = color_map.get(lvl, (COLOR_TEXT_SECONDARY, "rgba(161, 161, 170, 0.08)", "rgba(161, 161, 170, 0.2)"))

    return (
        f'<span class="soc-badge" style="color:{fg}; background:{bg}; border:1px solid {border};">'
        f'{lvl}</span>'
    )


def render_network_node(name: str, ip: str, role: str, status: str, is_threat: bool = False) -> str:
    """Render a network node card for topology visualizations with rich hover glow."""
    accent_color = SEV_HIGH if is_threat else ("#3B82F6" if "Server" in name else COLOR_AI_PRIMARY)
    status_color = SEV_CRITICAL if "BLOCK" in status.upper() else (SEV_HIGH if is_threat else SEV_LOW)
    icon_name = "alert-triangle" if is_threat else ("server" if "Server" in name or "Router" in name else "user")
    icon_svg = get_icon(icon_name, size=20, color=accent_color)
    card_class = "soc-node soc-node-threat" if is_threat else "soc-node"

    return f"""
    <div class="{card_class}" style="border-top:2px solid {accent_color};">
        <div style="display:flex; justify-content:center; margin-bottom:0.4rem;">{icon_svg}</div>
        <div style="font-weight:600; font-size:0.92rem; color:{COLOR_TEXT_PRIMARY};">{name}</div>
        <div class="mono" style="font-size:0.78rem; color:{accent_color}; margin:0.15rem 0;">{ip}</div>
        <div style="font-size:0.7rem; color:{COLOR_TEXT_MUTED};">{role}</div>
        <div style="margin-top:0.4rem;">
            <span class="soc-badge" style="color:{status_color}; background:rgba(255,255,255,0.03); border:1px solid {status_color}40;">
                {status}
            </span>
        </div>
    </div>
    """


def get_plotly_soc_layout(height: int = 260) -> dict:
    """Standardized Plotly dark layout dictionary for SOC dashboards (Maximally Dark Theme)."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 10, 10, 0.7)",
        font=dict(family="Inter, sans-serif", color=COLOR_TEXT_SECONDARY, size=11),
        xaxis=dict(
            gridcolor="#1A1A1A",
            zerolinecolor="#1A1A1A",
            showline=True,
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            gridcolor="#1A1A1A",
            zerolinecolor="#1A1A1A",
            showline=True,
            linecolor=COLOR_BORDER,
        ),
        margin=dict(t=20, b=20, l=30, r=20),
        height=height,
        hoverlabel=dict(
            bgcolor=COLOR_CARD,
            bordercolor=COLOR_BORDER,
            font=dict(family="Inter, sans-serif", color=COLOR_TEXT_PRIMARY, size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLOR_TEXT_SECONDARY),
        ),
    )
