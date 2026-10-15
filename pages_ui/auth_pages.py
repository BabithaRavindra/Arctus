"""
Authentication Views (Login & Register) for Arctus.
Part of the unified Public Realm with top glassmorphic navbar and enterprise footer.
Includes client-side validation, password strength indicator, SQLite credential verification,
turnover bracket selection, and 1-click CFO demo login for instant evaluator access.
"""

import re
import streamlit as st
from core.database import create_user, authenticate_user
from core.theme import (
    ACCENT_GOLD,
    SURFACE_CARD,
    BORDER_COLOR,
    BORDER_COLOR_GOLD,
    COLOR_GROWTH,
    COLOR_RECESSION,
    COLOR_BASE,
)
from components.public_ui import (
    get_public_css,
    get_public_navbar,
    get_public_footer,
    get_public_scripts,
)
from core.assets import get_logo_dark_full_b64, get_logo_light_full_b64, get_logo_full_b64


def calculate_password_strength(password: str) -> tuple[int, str, str]:
    """
    Evaluates password strength.
    Returns (score 0-4, label, color).
    """
    if not password:
        return 0, "Enter password", "#E5E5E5"

    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1

    if score <= 1:
        return score, "Weak", COLOR_RECESSION
    elif score == 2 or score == 3:
        return score, "Moderate", COLOR_BASE
    else:
        return score, "Strong", COLOR_GROWTH


def _apply_public_auth_page_layout(active_page: str):
    """Applies edge-to-edge layout and renders the shared public navbar."""
    st.markdown(
        """
        <style>
        .main, .block-container {
            max-width: 100% !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            margin: 0 !important;
            width: 100% !important;
        }
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        [data-testid="stHeader"], header[data-testid="stHeader"], [data-testid="stBottom"], [data-testid="stStatusWidget"] {
            display: none !important;
            height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .top-navbar, nav.top-navbar {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 9999 !important;
        }
        .site-footer, footer.site-footer {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        .stHtml, [data-testid="stHtml"] {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .auth-content-container {
            max-width: 520px;
            margin: 0 auto;
            padding: 105px 20px 60px 20px;
        }
        .auth-card {
            background: var(--surface-card);
            border: 1px solid rgba(180, 154, 90, 0.25);
            border-radius: 16px;
            padding: 32px 28px;
            box-shadow: 0 16px 50px rgba(0, 0, 0, 0.8), 0 0 1px rgba(180, 154, 90, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Render top navbar
    navbar_html = f"{get_public_css()}{get_public_navbar(active_page=active_page)}{get_public_scripts()}"
    st.html(navbar_html, unsafe_allow_javascript=True)


def render_login_page(on_navigate, on_login_success):
    """
    Renders Login form with 1-click Demo credentials button and public header/footer.
    """
    _apply_public_auth_page_layout(active_page="login")
    logo_dark_full = get_logo_dark_full_b64()
    logo_light_full = get_logo_light_full_b64()

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 100px; margin-bottom: 24px;">
                <img src="{logo_dark_full}" alt="Arctus" class="logo-dark" style="width: 190px; height: auto; margin-bottom: 12px;" />
                <img src="{logo_light_full}" alt="Arctus" class="logo-light" style="width: 190px; height: auto; margin-bottom: 12px;" />
                <h2 style="font-family: 'DM Sans', sans-serif; font-size: 1.6rem; color: var(--text-primary); font-weight: 700;">
                    Enterprise Sign In
                </h2>
                <p style="color: rgba(229, 229, 229, 0.65); font-size: 0.92rem; margin-top: 4px;">
                    Access your company's stress-testing models and scenario runs
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1-Click Fast Evaluator Demo Login
        if st.button("⚡ 1-Click CFO Demo Access (Instant Launch)", type="primary", use_container_width=True):
            # Ensure demo account exists
            create_user(
                email="cfo@apexprecision.in",
                password="ArctusDemo2024!",
                name="Siddharth Mehta, CFO",
                company_name="Apex Precision Automotives Ltd.",
                default_unit="crores"
            )
            success, msg, user = authenticate_user("cfo@apexprecision.in", "ArctusDemo2024!")
            if success and user:
                on_login_success(user)

        st.markdown(
            f"""
            <div style="text-align: center; margin: 18px 0; color: rgba(255,255,255,0.4); font-size: 0.8rem; letter-spacing: 0.08em;">
                — OR ENTER CREDENTIALS —
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            email = st.text_input("Business Email", placeholder="cfo@apexprecision.in")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In to Arctus", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please provide both email and password.")
            else:
                success, msg, user = authenticate_user(email, password)
                if success and user:
                    st.success("Authenticated successfully.")
                    on_login_success(user)
                else:
                    st.error(msg)

        st.markdown(
            """
            <div style="text-align: right; margin-top: 8px;">
                <span style="font-size: 0.8rem; color: rgba(255,255,255,0.4); cursor: not-allowed;" title="Self-service reset disabled in local demo scope">
                    Forgot password? (Demo scope)
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write("Need an account?")
        with subcol2:
            if st.button("Register Enterprise →", key="switch_to_register", use_container_width=True):
                on_navigate("register")

        st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)

    # Render enterprise footer
    st.html(get_public_footer(), unsafe_allow_javascript=True)


def render_register_page(on_navigate, on_login_success):
    """
    Renders Enterprise Registration form with Indian turnover bracket selection,
    interactive password strength meter, and public header/footer.
    """
    _apply_public_auth_page_layout(active_page="register")
    logo_dark_full = get_logo_dark_full_b64()
    logo_light_full = get_logo_light_full_b64()

    col1, col2, col3 = st.columns([1, 2.0, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 100px; margin-bottom: 24px;">
                <img src="{logo_dark_full}" alt="Arctus" class="logo-dark" style="width: 190px; height: auto; margin-bottom: 12px;" />
                <img src="{logo_light_full}" alt="Arctus" class="logo-light" style="width: 190px; height: auto; margin-bottom: 12px;" />
                <h2 style="font-family: 'DM Sans', sans-serif; font-size: 1.6rem; color: var(--text-primary); font-weight: 700;">
                    Register Enterprise Account
                </h2>
                <p style="color: rgba(229, 229, 229, 0.65); font-size: 0.92rem; margin-top: 4px;">
                    Institutional FP&A and stress-testing for Indian mid-market CFOs
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("register_form"):
            name = st.text_input("Full Name & Designation", placeholder="e.g. Vikram Malhotra, CFO")
            company = st.text_input("Company / Enterprise Name", placeholder="e.g. Apex Precision Components Ltd.")
            turnover_tier = st.selectbox(
                "Annual Company Turnover Tier",
                options=[
                    "₹50 Cr – ₹150 Cr (Established Mid-Market)",
                    "₹25 Cr – ₹50 Cr (Emerging Mid-Market)",
                    "₹150 Cr – ₹500 Cr (Upper Mid-Market)",
                    "₹500 Cr+ (Large Enterprise)"
                ]
            )
            email = st.text_input("Corporate Email", placeholder="e.g. vikram@apexprecision.in")
            password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
            unit = st.selectbox(
                "Preferred Financial Unit",
                options=["crores", "lakhs", "raw"],
                format_func=lambda x: "Crores (₹ in Cr)" if x == "crores" else ("Lakhs (₹ in L)" if x == "lakhs" else "Raw (₹ Actuals)")
            )

            submit = st.form_submit_button("Create Account & Begin Onboarding →", use_container_width=True)

        # Dynamic password meter
        if password:
            score, label, color = calculate_password_strength(password)
            pct = max(10, score * 25)
            st.markdown(
                f"""
                <div style="margin-top: -10px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 4px;">
                        <span>Password Strength:</span>
                        <span style="color: {color}; font-weight: 600;">{label}</span>
                    </div>
                    <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px;">
                        <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 2px; transition: width 200ms ease;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if submit:
            if not name or not company or not email or not password:
                st.error("Please fill in all required registration fields.")
            elif "@" not in email or "." not in email:
                st.error("Please provide a valid corporate email address.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                full_company_desc = f"{company.strip()} [{turnover_tier.split(' ')[0]}]"
                success, msg, user = create_user(
                    email=email,
                    password=password,
                    name=name,
                    company_name=full_company_desc,
                    default_unit=unit
                )
                if success and user:
                    st.success("Enterprise account created successfully!")
                    st.session_state["show_onboarding"] = True
                    on_login_success(user)
                else:
                    st.error(msg)

        st.markdown(
            f"""
            <div style="
                background: rgba(20, 33, 61, 0.5); border: 1px solid {BORDER_COLOR}; border-radius: 8px;
                padding: 12px; margin-top: 20px; font-size: 0.75rem; color: rgba(255,255,255,0.5);
            ">
                <span style="color: {ACCENT_GOLD}; font-weight: 600;">Security & Sovereignty:</span>
                Your financial models are protected with local AES-256 encryption. Zero P&L data is sent to public AI platforms.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write("Already registered?")
        with subcol2:
            if st.button("Sign In →", key="switch_to_login", use_container_width=True):
                on_navigate("login")

        st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)

    # Render enterprise footer
    st.html(get_public_footer(), unsafe_allow_javascript=True)


# Backwards compatibility alias for existing references
render_signup_page = render_register_page
