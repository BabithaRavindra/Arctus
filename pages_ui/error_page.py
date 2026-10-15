"""
Custom 404 and Error Page for Arctus.
Branded fallback view adhering to the Black & Gold Elegance design system.
"""

import streamlit as st
from core.theme import ACCENT_GOLD, SURFACE_CARD, BORDER_COLOR


def render_error_page(on_navigate, error_message: str = "Page or Resource Not Found"):
    """
    Renders styled 404 / error recovery screen.
    """
    st.markdown(
        f"""
        <div style="
            background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 16px;
            padding: 64px 32px; text-align: center; max-width: 650px; margin: 40px auto;
        ">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 5rem; font-weight: 800; color: {ACCENT_GOLD}; line-height: 1;">
                404
            </div>
            <h2 style="margin-top: 16px; font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem;">
                {error_message}
            </h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem; margin: 12px auto 28px auto; max-width: 440px;">
                The requested financial model, scenario run, or route does not exist or has been relocated.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("Return to Main Dashboard →", type="primary", use_container_width=True):
            on_navigate("dashboard")
