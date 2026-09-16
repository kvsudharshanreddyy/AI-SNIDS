"""
dashboard/theme.py

AI-SNIDS Global Minimalist Visual Design System & Component Library.
Strictly Black-First (#000000), Linear/Vercel-inspired:
- Absolute black (#000000) canvas
- Subtle elevation surfaces (#050505 secondary, #080808 cards)
- Subtle hover states (#0D0D0D, 150-250ms transitions)
- Razor-thin structural borders (#1A1A1A, hover #262626)
- Monochromatic text hierarchy: #FFFFFF (Primary), #A1A1AA (Secondary), #71717A (Muted)
- Monospace values: #D4D4D8 (JetBrains Mono)
- Restrained Electric Cyan (#00E5FF) AI accent for active/selected/intelligence
- Security states: Green (#22C55E), Amber (#F59E0B), Red (#EF4444) strictly on small indicators
- Zero gratuitous glows, zero gradient backgrounds, zero visual clutter
"""

# ─── Global Minimalist Color Tokens ─────────────────────────────────────────────
COLOR_BLACK = "#000000"             # Main background (Absolute black)
COLOR_SURFACE = "#050505"           # Secondary surface
COLOR_SURFACE_HOVER = "#0D0D0D"     # Hover state
COLOR_CARD = "#080808"              # Elevation card surface
COLOR_CARD_HOVER = "#0D0D0D"        # Card hover surface
COLOR_BORDER = "#1A1A1A"            # Structural border
COLOR_BORDER_HOVER = "#262626"      # Interactive border highlight
COLOR_BORDER_SUBTLE = "#121212"     # Subtle dividers

COLOR_WHITE = "#FFFFFF"             # Primary focal text & headers
COLOR_GRAY = "#A1A1AA"              # Secondary text & labels (Zinc 400)
COLOR_MUTED = "#71717A"             # Timestamps & metadata (Zinc 500)
COLOR_TECH = "#D4D4D8"              # Monospace values & technical telemetry (Zinc 300)

# Single AI Accent (Electric Cyan — restrained)
COLOR_AI_ACCENT = "#00E5FF"
COLOR_AI_SECONDARY = "#3B82F6"

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
COLOR_TEXT_PRIMARY = COLOR_WHITE
COLOR_TEXT_SECONDARY = COLOR_GRAY
COLOR_TEXT_MUTED = COLOR_MUTED
COLOR_TEXT_TECH = COLOR_TECH
SEV_LOW = SEV_SAFE
SEV_MED = SEV_WARN
SEV_HIGH = SEV_THREAT


# ─── Lucide Minimal SVG Vector Icons ───────────────────────────────────────────
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


# ─── Minimalist Global CSS: Black-First, Linear-Inspired ───────────────────────
GLOBAL_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Design System CSS Tokens */
    :root {{
        --background: {COLOR_BLACK};
        --surface: {COLOR_SURFACE};
        --surface-hover: {COLOR_SURFACE_HOVER};
        --card: {COLOR_CARD};
        --card-hover: {COLOR_CARD_HOVER};
        --border: {COLOR_BORDER};
        --border-hover: {COLOR_BORDER_HOVER};
        --border-subtle: {COLOR_BORDER_SUBTLE};
        --text-primary: {COLOR_WHITE};
        --text-secondary: {COLOR_GRAY};
        --text-muted: {COLOR_MUTED};
        --text-tech: {COLOR_TECH};
        --ai-accent: {COLOR_AI_ACCENT};
        --ai-secondary: {COLOR_AI_SECONDARY};
        --success: {SEV_SAFE};
        --warning: {SEV_WARN};
        --danger: {SEV_THREAT};
        --critical: {SEV_CRITICAL};
    }}

    /* Base Reset: Absolute Black Canvas & Typography */
    html, body, [class*="css"], .stApp {{
        background-color: var(--background) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.012em;
    }}

    header[data-testid="stHeader"] {{
        background-color: var(--background) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }}

    /* Main Content Container Padding & Spacing */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }}

    /* Sidebar: Pure Minimal Black (#000000) */
    [data-testid="stSidebar"] {{
        background-color: var(--background) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background-color: var(--background) !important;
        padding-top: 1.25rem;
    }}

    /* Sidebar Navigation Radio Options (Linear-Style Links) */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
        gap: 2px;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        background: transparent;
        border: 1px solid transparent;
        border-left: 2px solid transparent !important;
        padding: 0.45rem 0.75rem;
        border-radius: 6px;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: -0.01em;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background-color: var(--surface-hover) !important;
        color: var(--text-primary) !important;
        border-left: 2px solid rgba(0, 229, 255, 0.4) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
        background-color: var(--surface-hover) !important;
        color: var(--text-primary) !important;
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
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
    }}

    code, kbd, samp, pre, .mono {{
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-tech);
        font-size: 0.85em;
    }}

    [data-testid="stCodeBlock"] {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: border-color 180ms ease !important;
    }}
    [data-testid="stCodeBlock"]:hover {{
        border-color: var(--border-hover) !important;
    }}

    /* Minimalist Buttons: Black-First, White/Cyan Hover */
    .stButton > button, .stDownloadButton > button {{
        background-color: var(--background) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
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
        background-color: #FFFFFF !important;
        border-color: #FFFFFF !important;
        color: #000000 !important;
        transform: translateY(-1px);
    }}
    .stButton > button:active, .stDownloadButton > button:active {{
        transform: scale(0.98) !important;
    }}

    /* Primary Accent Button: Restrained Cyan */
    .stButton > button[kind="primary"] {{
        background-color: var(--background) !important;
        border: 1px solid var(--ai-accent) !important;
        color: var(--ai-accent) !important;
        font-weight: 600 !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: var(--ai-accent) !important;
        border-color: var(--ai-accent) !important;
        color: var(--background) !important;
        transform: translateY(-1px);
    }}

    /* Danger Button (when specified) */
    .btn-danger button, button.btn-danger {{
        background-color: var(--background) !important;
        border: 1px solid var(--danger) !important;
        color: var(--danger) !important;
    }}
    .btn-danger button:hover, button.btn-danger:hover {{
        background-color: var(--danger) !important;
        border-color: var(--danger) !important;
        color: #FFFFFF !important;
    }}

    /* Metric Cards: Pure Minimalist #080808, Razor Border #1A1A1A */
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
        background-color: var(--card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 1.45rem !important;
        letter-spacing: -0.03em !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.04em !important;
        font-weight: 500 !important;
    }}

    /* Dataframe & Tables: Clean Monochrome */
    [data-testid="stDataFrame"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: border-color 180ms ease !important;
    }}
    [data-testid="stDataFrame"]:hover {{
        border-color: var(--border-hover) !important;
    }}

    /* Form Controls: Inputs, Selectboxes */
    [data-testid="stSelectbox"] > div > div {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        cursor: pointer !important;
        transition: all 180ms ease !important;
    }}
    [data-testid="stSelectbox"] > div > div:hover {{
        border-color: var(--ai-accent) !important;
        background-color: var(--card) !important;
    }}

    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        transition: all 180ms ease !important;
    }}
    [data-testid="stTextInput"] input:hover, [data-testid="stNumberInput"] input:hover {{
        border-color: var(--border-hover) !important;
    }}
    [data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus {{
        border-color: var(--ai-accent) !important;
        box-shadow: none !important;
    }}

    /* Slider Minimalist */
    [data-testid="stSlider"] div[role="slider"] {{
        background-color: var(--ai-accent) !important;
        transition: transform 150ms ease !important;
        box-shadow: none !important;
    }}
    [data-testid="stSlider"] div[role="slider"]:hover {{
        transform: scale(1.2) !important;
    }}

    /* Popover & Menus */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }}
    li[data-baseweb="menu-item"] {{
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        transition: background-color 100ms ease, color 100ms ease !important;
    }}
    li[data-baseweb="menu-item"]:hover {{
        background-color: var(--surface-hover) !important;
        color: var(--text-primary) !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: border-color 180ms ease !important;
    }}
    [data-testid="stExpander"]:hover {{
        border-color: var(--border-hover) !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        color: var(--text-primary) !important;
    }}

    /* Native Modal Dialog: Pure Minimalist Dark Container */
    div[role="dialog"] {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        box-shadow: 0 16px 32px rgba(0, 0, 0, 0.9) !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 5px;
        height: 5px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--background);
    }}
    ::-webkit-scrollbar-thumb {{
        background: #1C1C1C;
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #2E2E2E;
    }}

    /* Toast Notification: Minimalist Dark Container, No Neon Halo */
    [data-testid="stToast"] {{
        min-width: 480px !important;
        max-width: 600px !important;
        width: auto !important;
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-left: 3px solid var(--ai-accent) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.8) !important;
        border-radius: 6px !important;
        padding: 1rem 1.25rem !important;
    }}
    [data-testid="stToast"] div {{
        white-space: normal !important;
        word-break: break-word !important;
        font-size: 0.84rem !important;
        line-height: 1.55 !important;
        color: var(--text-primary) !important;
    }}

    /* Reusable Cards: Linear Elevation */
    .min-card, .soc-card {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem 1.15rem;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .min-card:hover, .soc-card:hover {{
        background-color: var(--card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px);
    }}

    /* Threat Cards Hover */
    .soc-card-threat:hover {{
        border-color: rgba(239, 68, 68, 0.35) !important;
        background-color: var(--card-hover) !important;
        transform: translateY(-1px);
    }}

    /* Scenario Selection Cards */
    .soc-scenario-card {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer;
    }}
    .soc-scenario-card:hover {{
        background-color: var(--card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px);
    }}
    .soc-scenario-card-selected {{
        border: 1px solid var(--ai-accent) !important;
        background-color: rgba(0, 229, 255, 0.03) !important;
    }}

    /* Network Topology Nodes */
    .soc-node {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.9rem;
        text-align: center;
        cursor: default;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .soc-node:hover {{
        background-color: var(--card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px);
    }}
    .soc-node-threat:hover {{
        border-color: rgba(239, 68, 68, 0.4) !important;
    }}

    /* Flow Features Pills */
    .soc-feat-pill {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 4px;
        transition: all 150ms ease !important;
        cursor: default;
    }}
    .soc-feat-pill:hover {{
        background-color: var(--card-hover) !important;
        border-color: var(--border-hover) !important;
    }}

    /* Status Badges: Small, Restrained Security Indicators */
    .soc-badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        transition: all 150ms ease !important;
        cursor: default;
    }}
    .soc-badge:hover {{
        filter: brightness(1.2);
    }}

    /* Minimalist Status Dots */
    .status-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
        transition: transform 150ms ease !important;
    }}
    .status-dot:hover {{
        transform: scale(1.3);
    }}

    .dot-cyan {{ background-color: var(--ai-accent); }}
    .dot-green {{ background-color: var(--success); }}
    .dot-amber {{ background-color: var(--warning); }}
    .dot-red {{ background-color: var(--danger); }}

    /* Sidebar Status Item Row */
    .sidebar-status-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.25rem 0.4rem;
        border-radius: 4px;
        transition: background-color 150ms ease;
    }}
    .sidebar-status-row:hover {{
        background-color: var(--surface-hover);
    }}

    /* Image Container */
    [data-testid="stImage"] img {{
        border-radius: 6px;
        border: 1px solid var(--border);
        transition: border-color 180ms ease !important;
    }}
    [data-testid="stImage"] img:hover {{
        border-color: var(--border-hover) !important;
    }}

    /* Attack Intelligence Pop Message Container (Minimalist Black Card) */
    .soc-pop-alert {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1.15rem 1.25rem;
        margin: 0.75rem 0 1.25rem 0;
        transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
        animation: fadeIn 200ms ease-out;
    }}
    .soc-pop-alert:hover {{
        background-color: var(--card-hover) !important;
        border-color: var(--border-hover) !important;
    }}
    .soc-pop-alert-threat {{
        border-left: 3px solid var(--danger) !important;
    }}
    .soc-pop-alert-safe {{
        border-left: 3px solid var(--success) !important;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-3px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
</style>
"""


# ─── Minimal Reusable Components ───────────────────────────────────────────────

def render_section_header(title: str, subtitle: str = None, category: str = None, icon_name: str = "shield") -> str:
    """Minimal section header with clean typography and subtle gray metadata."""
    category_html = (
        f'<div style="font-size:0.65rem; font-weight:500; letter-spacing:0.04em; '
        f'color:{COLOR_MUTED}; text-transform:uppercase; margin-bottom:0.15rem;">'
        f'{category}</div>'
    ) if category else ""

    sub_html = (
        f'<div style="color:{COLOR_GRAY}; font-size:0.8rem; margin-top:0.2rem;">'
        f'{subtitle}</div>'
    ) if subtitle else ""

    icon_svg = get_icon(icon_name, size=15, color=COLOR_MUTED)

    return f"""
    <div style="margin: 1.25rem 0 0.75rem 0;">
        {category_html}
        <div style="display:flex; align-items:center; gap:0.45rem;">
            {icon_svg}
            <h3 style="margin:0; font-size:1.05rem; font-weight:600; color:{COLOR_WHITE}; letter-spacing:-0.02em;">{title}</h3>
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
            <span style="color:{COLOR_MUTED}; font-size:0.68rem; font-weight:500; letter-spacing:0.03em; text-transform:uppercase;">
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
    fg, bg, border = color_map.get(lvl, (COLOR_GRAY, "rgba(161, 161, 170, 0.06)", "rgba(161, 161, 170, 0.15)"))

    return (
        f'<span class="soc-badge" style="color:{fg}; background:{bg}; border:1px solid {border};">'
        f'{lvl}</span>'
    )


def render_network_node(name: str, ip: str, role: str, status: str, is_threat: bool = False) -> str:
    """Render a minimal network node card with subtle border highlight on hover."""
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
    """Standardized minimal Plotly layout: absolute black, subtle #141414 grid, Inter typography."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLOR_MUTED, size=10),
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


# ─── Attack Intelligence & Explanations ─────────────────────────────────────────

ATTACK_INTELLIGENCE = {
    "Port Scan": {
        "title": "Port Scanning Reconnaissance",
        "icon": "radar",
        "category": "Reconnaissance (MITRE ATT&CK T1046)",
        "what_kind": "Automated sequential TCP service probe scanning across multiple listening daemons to identify open network gates without completing standard 3-way handshakes.",
        "how_it_got": "The adversary at host 10.0.0.50 routed through the gateway (10.0.0.1) directly to Server B (10.0.0.100), dispatching a rapid burst of TCP SYN packets across 13 ports (21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3389, 8080) with micro flow duration (<50µs) and zero response payload.",
        "why": "Initial Cyber Kill Chain discovery. The attacker maps active operating system daemons and unpatched network services to identify exploitable entry points before launching targeted payloads.",
        "danger": "Exposes vulnerable service versions, management portals, and internal host architecture to the adversary.",
        "ai_detection": "Random Forest flagged extreme Flow Packets/s, zero backward packets, and short flow duration with 99.8% confidence.",
        "mitigation": "Automated Perimeter Defense: Ingress traffic from 10.0.0.50 dropped immediately; source IP quarantined.",
        "severity": "HIGH",
    },
    "DoS": {
        "title": "Denial of Service (Volumetric Flood)",
        "icon": "activity",
        "category": "Impact & Availability Disruption (MITRE ATT&CK T1498)",
        "what_kind": "Single-source volumetric TCP flood designed to exhaust server processing capacity, socket backlogs, and memory buffers.",
        "how_it_got": "Host 10.0.0.50 opened an aggressive, unthrottled packet stream directly into Server B's HTTP port (80) with minimal inter-arrival times (<10µs), filling the server's TCP connection backlog and starving CPU worker threads.",
        "why": "Resource exhaustion attack aimed at rendering Server B totally unresponsive to legitimate users (Client A at 10.0.0.10), causing critical application downtime.",
        "danger": "Total service blackout, dropped customer sessions, and server operating system kernel panic.",
        "ai_detection": "Extreme Flow Packets/s combined with near-zero Flow Inter-Arrival Times (IAT Min/Mean) and concentrated target IP/port.",
        "mitigation": "Rate-limiting activated: Source IP isolated; stateful connection drop applied at the gateway router.",
        "severity": "CRITICAL",
    },
    "DDoS": {
        "title": "Distributed Denial of Service (Botnet Swarm)",
        "icon": "zap",
        "category": "Distributed Infrastructure Disruption (MITRE ATT&CK T1498.001)",
        "what_kind": "Coordinated multi-origin volumetric flood launched simultaneously from a synchronized botnet swarm of compromised hosts.",
        "how_it_got": "6 coordinated botnet IP addresses (10.0.0.51 through 10.0.0.56) converged their attacks simultaneously on Server B (10.0.0.100) Port 80, flooding the gateway router and saturating link bandwidth while evading single-IP rate limits.",
        "why": "Engineered to overwhelm upstream perimeter routers and bring down mission-critical server infrastructure with aggregate volumetric traffic that cannot be blocked by single-source rules.",
        "danger": "Catastrophic network perimeter congestion, gateway buffer overruns, and multi-tenant service failure.",
        "ai_detection": "Correlated flow bursts exhibiting synchronized inter-arrival rates across distinct source IPs targeting port 80.",
        "mitigation": "Subnet-wide perimeter defense: Distributed drop policies activated; all identified botnet nodes blocked simultaneously.",
        "severity": "CRITICAL",
    },
    "Brute Force": {
        "title": "Authentication Brute Force (Credential Abuse)",
        "icon": "lock",
        "category": "Credential Access (MITRE ATT&CK T1110)",
        "what_kind": "Automated high-velocity dictionary attack attempting to guess administrative credentials against remote access daemons.",
        "how_it_got": "Adversary host 10.0.0.50 connected across the virtual network to Server B (10.0.0.100), bombarding Port 22 (SSH) and Port 21 (FTP) with automated credential dictionary attempts using rapid short-lived TCP connection cycles.",
        "why": "Credential guessing / password spraying to obtain unauthorized root or administrative shell credentials and seize total system control.",
        "danger": "Unauthorized system takeover, data exfiltration, and internal lateral movement across enterprise subnets.",
        "ai_detection": "Repetitive short-lived TCP sessions targeting authentication ports with identical packet lengths and failure rates.",
        "mitigation": "Adaptive fail2ban lockout: Host IP 10.0.0.50 blocked on all administrative ports immediately.",
        "severity": "HIGH",
    },
    "Suspicious Traffic": {
        "title": "Anomalous Traffic (Stealth Jitter / Evasion Probe)",
        "icon": "alert-triangle",
        "category": "Defense Evasion (MITRE ATT&CK T1027)",
        "what_kind": "Obfuscated network flow incorporating artificial timing delays (jitter) and mixed protocol behavior designed to evade static rule-based thresholds.",
        "how_it_got": "Host 10.0.0.50 injected artificial timing delays (varying between 50ms and 500ms) between probe packets directed at ports 80 and 443, blending benign web browsing requests with non-standard packet sizes to stay under static threshold alarms.",
        "why": "To test detection threshold boundaries, establish a low-and-slow command & control (C2) channel, or stage covert data exfiltration without tripping threshold firewalls.",
        "danger": "Covert reconnaissance, persistence testing, and silent exfiltration evasion.",
        "ai_detection": "Feature anomaly: Statistical variance in Flow IAT Std and Max Packet Length deviating significantly from standard benign clusters.",
        "mitigation": "Flow tagged for deep inspection; origin placed under heightened continuous behavioral monitoring.",
        "severity": "MEDIUM",
    },
    "BENIGN": {
        "title": "Legitimate Traffic (Standard Flow)",
        "icon": "shield-check",
        "category": "Normal Operational Baseline",
        "what_kind": "Authorized enterprise application communication adhering strictly to RFC TCP protocol standards.",
        "how_it_got": "Standard three-way TCP handshake (SYN, SYN-ACK, ACK) initiated by authorized Client A (10.0.0.10) to Server B (10.0.0.100) on Port 80/443 with normal balanced packet exchanges.",
        "why": "Standard day-to-day enterprise operations conforming to standard TCP three-way handshakes and valid protocol payloads.",
        "danger": "None — fully authenticated and normal operational telemetry.",
        "ai_detection": "Flow characteristics align precisely with baseline training distribution (balanced packet ratios, normal IAT).",
        "mitigation": "Unrestricted routing: Traffic permitted through the network with continuous telemetry logging.",
        "severity": "SAFE",
    },
    "Normal Traffic": {
        "title": "Legitimate Traffic (Standard Flow)",
        "icon": "shield-check",
        "category": "Normal Operational Baseline",
        "what_kind": "Authorized enterprise application communication adhering strictly to RFC TCP protocol standards.",
        "how_it_got": "Standard three-way TCP handshake (SYN, SYN-ACK, ACK) initiated by authorized Client A (10.0.0.10) to Server B (10.0.0.100) on Port 80/443 with normal balanced packet exchanges.",
        "why": "Standard day-to-day enterprise operations conforming to standard TCP three-way handshakes and valid protocol payloads.",
        "danger": "None — fully authenticated and normal operational telemetry.",
        "ai_detection": "Flow characteristics align precisely with baseline training distribution (balanced packet ratios, normal IAT).",
        "mitigation": "Unrestricted routing: Traffic permitted through the network with continuous telemetry logging.",
        "severity": "SAFE",
    },
    "Normal": {
        "title": "Legitimate Traffic (Standard Flow)",
        "icon": "shield-check",
        "category": "Normal Operational Baseline",
        "what_kind": "Authorized enterprise application communication adhering strictly to RFC TCP protocol standards.",
        "how_it_got": "Standard three-way TCP handshake (SYN, SYN-ACK, ACK) initiated by authorized Client A (10.0.0.10) to Server B (10.0.0.100) on Port 80/443 with normal balanced packet exchanges.",
        "why": "Standard day-to-day enterprise operations conforming to standard TCP three-way handshakes and valid protocol payloads.",
        "danger": "None — fully authenticated and normal operational telemetry.",
        "ai_detection": "Flow characteristics align precisely with baseline training distribution (balanced packet ratios, normal IAT).",
        "mitigation": "Unrestricted routing: Traffic permitted through the network with continuous telemetry logging.",
        "severity": "SAFE",
    },
}

ATTACK_INTELLIGENCE["PortScan"] = ATTACK_INTELLIGENCE["Port Scan"]
ATTACK_INTELLIGENCE["BruteForce"] = ATTACK_INTELLIGENCE["Brute Force"]
ATTACK_INTELLIGENCE["Botnet"] = ATTACK_INTELLIGENCE["DDoS"]


def get_attack_intel(attack_type: str) -> dict:
    """Retrieve structured attack intelligence with resilient fallback and normalization."""
    if not attack_type:
        return ATTACK_INTELLIGENCE["Suspicious Traffic"]
    norm = str(attack_type).strip()
    if norm in ATTACK_INTELLIGENCE:
        return ATTACK_INTELLIGENCE[norm]
    up = norm.upper()
    if "BENIGN" in up or "NORMAL" in up:
        return ATTACK_INTELLIGENCE["BENIGN"]
    if "PORT" in up:
        return ATTACK_INTELLIGENCE["Port Scan"]
    if "BRUTE" in up:
        return ATTACK_INTELLIGENCE["Brute Force"]
    if "DDOS" in up or "BOTNET" in up:
        return ATTACK_INTELLIGENCE["DDoS"]
    if "DOS" in up:
        return ATTACK_INTELLIGENCE["DoS"]
    if "SUSPICIOUS" in up or "JITTER" in up or "EVASION" in up:
        return ATTACK_INTELLIGENCE["Suspicious Traffic"]
    return ATTACK_INTELLIGENCE["Suspicious Traffic"]


def render_attack_pop_message(
    attack_type: str,
    source_ip: str,
    destination_ip: str,
    confidence: float,
    risk_level: str,
    action: str,
    is_injected: bool = False,
    extra_note: str = None,
) -> str:
    """Render a clean, high-contrast, minimalist threat intelligence pop message card."""
    norm_type = attack_type.strip()
    if "BENIGN" in norm_type.upper() or "NORMAL" in norm_type.upper():
        norm_type = "BENIGN"
    elif "PORT" in norm_type.upper():
        norm_type = "Port Scan"
    elif "BRUTE" in norm_type.upper():
        norm_type = "Brute Force"
    elif "DDOS" in norm_type.upper():
        norm_type = "DDoS"
    elif "DOS" in norm_type.upper():
        norm_type = "DoS"
    elif "SUSPICIOUS" in norm_type.upper():
        norm_type = "Suspicious Traffic"

    intel = ATTACK_INTELLIGENCE.get(norm_type, ATTACK_INTELLIGENCE["Suspicious Traffic"])
    is_safe = (norm_type == "BENIGN")

    card_class = "soc-pop-alert soc-pop-alert-safe" if is_safe else "soc-pop-alert soc-pop-alert-threat"
    dot_class = "dot-green" if is_safe else ("dot-amber" if norm_type == "Suspicious Traffic" else "dot-red")
    icon_svg = get_icon(intel["icon"], size=18, color=SEV_SAFE if is_safe else (SEV_WARN if norm_type == "Suspicious Traffic" else SEV_THREAT))

    if is_injected:
        banner_text = "SUDDEN MID-STREAM INJECTION · ATTACK ACTIVE"
    elif not is_safe:
        banner_text = "THREAT INTELLIGENCE POPUP · ACTIVE INCIDENT DETECTED"
    else:
        banner_text = "TELEMETRY POPUP · VERIFIED BENIGN FLOW"

    action_color = SEV_SAFE if action in ["ALLOW", "MONITOR"] else SEV_THREAT
    action_bg = "rgba(34, 197, 94, 0.08)" if action in ["ALLOW", "MONITOR"] else "rgba(239, 68, 68, 0.08)"

    note_html = (
        f'<div style="margin-top:0.5rem; padding:0.4rem 0.6rem; background:#0D0D0D; border-left:2px solid {COLOR_AI_ACCENT}; font-size:0.73rem; color:{COLOR_GRAY};">'
        f'{extra_note}</div>'
    ) if extra_note else ""

    if is_safe:
        body_grid = f"""
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; margin:0.75rem 0; background:#050505; border:1px solid #141414; border-radius:6px; padding:0.85rem;">
            <div>
                <div style="font-size:0.68rem; font-weight:600; color:{SEV_SAFE}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.25rem;">
                    TRAFFIC PROFILE
                </div>
                <div style="font-size:0.77rem; color:#D4D4D8; line-height:1.45;">
                    {intel['what_kind']}
                </div>
            </div>
            <div>
                <div style="font-size:0.68rem; font-weight:600; color:{COLOR_AI_ACCENT}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.25rem;">
                    OPERATIONAL PURPOSE
                </div>
                <div style="font-size:0.77rem; color:#D4D4D8; line-height:1.45;">
                    {intel['why']}
                </div>
            </div>
        </div>
        """
    else:
        body_grid = f"""
        <div style="display:flex; flex-direction:column; gap:0.6rem; margin:0.75rem 0; background:#050505; border:1px solid #141414; border-radius:6px; padding:0.85rem;">
            <div>
                <div style="font-size:0.68rem; font-weight:600; color:{COLOR_AI_ACCENT}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.2rem;">
                    WHAT KIND OF ATTACK IS THIS?
                </div>
                <div style="font-size:0.77rem; color:#FFFFFF; line-height:1.4;">
                    {intel['what_kind']}
                </div>
            </div>
            <div style="border-top:1px solid #141414; padding-top:0.5rem;">
                <div style="font-size:0.68rem; font-weight:600; color:{COLOR_TECH}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.2rem;">
                    HOW IT GOT IN / HOW IT WAS EXECUTED:
                </div>
                <div style="font-size:0.77rem; color:#D4D4D8; line-height:1.4;">
                    {intel['how_it_got']}
                </div>
            </div>
            <div style="border-top:1px solid #141414; padding-top:0.5rem;">
                <div style="font-size:0.68rem; font-weight:600; color:{SEV_WARN}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.2rem;">
                    WHY IT HAPPENED & ADVERSARY INTENT:
                </div>
                <div style="font-size:0.77rem; color:#D4D4D8; line-height:1.4;">
                    {intel['why']} <span style="color:#EF4444;">({intel['danger']})</span>
                </div>
            </div>
        </div>
        """

    return f"""
    <div class="{card_class}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; border-bottom:1px solid #141414; padding-bottom:0.5rem;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span class="status-dot {dot_class}"></span>
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:{COLOR_MUTED}; letter-spacing:0.04em;">
                    {banner_text}
                </span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span class="mono" style="font-size:0.68rem; color:{COLOR_MUTED};">{intel.get('category', '')}</span>
                {render_severity_badge(risk_level)}
                <span class="soc-badge" style="color:{action_color}; background:{action_bg}; border:1px solid {action_color}30;">
                    {action}
                </span>
            </div>
        </div>

        <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:0.75rem;">
            <div style="background:#0D0D0D; border:1px solid #1A1A1A; border-radius:6px; padding:0.45rem; display:flex; align-items:center;">
                {icon_svg}
            </div>
            <div>
                <div style="font-size:1.02rem; font-weight:600; color:{COLOR_WHITE}; letter-spacing:-0.02em;">
                    {intel['title']}
                </div>
                <div class="mono" style="font-size:0.74rem; color:{COLOR_MUTED}; margin-top:0.15rem;">
                    Origin: <span style="color:{COLOR_WHITE};">{source_ip}</span> ➔ Target: <span style="color:{COLOR_WHITE};">{destination_ip}</span> · AI Confidence: <span style="color:{COLOR_AI_ACCENT};">{confidence*100:.1f}%</span>
                </div>
            </div>
        </div>

        {body_grid}

        {note_html}

        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.71rem; color:{COLOR_MUTED}; border-top:1px solid #141414; padding-top:0.5rem; margin-top:0.6rem;">
            <div>
                <span style="color:{COLOR_GRAY};">AI Detection Logic:</span> {intel['ai_detection']}
            </div>
            <div>
                <span style="color:{COLOR_GRAY};">Mitigation:</span> <span style="color:{COLOR_WHITE}; font-weight:500;">{intel['mitigation']}</span>
            </div>
        </div>
    </div>
    """
