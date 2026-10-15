"""
Arctus Design System - "Black & Gold Elegance"
Central source of truth for color palette, typography, CSS tokens, Indian currency formatting,
and the shared Plotly dark theme.
"""

from typing import Union
import plotly.graph_objects as go
import plotly.io as pio

# -----------------------------------------------------------------------------
# Base Color Palette Tokens (User Palette: #101722, #F4F1E8, #B49A5A)
# -----------------------------------------------------------------------------
BG_BASE = "#101722"                   # Obsidian Deep Navy (Dark Base)
SURFACE_CARD = "#16202E"              # Elevated Navy Surface
ACCENT_GOLD = "#B49A5A"               # Antique Champagne Gold
ACCENT_GOLD_HOVER = "#C5AC6C"         # Bright Antique Gold
TEXT_PRIMARY = "#F4F1E8"              # Warm Alabaster / Ivory Cream
TEXT_MUTED = "rgba(244, 241, 232, 0.72)"
BORDER_COLOR = "rgba(244, 241, 232, 0.12)"
BORDER_COLOR_GOLD = "rgba(180, 154, 90, 0.35)"

# Light Mode Tokens
LIGHT_BG_BASE = "#F4F1E8"             # Warm Alabaster (Light Base)
LIGHT_SURFACE_CARD = "#FFFFFF"        # Crisp White Card Surface
LIGHT_TEXT_PRIMARY = "#101722"        # Obsidian Deep Navy Text
LIGHT_TEXT_MUTED = "rgba(16, 23, 34, 0.75)"
LIGHT_BORDER_COLOR = "rgba(16, 23, 34, 0.12)"

# -----------------------------------------------------------------------------
# Semantic / Scenario Colors (Demure, Palette-Matched)
# -----------------------------------------------------------------------------
COLOR_GROWTH = "#7A9B76"              # Muted sage green
COLOR_GROWTH_BG = "rgba(122, 155, 118, 0.12)"

COLOR_BASE = "#B49A5A"                # Brand antique gold
COLOR_BASE_BG = "rgba(180, 154, 90, 0.12)"

COLOR_RECESSION = "#B5545A"           # Dusty muted rose / brick red
COLOR_RECESSION_BG = "rgba(181, 84, 90, 0.12)"

COLOR_INFO = "#4A90E2"
COLOR_INFO_BG = "rgba(74, 144, 226, 0.12)"

# -----------------------------------------------------------------------------
# Typography Tokens (DM Sans & Geist Mono)
# -----------------------------------------------------------------------------
FONT_HEADER = "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_BODY = "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"

# -----------------------------------------------------------------------------
# Indian Currency & Number Formatting Helpers
# -----------------------------------------------------------------------------
def format_indian_number(val: Union[int, float], decimals: int = 2) -> str:
    """
    Format a number following Indian comma notation (e.g. 12,34,567.89).
    Negative numbers are formatted with leading minus or cleanly without parentheses.
    """
    if val is None:
        return "₹0.00"
    is_negative = val < 0
    val = abs(float(val))
    parts = f"{val:.{decimals}f}".split(".")
    integer_part = parts[0]
    decimal_part = f".{parts[1]}" if len(parts) > 1 and decimals > 0 else ""
    
    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last3 = integer_part[-3:]
        other = integer_part[:-3]
        res = []
        while len(other) > 2:
            res.insert(0, other[-2:])
            other = other[:-2]
        if other:
            res.insert(0, other)
        res.append(last3)
        formatted_int = ",".join(res)
        
    sign = "-" if is_negative else ""
    return f"{sign}{formatted_int}{decimal_part}"

def format_inr(val: Union[int, float], unit: str = "auto", decimals: int = 2) -> str:
    """
    Format an amount in Indian Rupees with ₹ symbol and optional Lakhs / Crores unit.
    unit: 'auto', 'crores', 'lakhs', or 'raw'
    """
    if val is None:
        return "₹0.00"
    
    num = float(val)
    abs_num = abs(num)
    sign = "-" if num < 0 else ""
    
    if unit == "crores" or (unit == "auto" and abs_num >= 1e7):
        cr_val = abs_num / 1e7
        return f"{sign}₹{cr_val:.{decimals}f} Cr"
    elif unit == "lakhs" or (unit == "auto" and abs_num >= 1e5):
        lakh_val = abs_num / 1e5
        return f"{sign}₹{lakh_val:.{decimals}f} L"
    else:
        return f"₹{format_indian_number(num, decimals=decimals)}"

def format_percentage(val: Union[int, float], decimals: int = 1, show_plus: bool = False) -> str:
    """Format float into percentage string (e.g. 12.5% or +8.2%)."""
    if val is None:
        return "0.0%"
    sign = "+" if show_plus and val > 0 else ""
    return f"{sign}{val:.{decimals}f}%"

# -----------------------------------------------------------------------------
# Global CSS Injected into Streamlit
# -----------------------------------------------------------------------------
def get_custom_css() -> str:
    """
    Generates CSS overrides to ensure the app matches 'Black & Gold Elegance'.
    Hides default Streamlit chrome and styles buttons, cards, tables, inputs.
    """
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Geist+Mono:wght@100..900&display=swap');

    :root, [data-theme="dark"] {{
        --bg-base: {BG_BASE};
        --surface-card: {SURFACE_CARD};
        --surface-card-hover: #1E2B3E;
        --accent-gold: {ACCENT_GOLD};
        --accent-gold-hover: {ACCENT_GOLD_HOVER};
        --text-primary: {TEXT_PRIMARY};
        --text-muted: {TEXT_MUTED};
        --border-color: {BORDER_COLOR};
        --border-gold: {BORDER_COLOR_GOLD};
        --color-growth: {COLOR_GROWTH};
        --color-base: {COLOR_BASE};
        --color-recession: {COLOR_RECESSION};
        --font-header: {FONT_HEADER};
        --font-body: {FONT_BODY};
        --font-mono: {FONT_MONO};
    }}

    [data-theme="light"] {{
        --bg-base: {LIGHT_BG_BASE};
        --surface-card: {LIGHT_SURFACE_CARD};
        --surface-card-hover: #FAF7F0;
        --accent-gold: {ACCENT_GOLD};
        --accent-gold-hover: #9E8548;
        --text-primary: {LIGHT_TEXT_PRIMARY};
        --text-muted: {LIGHT_TEXT_MUTED};
        --border-color: {LIGHT_BORDER_COLOR};
        --border-gold: rgba(180, 154, 90, 0.45);
        --color-growth: #4E7B4A;
        --color-base: {COLOR_BASE};
        --color-recession: #A83E44;
        --font-header: {FONT_HEADER};
        --font-body: {FONT_BODY};
        --font-mono: {FONT_MONO};
    }}

    /* Full reset on background and global typography */
    html, body, [class*="stApp"] {{
        background-color: var(--bg-base) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
        -webkit-font-smoothing: antialiased;
    }}

    /* Streamlit chrome suppression (only default streamlit headers/footers, never custom top navbar or footer) */
    #MainMenu, [data-testid="stHeader"], header[data-testid="stHeader"], [data-testid="stBottom"], footer[data-testid="stFooter"] {{
        visibility: hidden !important;
        display: none !important;
        height: 0px !important;
    }}
    .stDeployButton {{
        display: none !important;
    }}
    [data-testid="stToolbar"] {{
        visibility: hidden !important;
    }}

    /* Top navbar and footer persistence */
    .top-navbar, nav.top-navbar {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 9999 !important;
    }}
    .site-footer, footer.site-footer {{
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }}

    /* Logo Switching for Light & Dark Themes */
    .logo-light {{ display: none !important; }}
    .logo-dark {{ display: inline-block !important; }}
    [data-theme="dark"] .logo-light {{ display: none !important; }}
    [data-theme="dark"] .logo-dark {{ display: inline-block !important; }}
    [data-theme="light"] .logo-dark {{ display: none !important; }}
    [data-theme="light"] .logo-light {{ display: inline-block !important; }}

    /* Global Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-header) !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
        font-weight: 600 !important;
    }}
    h1 {{ font-weight: 700 !important; }}
    
    p, span, label, div {{
        font-family: var(--font-body);
    }}
    
    .tabular-numbers {{
        font-variant-numeric: tabular-nums !important;
    }}

    /* Main Container layout */
    .block-container {{
        max-width: 1200px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: var(--surface-card) !important;
        border-right: 1px solid var(--border-color) !important;
        transition: background-color 200ms ease, border-color 200ms ease;
    }}
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* Button Styling: Black background, gold border, gold text -> Inverts on hover */
    .stButton > button, div.stButton > button:first-child {{
        background-color: var(--bg-base) !important;
        color: var(--accent-gold) !important;
        border: 1px solid var(--accent-gold) !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.25rem !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: all 180ms ease-in-out !important;
        box-shadow: none !important;
        min-height: 42px !important;
    }}
    .stButton > button:hover, div.stButton > button:first-child:hover {{
        background-color: var(--accent-gold) !important;
        color: #101722 !important;
        border-color: var(--accent-gold) !important;
        box-shadow: 0 4px 18px rgba(180, 154, 90, 0.25) !important;
    }}
    .stButton > button:active, div.stButton > button:first-child:active {{
        transform: scale(0.98);
    }}

    /* Secondary / Ghost button */
    .secondary-btn > button {{
        background-color: transparent !important;
        color: var(--text-muted) !important;
        border: 1px solid var(--border-color) !important;
    }}
    .secondary-btn > button:hover {{
        background-color: var(--surface-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--text-muted) !important;
    }}

    /* Form Inputs & Selectboxes */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background-color: var(--surface-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px rgba(180, 154, 90, 0.2) !important;
    }}
    
    /* Sliders */
    .stSlider > div > div > div > div {{
        background-color: var(--accent-gold) !important;
    }}

    /* File Uploader */
    [data-testid="stFileUploader"] {{
        background-color: var(--surface-card) !important;
        border: 1px dashed var(--border-gold) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: border-color 200ms ease;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: var(--accent-gold) !important;
    }}
    [data-testid="stFileUploader"] button {{
        background-color: var(--bg-base) !important;
        color: var(--accent-gold) !important;
        border: 1px solid var(--accent-gold) !important;
    }}

    /* Expander / Accordion */
    [data-testid="stExpander"] {{
        background-color: var(--surface-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 16px;
        background-color: transparent !important;
        border-bottom: 1px solid var(--border-color) !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        color: var(--text-muted) !important;
        font-family: var(--font-header) !important;
        font-weight: 500 !important;
        border-bottom: 2px solid transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: var(--accent-gold) !important;
        border-bottom: 2px solid var(--accent-gold) !important;
        font-weight: 700 !important;
    }}

    /* Custom Arctus Card Container */
    .arctus-card {{
        background-color: var(--surface-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
                    box-shadow 260ms cubic-bezier(0.16, 1, 0.3, 1),
                    border-color 260ms ease,
                    background-color 200ms ease;
        margin-bottom: 1.5rem;
        position: relative;
    }}
    .arctus-card:hover {{
        transform: translateY(-5px);
        border-color: var(--border-gold) !important;
        box-shadow: 0 12px 35px rgba(180, 154, 90, 0.15) !important;
    }}

    /* Metric Cards */
    .arctus-metric-card {{
        background-color: var(--surface-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        transition: transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
                    box-shadow 260ms cubic-bezier(0.16, 1, 0.3, 1),
                    border-color 260ms ease,
                    background-color 200ms ease;
    }}
    .arctus-metric-card:hover {{
        transform: translateY(-6px) scale(1.01);
        border-color: var(--border-gold) !important;
        box-shadow: 0 12px 36px rgba(180, 154, 90, 0.15) !important;
    }}
    .arctus-metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        transition: left 600ms ease;
    }}
    .arctus-metric-card:hover::before {{
        left: 100%;
    }}
    .arctus-metric-label {{
        font-size: 0.82rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
        font-weight: 500;
    }}
    .arctus-metric-value {{
        font-size: 1.85rem;
        font-family: var(--font-header);
        font-weight: 700;
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
        line-height: 1.2;
    }}
    .arctus-metric-value.gold {{
        color: var(--accent-gold);
    }}
    .arctus-metric-sub {{
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 6px;
    }}

    /* Semantic Callout Badges */
    .badge-growth {{
        background-color: rgba(122, 155, 118, 0.15);
        color: var(--color-growth);
        border: 1px solid var(--color-growth);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    .badge-base {{
        background-color: rgba(180, 154, 90, 0.15);
        color: var(--color-base);
        border: 1px solid var(--color-base);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    .badge-recession {{
        background-color: rgba(181, 84, 90, 0.15);
        color: var(--color-recession);
        border: 1px solid var(--color-recession);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }}

    /* Scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-base);
    }}
    ::-webkit-scrollbar-thumb {{
        background: #1F2D4D;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--accent-gold);
    }}
    </style>

    <script>
    (function() {{
        function getArctusTheme() {{
            try {{
                return localStorage.getItem('arctus_theme') || 'dark';
            }} catch(e) {{
                return 'dark';
            }}
        }}

        function applyGlobalTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
            document.body.setAttribute('data-theme', theme);
            try {{
                localStorage.setItem('arctus_theme', theme);
            }} catch(e) {{}}

            try {{
                if (window.top && window.top.document) {{
                    window.top.document.documentElement.setAttribute('data-theme', theme);
                    window.top.document.body.setAttribute('data-theme', theme);
                }}
            }} catch(e) {{}}
            try {{
                if (window.parent && window.parent.document) {{
                    window.parent.document.documentElement.setAttribute('data-theme', theme);
                    window.parent.document.body.setAttribute('data-theme', theme);
                }}
            }} catch(e) {{}}

            const wrappers = document.querySelectorAll('.arctus-public-wrapper, .arctus-landing-wrapper, [class*="stApp"], [data-testid="stAppViewContainer"]');
            wrappers.forEach(w => w.setAttribute('data-theme', theme));
            window.dispatchEvent(new CustomEvent('arctusThemeChanged', {{ detail: {{ theme: theme }} }}));
        }}

        window.toggleTheme = function() {{
            const current = document.documentElement.getAttribute('data-theme') || getArctusTheme();
            const next = current === 'dark' ? 'light' : 'dark';
            applyGlobalTheme(next);
        }};

        document.addEventListener('click', function(e) {{
            const toggle = e.target.closest('#themeToggleBtn, #sidebarThemeToggleBtn, .theme-toggle-btn, [data-theme-toggle]');
            if (toggle) {{
                e.preventDefault();
                e.stopPropagation();
                window.toggleTheme();
            }}
        }}, true);

        // Apply immediately upon load
        applyGlobalTheme(getArctusTheme());
    }})();
    </script>
    """

# -----------------------------------------------------------------------------
# Shared Plotly Dark Theme
# -----------------------------------------------------------------------------
def get_plotly_template() -> go.layout.Template:
    """
    Creates and registers the standardized 'arctus_black_gold' Plotly template.
    Uses black & navy background, gold and demure scenario colors, tabular numbers,
    and subtle low-opacity gridlines.
    """
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor=BG_BASE,
        plot_bgcolor=SURFACE_CARD,
        font=dict(
            family="Inter, Space Grotesk, sans-serif",
            color=TEXT_PRIMARY,
            size=12
        ),
        title=dict(
            font=dict(
                family="Space Grotesk, sans-serif",
                color=TEXT_PRIMARY,
                size=16
            ),
            x=0.02,
            y=0.96
        ),
        colorway=[
            ACCENT_GOLD,      # Default / Primary
            COLOR_GROWTH,     # Sage Green (Growth)
            COLOR_RECESSION,  # Muted Brick Red (Recession)
            "#4A90E2",        # Muted Blue (Secondary / Actuals)
            "#A0AAB2",        # Silver / Neutral
            "#C59B27"
        ],
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=SURFACE_CARD,
            bordercolor=BORDER_COLOR_GOLD,
            font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=12)
        ),
        xaxis=dict(
            gridcolor="rgba(229, 229, 229, 0.08)",
            linecolor="rgba(229, 229, 229, 0.15)",
            zerolinecolor="rgba(229, 229, 229, 0.15)",
            tickfont=dict(color=TEXT_MUTED, size=11),
            title=dict(font=dict(color=TEXT_MUTED, size=12))
        ),
        yaxis=dict(
            gridcolor="rgba(229, 229, 229, 0.08)",
            linecolor="rgba(229, 229, 229, 0.15)",
            zerolinecolor="rgba(252, 163, 17, 0.25)",
            tickfont=dict(color=TEXT_MUTED, size=11),
            title=dict(font=dict(color=TEXT_MUTED, size=12))
        ),
        legend=dict(
            bgcolor="rgba(20, 33, 61, 0.6)",
            bordercolor=BORDER_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_PRIMARY, size=11)
        ),
        margin=dict(l=50, r=30, t=50, b=40)
    )
    return template

# Register the template globally in plotly
ARCTUS_TEMPLATE = get_plotly_template()
pio.templates["arctus_black_gold"] = ARCTUS_TEMPLATE
pio.templates.default = "arctus_black_gold"
