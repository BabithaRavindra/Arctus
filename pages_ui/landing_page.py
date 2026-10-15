"""
Landing Page Controller for Arctus.
Renders full-bleed, edge-to-edge landing experience using native st.html.
No sandboxed iframes, natural content height, zero trailing blank space.
"""

import streamlit as st
from components.landing import get_landing_html


def render_landing_page(on_navigate):
    """
    Renders edge-to-edge Apple-style landing page with integrated glassmorphic top navbar,
    official ARCTUS logo, unique hero animations, and comprehensive enterprise footer.
    """
    # Reset block-container constraints for full-bleed viewport and suppress Streamlit outer chrome
    st.markdown(
        """
        <style>
        /* Force full bleed for landing view */
        .main, .block-container {
            max-width: 100% !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            margin: 0 !important;
            width: 100% !important;
        }
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
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
        </style>
        """,
        unsafe_allow_html=True
    )

    landing_html = get_landing_html()
    # Native st.html: No iframe sandbox, natural flow height, zero trailing space, and direct link navigation!
    st.html(landing_html, unsafe_allow_javascript=True)
