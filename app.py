"""
ARCTUS — Institutional FP&A Stress-Testing Platform for Indian Mid-Market Enterprises.
Main application router and global session manager.
"""

import streamlit as st

# Set page configuration FIRST before any other streamlit commands
st.set_page_config(
    page_title="Arctus — FP&A Stress Testing",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import design system and inject global CSS reset
from core.theme import get_custom_css
st.markdown(get_custom_css(), unsafe_allow_html=True)

from core.database import create_user, authenticate_user, init_db
from components.navigation import render_sidebar
from pages_ui.landing_page import render_landing_page
from pages_ui.how_it_works_page import render_how_it_works_page
from pages_ui.product_page import render_product_page
from pages_ui.auth_pages import render_register_page, render_login_page, render_signup_page
from pages_ui.onboarding import render_onboarding_modal
from pages_ui.overview import render_overview_page
from pages_ui.model_page import render_model_page
from pages_ui.scenarios_page import render_scenarios_page
from pages_ui.covenants_page import render_covenants_page
from pages_ui.board_presentation_page import render_board_presentation_page
from pages_ui.dashboard import render_dashboard
from pages_ui.history import render_history_page
from pages_ui.settings import render_settings_page
from pages_ui.api_docs import render_api_docs_page
from pages_ui.error_page import render_error_page


@st.cache_resource
def start_background_api():
    """
    Spins up the Flask REST API server in a background daemon thread on port 5000.
    Cached via st.cache_resource so it only initializes once per Streamlit server lifecycle.
    """
    import socket
    import threading
    import logging

    # Silence Flask/Werkzeug request logging in the main console
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_open = sock.connect_ex(("127.0.0.1", 5000)) == 0
    sock.close()

    if not is_open:
        from api.app import app as flask_app
        t = threading.Thread(
            target=lambda: flask_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
            daemon=True,
            name="ArctusFlaskAPIThread"
        )
        t.start()
        return True
    return False


# Initialize database and auto-start REST API engine
init_db()
start_background_api()


def init_session():
    """Initializes global session state defaults and handles URL query parameters."""
    if "page" not in st.session_state:
        st.session_state["page"] = "landing"
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "show_onboarding" not in st.session_state:
        st.session_state["show_onboarding"] = False

    # Check for URL query parameter navigation from top navbar or footer
    query_page = st.query_params.get("page")
    if query_page:
        valid_pages = [
            "landing", "how_it_works", "product", "login", "register", "signup",
            "overview", "model", "scenarios", "covenants", "board_presentation", "dashboard", "history", "settings", "api_docs"
        ]
        if query_page in valid_pages:
            # If navigating directly to dashboard, model, scenarios, covenants, board_presentation, or overview, provide instant demo user if not logged in
            if query_page in ["dashboard", "overview", "model", "scenarios", "covenants", "board_presentation"] and st.session_state["user"] is None:
                create_user(
                    email="cfo@apexprecision.in",
                    password="ArctusDemo2024!",
                    name="Siddharth Mehta, CFO",
                    company_name="Apex Precision Automotives Ltd.",
                    default_unit="crores"
                )
                _, _, demo_user = authenticate_user("cfo@apexprecision.in", "ArctusDemo2024!")
                st.session_state["user"] = demo_user

            # Normalize signup to register
            if query_page == "signup":
                query_page = "register"

            st.session_state["page"] = query_page
            # Clear query params to keep clean URL
            st.query_params.clear()


def navigate_to(page_name: str):
    """Router navigation helper."""
    st.session_state["page"] = page_name
    st.rerun()


def handle_login_success(user):
    """Callback upon successful signup or login."""
    st.session_state["user"] = user
    if st.session_state.get("show_onboarding"):
        st.session_state["page"] = "onboarding"
    else:
        st.session_state["page"] = "overview"
    st.rerun()


def handle_logout():
    """Callback to clear session and return to Landing page."""
    st.session_state["user"] = None
    st.session_state["show_onboarding"] = False
    st.session_state["forecast_results"] = None
    st.session_state["page"] = "landing"
    st.rerun()


def main():
    init_session()
    current_page = st.session_state["page"]
    user = st.session_state["user"]

    # Public Unauthenticated Routes (The 5 Public Realm Pages)
    if current_page == "landing":
        render_landing_page(on_navigate=navigate_to)
        return

    if current_page == "how_it_works":
        render_how_it_works_page(on_navigate=navigate_to)
        return

    if current_page == "product":
        render_product_page(on_navigate=navigate_to)
        return

    if current_page in ["register", "signup"]:
        render_register_page(on_navigate=navigate_to, on_login_success=handle_login_success)
        return

    if current_page == "login":
        render_login_page(on_navigate=navigate_to, on_login_success=handle_login_success)
        return

    # Authenticated Routes (or Demo fallback)
    if user is None and current_page not in ["landing", "how_it_works", "product", "login", "register", "signup"]:
        navigate_to("login")
        return

    # Onboarding walkthrough screen
    if current_page == "onboarding":
        render_onboarding_modal(on_complete=lambda: navigate_to("overview"))
        return

    # Render Persistent Sidebar for Authenticated Workspace
    render_sidebar(
        current_page=current_page,
        on_navigate=navigate_to,
        on_logout=handle_logout
    )

    # Active Page Router
    user_unit = user.default_unit if user else "crores"

    if current_page == "overview":
        render_overview_page(on_navigate=navigate_to, user_unit=user_unit)
    elif current_page == "model":
        render_model_page(on_navigate=navigate_to, user_unit=user_unit)
    elif current_page == "scenarios":
        render_scenarios_page(on_navigate=navigate_to, user_unit=user_unit)
    elif current_page == "covenants":
        render_covenants_page(on_navigate=navigate_to, user_unit=user_unit)
    elif current_page == "board_presentation":
        render_board_presentation_page(on_navigate=navigate_to, user_unit=user_unit)
    elif current_page == "dashboard":
        render_dashboard(user_unit=user_unit, on_navigate=navigate_to)
    elif current_page == "history":
        render_history_page(on_navigate=navigate_to, user_unit=user_unit)
    elif current_page == "settings":
        render_settings_page()
    elif current_page == "api_docs":
        render_api_docs_page()
    else:
        render_error_page(on_navigate=navigate_to)


if __name__ == "__main__":
    main()
