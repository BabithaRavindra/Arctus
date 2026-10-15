"""
Unit tests for Arctus Public Realm Pages and Components.
Verifies HTML generation, unified navigation, footer presence, public route integrity,
Dark/Light theme toggle, DM Sans & Geist Mono typography, and updated brand logos.
"""

import pytest
from components.public_ui import (
    get_public_css,
    get_public_navbar,
    get_public_footer,
    get_public_scripts,
)
from components.landing import get_landing_html
from pages_ui.how_it_works_page import get_how_it_works_html
from pages_ui.product_page import get_product_html
from pages_ui.auth_pages import calculate_password_strength
from core.assets import (
    get_logo_dark_icon_b64,
    get_logo_dark_full_b64,
    get_logo_light_icon_b64,
    get_logo_light_full_b64,
)


def test_dual_brand_logos_exist():
    """Verify that both Dark and Light mode logos (icon + full) are available."""
    dark_icon = get_logo_dark_icon_b64()
    dark_full = get_logo_dark_full_b64()
    light_icon = get_logo_light_icon_b64()
    light_full = get_logo_light_full_b64()

    assert dark_icon.startswith("data:image/png;base64,")
    assert dark_full.startswith("data:image/png;base64,")
    assert light_icon.startswith("data:image/png;base64,")
    assert light_full.startswith("data:image/png;base64,")


def test_public_navbar_active_states_and_toggle():
    """Verify navbar renders 3 central links (Home, How It Works, Product), right actions (Sign In, Register), and theme toggle."""
    for page in ["landing", "how_it_works", "product", "login", "register"]:
        nav = get_public_navbar(active_page=page)
        assert 'class="top-navbar"' in nav
        assert f'data-page="{page}"' in nav
        assert "Home" in nav
        assert "How It Works" in nav
        assert "Product" in nav
        assert "Sign In" in nav
        assert "Register" in nav
        assert 'id="themeToggleBtn"' in nav
        assert "theme-icon-sun" in nav
        assert "theme-icon-moon" in nav
        assert "logo-dark" in nav
        assert "logo-light" in nav

    # Ensure Login and Register are NOT in center nav-links list
    sample_nav = get_public_navbar(active_page="landing")
    nav_links_block = sample_nav.split('<ul class="nav-links">')[1].split('</ul>')[0]
    assert "Home" in nav_links_block
    assert "How It Works" in nav_links_block
    assert "Product" in nav_links_block
    assert "Login" not in nav_links_block
    assert "Register" not in nav_links_block


def test_public_css_color_scheme_and_fonts():
    """Verify CSS tokens match the new palette (#101722, #F4F1E8, #B49A5A) and typography."""
    css = get_public_css()
    assert "#101722" in css
    assert "#F4F1E8" in css
    assert "#B49A5A" in css
    assert "DM Sans" in css
    assert "Geist Mono" in css
    assert '[data-theme="dark"]' in css
    assert '[data-theme="light"]' in css


def test_public_footer_content():
    """Verify enterprise footer contains all required columns, links, and dual logos."""
    footer = get_public_footer()
    assert 'class="site-footer"' in footer
    assert "RBI Policy Repo Rate" in footer
    assert "MoSPI Headline CPI" in footer
    assert "data-page=\"landing\"" in footer
    assert "data-page=\"how_it_works\"" in footer
    assert "data-page=\"product\"" in footer
    assert "data-page=\"login\"" in footer
    assert "data-page=\"register\"" in footer
    assert "logo-dark" in footer
    assert "logo-light" in footer


def test_landing_html_generation():
    """Verify landing page HTML generates cleanly without formatting errors."""
    html = get_landing_html()
    assert "Financial certainty," in html
    assert "simulated in seconds." in html
    assert "data-page=\"how_it_works\"" in html
    assert "data-page=\"product\"" in html
    assert "data-page=\"login\"" in html
    assert "data-page=\"register\"" in html
    assert "themeToggleBtn" in html
    assert "logo-dark" in html
    assert "logo-light" in html


def test_how_it_works_html_generation():
    """Verify How It Works page HTML contains the 4-stage pipeline and comparison table."""
    html = get_how_it_works_html()
    assert "From Raw Financials to" in html
    assert "CFO Certainty in 30 Seconds" in html
    assert "Multi-Period Ingestion & Currency Normalization" in html
    assert "RapidFuzz Indian GAAP Schema Reconciliation" in html
    assert "Correlated Vectorized Monte Carlo Engine" in html
    assert "CFO Prescriptive Analytics & Waterfall Bridges" in html
    assert "Excel Financial Models vs. Arctus" in html
    assert "Traditional Excel Scenario Modeling" in html


def test_product_html_generation():
    """Verify Product page HTML contains all 6 core modules and specifications."""
    html = get_product_html()
    assert "The Quantitative Engine Built for" in html
    assert "Vectorized Monte Carlo Engine" in html
    assert "Live Indian Macro Telemetry Hub" in html
    assert "CFO Visualization & Waterfall Suite" in html
    assert "Indian GAAP & Ind AS Compliance" in html
    assert "High-Throughput REST API" in html
    assert "Enterprise Security & Sovereignty" in html
    assert "Simulation Latency" in html


def test_password_strength_calculation():
    """Verify dynamic password strength scoring."""
    score, label, color = calculate_password_strength("")
    assert score == 0
    assert label == "Enter password"

    score, label, color = calculate_password_strength("weak")
    assert score <= 1
    assert label == "Weak"

    score, label, color = calculate_password_strength("StrongPass123!")
    assert score >= 4
    assert label == "Strong"


def test_landing_page_navbar_and_logo_switching():
    """Verify landing page includes persistent <nav> navbar, theme toggle, and dual logo CSS rules."""
    html = get_landing_html()
    # Navbar must use <nav> container, not suppressed <header>
    assert '<nav class="top-navbar">' in html
    assert 'id="themeToggleBtn"' in html
    assert 'data-theme="dark"' in html

    # Logo switching CSS rules must exist so both logos never display together
    assert ".logo-light { display: none !important; }" in html or ".logo-light { display: none !important; }" in html
    assert ".logo-dark { display: inline-block !important; }" in html
    assert '[data-theme="light"] .logo-dark { display: none !important; }' in html
    assert '[data-theme="light"] .logo-light { display: inline-block !important; }' in html


def test_global_css_preserves_navbar_and_supports_dual_logos():
    """Verify global CSS does not suppress custom navbar/footer and includes logo switching rules."""
    from core.theme import get_custom_css
    css = get_custom_css()
    # Must NOT have generic 'header, footer' suppression without data-testid
    assert "header[data-testid=\"stHeader\"]" in css or '[data-testid="stHeader"]' in css
    # Must explicitly protect top-navbar
    assert ".top-navbar, nav.top-navbar" in css
    assert "display: flex !important;" in css
    # Must define logo switching
    assert ".logo-light" in css
    assert ".logo-dark" in css
    assert "window.toggleTheme" in css

