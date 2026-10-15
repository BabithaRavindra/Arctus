"""
Onboarding Walkthrough Component for Arctus.
A 3-card interactive walkthrough displayed to new users to orient them on the
three-stage FP&A stress-testing workflow.
"""

import streamlit as st
from core.theme import ACCENT_GOLD, SURFACE_CARD, BORDER_COLOR, BORDER_COLOR_GOLD


def render_onboarding_modal(on_complete):
    """
    Renders 3-step onboarding overview modal for new finance teams.
    """
    st.markdown(
        f"""
        <div style="
            background: radial-gradient(circle at 50% 0%, rgba(20, 33, 61, 0.9) 0%, #000000 90%);
            border: 1px solid {BORDER_COLOR_GOLD}; border-radius: 16px; padding: 36px 32px;
            margin: 20px 0 36px 0; box-shadow: 0 8px 32px rgba(252, 163, 17, 0.1);
        ">
            <div style="text-align: center; max-width: 700px; margin: 0 auto 32px auto;">
                <span style="
                    background: rgba(252, 163, 17, 0.12); color: {ACCENT_GOLD};
                    padding: 4px 12px; border-radius: 100px; font-size: 0.75rem; font-weight: 600;
                    letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid {BORDER_COLOR_GOLD};
                ">Welcome to Arctus</span>
                <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; margin-top: 12px; color: #FFFFFF;">
                    30-Second Financial Stress-Testing
                </h2>
                <p style="color: rgba(255,255,255,0.7); font-size: 1rem; margin-top: 8px;">
                    Here is how Arctus transforms raw Indian accounting spreadsheets into CFO-grade forecasting rigor:
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="
                background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 12px;
                padding: 24px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
            ">
                <div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; color: {ACCENT_GOLD}; margin-bottom: 8px;">01</div>
                    <h4 style="font-size: 1.1rem; margin-bottom: 8px; color: #FFFFFF;">Zero-Friction Ingestion</h4>
                    <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.5;">
                        Upload raw P&L spreadsheets. The <b>RawNormalizer</b> automatically resolves multi-sheet files, unmerges cells, strips decorative banners, and parses Indian currency notations.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 12px;
                padding: 24px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
            ">
                <div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; color: {ACCENT_GOLD}; margin-bottom: 8px;">02</div>
                    <h4 style="font-size: 1.1rem; margin-bottom: 8px; color: #FFFFFF;">Live Macro Intelligence</h4>
                    <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.5;">
                        Scenario assumption sliders are grounded in live Indian macroeconomic indicators — <b>RBI Repo Rate</b>, <b>CPI Inflation</b>, and commodity indices — avoiding arbitrary guesswork.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="
                background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 12px;
                padding: 24px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
            ">
                <div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; color: {ACCENT_GOLD}; margin-bottom: 8px;">03</div>
                    <h4 style="font-size: 1.1rem; margin-bottom: 8px; color: #FFFFFF;">Monte Carlo Precision</h4>
                    <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.5;">
                        Vectorized execution simulates <b>1,000 iterations</b> per scenario in &lt;1 sec. View EBITDA waterfalls, probability fan charts, and tornado sensitivities instantly.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns([1, 1.5, 1])
    with b_col2:
        if st.button("Enter Financial Dashboard →", type="primary", use_container_width=True):
            on_complete()
