"""
Settings and Profile View for Arctus.
Enables updating enterprise metadata, financial display unit preferences (Lakhs vs Crores),
and viewing system environment configurations.
"""

import streamlit as st
from core.database import update_user_profile
from core.theme import ACCENT_GOLD, SURFACE_CARD, BORDER_COLOR, BORDER_COLOR_GOLD


def render_settings_page():
    """
    Renders enterprise settings, preferences, and profile configuration.
    """
    user = st.session_state.get("user")
    if not user:
        st.warning("Please sign in to view settings.")
        return

    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; margin-bottom: 4px;">
                Enterprise Settings & Preferences
            </h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">
                Configure reporting currency units, company name, and macroeconomic telemetry defaults.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("settings_form"):
        st.markdown("### Profile Information")
        name = st.text_input("Lead Finance Officer Name", value=user.name)
        company = st.text_input("Company / Enterprise Entity", value=user.company_name)
        st.text_input("Registered Email (Fixed)", value=user.email, disabled=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("### Financial Reporting Preferences")
        unit = st.selectbox(
            "Default Monetary Display Unit",
            options=["crores", "lakhs", "raw"],
            index=["crores", "lakhs", "raw"].index(user.default_unit) if user.default_unit in ["crores", "lakhs", "raw"] else 0,
            format_func=lambda x: "Crores (₹ in Cr) — Standard for >₹10 Cr Turnover" if x == "crores" else (
                "Lakhs (₹ in L) — Standard for <₹10 Cr Turnover" if x == "lakhs" else "Raw Indian Rupee Figures (₹ Actuals)"
            ),
            help="Determines default formatting across charts, metric cards, and reports."
        )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("### Design System Tokens")
        st.markdown(
            f"""
            <div style="
                background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 8px;
                padding: 16px; font-size: 0.85rem; color: rgba(255,255,255,0.8);
            ">
                <div style="display: flex; gap: 16px; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 600;">Active Theme:</span>
                    <span style="color: {ACCENT_GOLD}; font-weight: 700;">Black & Gold Elegance (Locked)</span>
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">
                    Palette: #000000 (Base), #14213D (Surface), #FCA311 (Accent Gold), #7A9B76 (Growth), #B5545A (Recession).
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        submit = st.form_submit_button("Save Changes", type="primary")

    if submit:
        update_user_profile(user.id, company, unit)
        user.name = name
        user.company_name = company
        user.default_unit = unit
        st.session_state["user"] = user
        st.success("Settings updated successfully!")
