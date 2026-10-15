"""
Metrics and Card Display Components for Arctus.
Renders CFO-grade metric cards, macro ticker telemetry strips, and scenario badge indicators.
"""

from typing import Dict, Any, Optional, Union
import streamlit as st
from core.theme import (
    format_inr,
    format_percentage,
    SURFACE_CARD,
    ACCENT_GOLD,
    BORDER_COLOR,
    BORDER_COLOR_GOLD,
    COLOR_GROWTH,
    COLOR_BASE,
    COLOR_RECESSION,
)


def render_metric_card(
    label: str,
    value: str,
    subtext: str = "",
    is_gold: bool = False,
    badge: Optional[str] = None,
    badge_type: str = "base"
):
    """
    Renders a custom styled metric card with tabular typography and gold accenting.
    """
    gold_cls = "gold" if is_gold else ""
    badge_html = ""
    if badge:
        b_cls = f"badge-{badge_type}"
        badge_html = f'<span class="{b_cls}" style="float: right; margin-top: -2px;">{badge}</span>'

    html = f"""
    <div class="arctus-metric-card">
        <div>
            <div class="arctus-metric-label">{label}{badge_html}</div>
            <div class="arctus-metric-value {gold_cls}">{value}</div>
        </div>
        {f'<div class="arctus-metric-sub">{subtext}</div>' if subtext else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_macro_ticker(macro_data: Dict[str, Any]):
    """
    Renders live Indian macroeconomic indicator telemetry strip.
    """
    rbi = macro_data.get("rbi_repo_rate", {}).get("value", 6.50)
    cpi = macro_data.get("cpi_inflation", {}).get("value", 4.85)
    brent = macro_data.get("brent_crude", {}).get("value", 74.50)
    gsec = macro_data.get("g_sec_10y", {}).get("value", 7.02)
    fetched_at = macro_data.get("_fetched_at", "Live")

    html = f"""
    <div style="
        background: {SURFACE_CARD};
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 12px 20px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    ">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="
                width: 8px; height: 8px; border-radius: 50%; background: {COLOR_GROWTH};
                box-shadow: 0 0 8px {COLOR_GROWTH}; display: inline-block;
            "></span>
            <span style="font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; color: {ACCENT_GOLD}; text-transform: uppercase;">
                Live Indian Macro Telemetry
            </span>
        </div>
        <div style="display: flex; gap: 24px; flex-wrap: wrap; font-size: 0.85rem;">
            <div>
                <span style="color: rgba(255,255,255,0.5);">RBI Repo:</span>
                <span style="font-weight: 700; color: #FFFFFF; font-variant-numeric: tabular-nums;">{rbi:.2f}%</span>
            </div>
            <div>
                <span style="color: rgba(255,255,255,0.5);">CPI Inflation:</span>
                <span style="font-weight: 700; color: #FFFFFF; font-variant-numeric: tabular-nums;">{cpi:.2f}%</span>
            </div>
            <div>
                <span style="color: rgba(255,255,255,0.5);">Brent Crude:</span>
                <span style="font-weight: 700; color: #FFFFFF; font-variant-numeric: tabular-nums;">${brent:.2f}</span>
            </div>
            <div>
                <span style="color: rgba(255,255,255,0.5);">10Y G-Sec:</span>
                <span style="font-weight: 700; color: #FFFFFF; font-variant-numeric: tabular-nums;">{gsec:.2f}%</span>
            </div>
        </div>
        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4);">
            Updated: {fetched_at}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
