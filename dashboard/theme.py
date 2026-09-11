"""
dashboard/theme.py

AI-SNIDS Minimalist Design System & Component Library.
Inspired by Linear, Vercel, and Apple:
- Absolute black (#000000) canvas
- Subtle elevation (#080808 cards, #0D0D0D hover)
- Razor-thin borders (#1A1A1A)
- Monochromatic hierarchy (White / Gray / Muted)
- Single Electric Cyan (#00E5FF) AI accent used with extreme restraint
- Rich, smooth, subtle micro-hover states across all components
- Zero visual noise, zero gratuitous shadows, generous whitespace
"""

# ─── Minimal Color Tokens ──────────────────────────────────────────────────────
COLOR_BLACK = "#000000"             # Absolute black canvas
COLOR_SURFACE = "#050505"           # Secondary surface
COLOR_CARD = "#080808"              # Elevation card
COLOR_CARD_HOVER = "#0D0D0D"        # Hover state
COLOR_BORDER = "#1A1A1A"            # Subtle structural border
COLOR_BORDER_HOVER = "#2A2A2A"      # Interactive border highlight
COLOR_BORDER_SUBTLE = "#141414"     # Divider lines

COLOR_WHITE = "#FFFFFF"             # Primary focal text
COLOR_GRAY = "#888888"              # Secondary text & labels
COLOR_MUTED = "#555555"             # Timestamps & metadata
COLOR_TECH = "#CCCCCC"              # Monospace values

# Single AI Accent (Electric Cyan — restrained)
COLOR_AI_ACCENT = "#00E5FF"

# Minimal Security Severity Tokens (indicators only)
SEV_SAFE = "#22C55E"
SEV_WARN = "#F59E0B"
SEV_THREAT = "#EF4444"
SEV_CRITICAL = "#DC2626"

# Backward compatibility aliases for existing imports
COLOR_BG = COLOR_BLACK
COLOR_BG_SECONDARY = COLOR_SURFACE
COLOR_BG_SIDEBAR = COLOR_BLACK
COLOR_BORDER_SIDEBAR = COLOR_BORDER_SUBTLE
COLOR_AI_PRIMARY = COLOR_AI_ACCENT
COLOR_AI_SECONDARY = "#3B82F6"
COLOR_TEXT_PRIMARY = COLOR_WHITE
COLOR_TEXT_SECONDARY = COLOR_GRAY
COLOR_TEXT_MUTED = COLOR_MUTED
COLOR_TEXT_TECH = COLOR_TECH
SEV_LOW = SEV_SAFE
SEV_MED = SEV_WARN
SEV_HIGH = SEV_THREAT


# ─── Lucide Minimal SVG Icons ──────────────────────────────────────────────────
ICONS = {
    "shield": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    ),
    "shield-check": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="m9 12 2 2 4-4"/></svg>'
    ),
    "network": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/>'
        '<rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/>'
        '<path d="M12 12V8"/></svg>'
    ),
    "cpu": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>'
        '<path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/>'
        '<path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>'
    ),
    "activity": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    ),
    "alert-triangle": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    ),
    "server": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="20" height="8" x="2" y="2" rx="2" ry="2"/>'
        '<rect width="20" height="8" x="2" y="14" rx="2" ry="2"/>'
        '<line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>'
    ),
    "user": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/></svg>'
    ),
    "lock": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
    ),
    "database": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5V19A9 3 0 0 0 21 19V5"/>'
        '<path d="M3 12A9 3 0 0 0 21 12"/></svg>'
    ),
    "ban": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/></svg>'
    ),
    "radar": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/>'
        '<path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/>'
        '<path d="M16.24 7.76A6 6 0 1 0 8.23 16.24"/>'
        '<path d="M12 12h.01"/><path d="m12 12 5-5"/></svg>'
    ),
    "terminal": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/></svg>'
    ),
    "zap": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
    ),
}


def get_icon(name: str, size: int = 14, color: str = COLOR_GRAY) -> str:
    """Return raw inline SVG string for the requested Lucide icon."""
    template = ICONS.get(name, ICONS["shield"])
    return template.format(size=size, color=color)


# ─── Minimalist Global CSS with Rich Hover Effects ─────────────────────────────
GLOBAL_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Design System Tokens */
    :root {{
        --black: {COLOR_BLACK};
        --surface: {COLOR_SURFACE};
        --surface-hover: {COLOR_CARD_HOVER};
        --card: {COLOR_CARD};
        --border: {COLOR_BORDER};
        --border-hover: {COLOR_BORDER_HOVER};
        --border-subtle: {COLOR_BORDER_SUBTLE};
        --white: {COLOR_WHITE};
        --gray: {COLOR_GRAY};
        --muted: {COLOR_MUTED};
        --tech: {COLOR_TECH};
        --ai-accent: {COLOR_AI_ACCENT};
        --success: {SEV_SAFE};
        --warning: {SEV_WARN};
        --danger: {SEV_THREAT};
    }}

    /* Base Reset & Typography */
    html, body, [class*="css"], .stApp {{
        background-color: var(--black) !important;
        color: var(--white) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.012em;
    }}

    header[data-testid="stHeader"] {{
        background-color: var(--black) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }}

    /* Sidebar (Pure Minimal Black with Smooth Nav Hover) */
    [data-testid="stSidebar"] {{
        background-color: var(--black) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background-color: var(--black) !important;
        padding-top: 1.5rem;
    }}

    /* Sidebar Navigation Links */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
        gap: 3px;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        background: transparent;
        border: 1px solid transparent;
        border-left: 2px solid transparent !important;
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        color: var(--gray) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: -0.01em;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border-left: 2px solid rgba(0, 229, 255, 0.5) !important;
        padding-left: 0.95rem !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
        background-color: #111111 !important;
        color: var(--ai-accent) !important;
        font-weight: 600 !important;
        border-left: 2px solid var(--ai-accent) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] input {{
        display: none;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] {{
        margin-left: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] ~ div {{
        display: none;
    }}

    /* Typography Hierarchy */
    h1, h2, h3, h4 {{
        font-family: 'Inter', sans-serif !important;
        color: var(--white) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
    }}

    code, kbd, samp, pre, .mono {{
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--tech);
        font-size: 0.85em;
    }}

    [data-testid="stCodeBlock"] {{
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: border-color 180ms ease, box-shadow 180ms ease !important;
    }}
    [data-testid="stCodeBlock"]:hover {{
        border-color: #333333 !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4) !important;
    }}

    /* Interactive Buttons with Smooth Hover & Micro-Lift */
    .stButton > button, .stDownloadButton > button {{
        background-color: var(--black) !important;
        border: 1px solid #262626 !important;
        color: var(--white) !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 1rem !important;
        box-shadow: none !important;
        cursor: pointer !important;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background-color: #141414 !important;
        border-color: var(--ai-accent) !important;
        color: var(--ai-accent) !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 10px rgba(0, 229, 255, 0.15) !important;
    }}
    .stButton > button:active, .stDownloadButton > button:active {{
        transform: scale(0.98) !important;
    }}

    /* Primary Accent Button */
    .stButton > button[kind="primary"] {{
        background-color: var(--black) !important;
        border: 1px solid var(--ai-accent) !important;
        color: var(--ai-accent) !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: var(--ai-accent) !important;
        border-color: var(--ai-accent) !important;
        color: var(--black) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0, 229, 255, 0.35) !important;
    }}

    /* Metric Cards with Smooth Elevation Hover */
    [data-testid="metric-container"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 0.9rem 1.1rem !important;
        box-shadow: none !important;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: default;
    }}
    [data-testid="metric-container"]:hover {{
        background-color: #0E0E0E !important;
        border-color: #333333 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Inter', sans-serif !important;
        color: var(--white) !important;
        font-weight: 600 !important;
        font-size: 1.45rem !important;
        letter-spacing: -0.03em !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        color: var(--gray) !important;
        text-transform: uppercase !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.04em !important;
        font-weight: 500 !important;
    }}

    /* Dataframe & Tables with Subtle Border Hover */
    [data-testid="stDataFrame"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: border-color 180ms ease !important;
    }}
    [data-testid="stDataFrame"]:hover {{
        border-color: #2E2E2E !important;
    }}

    /* Form Controls: Inputs, Selectboxes with Hover Highlighting */
    [data-testid="stSelectbox"] > div > div {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--white) !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        cursor: pointer !important;
        transition: all 180ms ease !important;
    }}
    [data-testid="stSelectbox"] > div > div:hover {{
        border-color: var(--ai-accent) !important;
        background-color: #080808 !important;
    }}

    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--white) !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        transition: all 180ms ease !important;
    }}
    [data-testid="stTextInput"] input:hover, [data-testid="stNumberInput"] input:hover {{
        border-color: #333333 !important;
    }}
    [data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus {{
        border-color: var(--ai-accent) !important;
        box-shadow: 0 0 8px rgba(0, 229, 255, 0.2) !important;
    }}

    /* Slider Handle Hover */
    [data-testid="stSlider"] div[role="slider"] {{
        transition: transform 150ms ease, box-shadow 150ms ease !important;
        background-color: var(--ai-accent) !important;
    }}
    [data-testid="stSlider"] div[role="slider"]:hover {{
        transform: scale(1.3) !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.5) !important;
    }}

    /* Popover & Menus */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }}
    li[data-baseweb="menu-item"] {{
        color: var(--gray) !important;
        font-size: 0.82rem !important;
        transition: background-color 100ms ease, color 100ms ease !important;
    }}
    li[data-baseweb="menu-item"]:hover {{
        background-color: var(--surface-hover) !important;
        color: var(--ai-accent) !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: all 180ms ease !important;
    }}
    [data-testid="stExpander"]:hover {{
        border-color: #333333 !important;
        background-color: #0A0A0A !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        color: var(--white) !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 5px;
        height: 5px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--black);
    }}
    ::-webkit-scrollbar-thumb {{
        background: #202020;
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #333333;
    }}

    /* Reusable Cards with Micro-Lift Hover */
    .min-card, .soc-card {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem 1.15rem;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .min-card:hover, .soc-card:hover {{
        background-color: #0E0E0E !important;
        border-color: #333333 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
    }}

    /* Threat Cards Hover */
    .soc-card-threat:hover {{
        border-color: rgba(239, 68, 68, 0.5) !important;
        background-color: #0E0E0E !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.15) !important;
        transform: translateY(-2px);
    }}

    /* Scenario Selection Cards Hover */
    .soc-scenario-card {{
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer;
    }}
    .soc-scenario-card:hover {{
        background-color: #0E0E0E !important;
        border-color: var(--ai-accent) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(0, 229, 255, 0.18) !important;
    }}

    /* Network Topology Nodes with Hover Glow */
    .soc-node {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.9rem;
        text-align: center;
        cursor: default;
        transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .soc-node:hover {{
        background-color: #0E0E0E !important;
        border-color: var(--ai-accent) !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 229, 255, 0.18) !important;
    }}
    .soc-node-threat:hover {{
        border-color: var(--danger) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.25) !important;
        transform: translateY(-3px);
    }}

    /* Flow Features Pills Hover */
    .soc-feat-pill {{
        transition: all 150ms ease !important;
        cursor: default;
    }}
    .soc-feat-pill:hover {{
        background-color: #121212 !important;
        border-color: #333333 !important;
        transform: translateY(-1px);
    }}

    /* Status Badges Hover */
    .soc-badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        transition: all 150ms ease !important;
        cursor: default;
    }}
    .soc-badge:hover {{
        filter: brightness(1.25);
        transform: scale(1.04);
    }}

    /* Status Dots Hover */
    .status-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
        transition: transform 150ms ease !important;
    }}
    .status-dot:hover {{
        transform: scale(1.4);
    }}

    .dot-cyan {{ background-color: var(--ai-accent); }}
    .dot-green {{ background-color: var(--success); }}
    .dot-amber {{ background-color: var(--warning); }}
    .dot-red {{ background-color: var(--danger); }}

    .pulse-indicator {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }}

    /* Sidebar Status Item Hover */
    .sidebar-status-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.25rem 0.4rem;
        border-radius: 4px;
        transition: background-color 150ms ease;
    }}
    .sidebar-status-row:hover {{
        background-color: #0F0F0F;
    }}

    /* Image Container Hover */
    [data-testid="stImage"] img {{
        border-radius: 6px;
        border: 1px solid var(--border);
        transition: all 180ms ease !important;
    }}
    [data-testid="stImage"] img:hover {{
        border-color: #333333 !important;
        transform: translateY(-2px);
    }}
</style>
"""


# ─── Minimal Reusable Components ───────────────────────────────────────────────

def render_section_header(title: str, subtitle: str = None, category: str = None, icon_name: str = "shield") -> str:
    """Minimal section header with clean typography and subtle gray metadata."""
    category_html = (
        f'<div style="font-size:0.65rem; font-weight:500; letter-spacing:0.04em; '
        f'color:{COLOR_GRAY}; text-transform:uppercase; margin-bottom:0.15rem;">'
        f'{category}</div>'
    ) if category else ""

    sub_html = (
        f'<div style="color:{COLOR_GRAY}; font-size:0.8rem; margin-top:0.2rem;">'
        f'{subtitle}</div>'
    ) if subtitle else ""

    icon_svg = get_icon(icon_name, size=15, color=COLOR_GRAY)

    return f"""
    <div style="margin: 1.25rem 0 0.75rem 0;">
        {category_html}
        <div style="display:flex; align-items:center; gap:0.45rem;">
            {icon_svg}
            <h3 style="margin:0; font-size:1.05rem; font-weight:600; color:{COLOR_WHITE};">{title}</h3>
        </div>
        {sub_html}
    </div>
    """


def render_metric_card(label: str, value: str, subtitle: str = None, status_color: str = None) -> str:
    """Minimal Linear-style KPI card with small status dot, subtle borders, and smooth hover elevation."""
    dot_html = (
        f'<span class="status-dot" style="background-color:{status_color}; margin-right:6px;"></span>'
    ) if status_color else ""

    sub_html = (
        f'<div style="color:{COLOR_MUTED}; font-size:0.7rem; margin-top:0.3rem;">{subtitle}</div>'
    ) if subtitle else ""

    return f"""
    <div class="soc-card" style="padding:0.9rem 1.1rem; margin-bottom:0.4rem;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <span style="color:{COLOR_GRAY}; font-size:0.68rem; font-weight:500; letter-spacing:0.03em; text-transform:uppercase;">
                {label}
            </span>
            <div>{dot_html}</div>
        </div>
        <div style="font-size:1.45rem; font-weight:600; color:{COLOR_WHITE}; margin-top:0.25rem; letter-spacing:-0.03em;">
            {value}
        </div>
        {sub_html}
    </div>
    """


def render_severity_badge(level: str) -> str:
    """Render a minimal severity indicator (small pill with subtle border and text) with hover brightness."""
    lvl = str(level).upper().strip()
    color_map = {
        "LOW": (SEV_SAFE, "rgba(34, 197, 94, 0.08)", "rgba(34, 197, 94, 0.2)"),
        "BENIGN": (SEV_SAFE, "rgba(34, 197, 94, 0.08)", "rgba(34, 197, 94, 0.2)"),
        "NORMAL": (SEV_SAFE, "rgba(34, 197, 94, 0.08)", "rgba(34, 197, 94, 0.2)"),
        "SAFE": (SEV_SAFE, "rgba(34, 197, 94, 0.08)", "rgba(34, 197, 94, 0.2)"),
        "ALLOW": (SEV_SAFE, "rgba(34, 197, 94, 0.08)", "rgba(34, 197, 94, 0.2)"),
        "MONITOR": (COLOR_AI_ACCENT, "rgba(0, 229, 255, 0.06)", "rgba(0, 229, 255, 0.2)"),
        "LOG": (COLOR_AI_ACCENT, "rgba(0, 229, 255, 0.06)", "rgba(0, 229, 255, 0.2)"),
        "MEDIUM": (SEV_WARN, "rgba(245, 158, 11, 0.08)", "rgba(245, 158, 11, 0.2)"),
        "WARNING": (SEV_WARN, "rgba(245, 158, 11, 0.08)", "rgba(245, 158, 11, 0.2)"),
        "ALERT": (SEV_WARN, "rgba(245, 158, 11, 0.08)", "rgba(245, 158, 11, 0.2)"),
        "HIGH": (SEV_THREAT, "rgba(239, 68, 68, 0.08)", "rgba(239, 68, 68, 0.25)"),
        "CRITICAL": (SEV_CRITICAL, "rgba(220, 38, 38, 0.1)", "rgba(220, 38, 38, 0.3)"),
        "BLOCK": (SEV_CRITICAL, "rgba(220, 38, 38, 0.1)", "rgba(220, 38, 38, 0.3)"),
        "BLOCKED": (SEV_THREAT, "rgba(239, 68, 68, 0.08)", "rgba(239, 68, 68, 0.25)"),
    }
    fg, bg, border = color_map.get(lvl, (COLOR_GRAY, "rgba(136, 136, 136, 0.06)", "rgba(136, 136, 136, 0.15)"))

    return (
        f'<span class="soc-badge" style="color:{fg}; background:{bg}; border:1px solid {border};">'
        f'{lvl}</span>'
    )


def render_network_node(name: str, ip: str, role: str, status: str, is_threat: bool = False) -> str:
    """Render a minimal network node card with subtle border highlight and lift on hover."""
    accent_color = SEV_THREAT if is_threat else (COLOR_AI_ACCENT if "Client" in name or "Router" in name else COLOR_WHITE)
    status_color = SEV_CRITICAL if "BLOCK" in status.upper() else (SEV_THREAT if is_threat else SEV_SAFE)
    icon_name = "alert-triangle" if is_threat else ("server" if "Server" in name or "Router" in name else "user")
    icon_svg = get_icon(icon_name, size=16, color=accent_color)
    card_class = "soc-node soc-node-threat" if is_threat else "soc-node"

    return f"""
    <div class="{card_class}">
        <div style="display:flex; justify-content:center; margin-bottom:0.35rem;">{icon_svg}</div>
        <div style="font-weight:600; font-size:0.86rem; color:{COLOR_WHITE};">{name}</div>
        <div class="mono" style="font-size:0.75rem; color:{COLOR_TECH}; margin:0.15rem 0;">{ip}</div>
        <div style="font-size:0.68rem; color:{COLOR_MUTED};">{role}</div>
        <div style="margin-top:0.35rem;">
            <span class="soc-badge" style="color:{status_color}; background:transparent; border:1px solid {status_color}30;">
                {status}
            </span>
        </div>
    </div>
    """


def get_plotly_soc_layout(height: int = 240) -> dict:
    """Standardized minimal Plotly layout: pure black, subtle #141414 grid, minimal typography."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLOR_GRAY, size=10),
        xaxis=dict(
            gridcolor="#141414",
            zerolinecolor="#141414",
            showline=False,
            tickfont=dict(size=9, color=COLOR_MUTED),
        ),
        yaxis=dict(
            gridcolor="#141414",
            zerolinecolor="#141414",
            showline=False,
            tickfont=dict(size=9, color=COLOR_MUTED),
        ),
        margin=dict(t=15, b=20, l=30, r=15),
        height=height,
        hoverlabel=dict(
            bgcolor=COLOR_CARD,
            bordercolor=COLOR_BORDER,
            font=dict(family="Inter, sans-serif", color=COLOR_WHITE, size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLOR_GRAY),
        ),
    )
