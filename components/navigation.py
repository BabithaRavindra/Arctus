"""
Navigation Sidebar Component for Arctus.
Renders persistent custom sidebar for authenticated sessions with active-page
gold indicator, user/company details, and logout flow.
"""

from typing import Callable, Dict, Any
import streamlit as st
from core.theme import ACCENT_GOLD, SURFACE_CARD, BORDER_COLOR, TEXT_MUTED


def render_sidebar(current_page: str, on_navigate: Callable[[str], None], on_logout: Callable[[], None]):
    """
    Renders custom styled sidebar navigation.
    """
    user = st.session_state.get("user")
    company_name = user.company_name if user else "Arctus Enterprise"
    user_name = user.name if user else "Finance Lead"

    from core.assets import (
        get_logo_dark_full_b64,
        get_logo_light_full_b64,
        get_logo_icon_b64
    )
    logo_dark_full = get_logo_dark_full_b64()
    logo_light_full = get_logo_light_full_b64()
    logo_icon = get_logo_icon_b64()

    with st.sidebar:
        # Official Brand Logo Header
        st.markdown(
            f"""
            <div style="padding: 12px 0 16px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 14px; text-align: center;">
                <img src="{logo_dark_full}" alt="Arctus" class="logo-dark" style="width: 170px; height: auto; display: block; margin: 0 auto;" />
                <img src="{logo_light_full}" alt="Arctus" class="logo-light" style="width: 170px; height: auto; display: block; margin: 0 auto;" />
                <div style="font-size: 0.68rem; color: var(--accent-gold); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 8px; font-weight: 600;">
                    FP&A Stress-Testing Platform
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 12px; background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 8px; margin-bottom: 16px;">
                <span style="font-size: 0.78rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Theme</span>
                <button id="sidebarThemeToggleBtn" class="theme-toggle-btn" onclick="toggleTheme()" title="Toggle Dark / Light Mode" style="width: 32px; height: 32px; font-size: 1rem;">
                    <span class="theme-icon-sun">☀️</span>
                    <span class="theme-icon-moon">🌙</span>
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Company badge
        st.markdown(
            f"""
            <div style="
                background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 8px;
                padding: 10px 12px; margin-bottom: 24px;
            ">
                <div style="font-size: 0.7rem; text-transform: uppercase; color: rgba(255,255,255,0.4); letter-spacing: 0.05em;">
                    Active Enterprise
                </div>
                <div style="font-size: 0.9rem; font-weight: 600; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {company_name}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div style="font-size: 0.72rem; text-transform: uppercase; color: rgba(255,255,255,0.35); letter-spacing: 0.08em; margin-bottom: 8px;">Workspace</div>', unsafe_allow_html=True)

        pages = [
            ("overview", "📊 Executive Cockpit"),
            ("model", "📝 Ingestion & Modeling Grid"),
            ("scenarios", "🎯 Scenario Studio"),
            ("covenants", "🏦 Debt Covenant Matrix"),
            ("board_presentation", "📑 CFO Board Presentation"),
            ("dashboard", "⚡ Stress Engine & Simulation"),
            ("history", "📋 Scenario History"),
            ("settings", "⚙ Settings & Profile"),
            ("api_docs", "🔌 API Documentation"),
        ]

        for page_id, page_title in pages:
            is_active = (current_page == page_id)
            btn_style = "primary" if is_active else "secondary"
            if st.button(
                page_title,
                key=f"nav_{page_id}",
                use_container_width=True,
                type=btn_style
            ):
                on_navigate(page_id)

        st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='border-top: 1px solid {BORDER_COLOR}; margin-bottom: 16px;'></div>", unsafe_allow_html=True)

        # User profile summary & logout
        st.markdown(
            f"""
            <div style="margin-bottom: 12px;">
                <div style="font-size: 0.85rem; font-weight: 600; color: #FFFFFF;">{user_name}</div>
                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">{user.email if user else 'demo@arctus.in'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Sign Out", key="sidebar_logout_btn", use_container_width=True):
            on_logout()
