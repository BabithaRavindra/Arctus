"""
Shared Public UI Components for Arctus.
Provides the consistent Glassmorphic Top Navbar, Enterprise Footer,
Dark/Light theme toggle, design system CSS tokens (#101722, #F4F1E8, #B49A5A),
DM Sans & Geist Mono typography, and JavaScript navigation & theme handlers across all public pages:
- Landing (/)
- How It Works (/how-it-works)
- Product (/product)
- Login (/login)
- Register (/register)
"""

from core.assets import (
    get_logo_dark_icon_b64,
    get_logo_dark_full_b64,
    get_logo_light_icon_b64,
    get_logo_light_full_b64,
)


def get_public_css() -> str:
    """Returns the shared CSS styling for all public pages with dual light/dark theme support."""
    return """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Geist+Mono:wght@100..900&display=swap');

  /* -------------------------------------------------------------
     COLOR SCHEME TOKENS:
     - #101722: Obsidian Deep Navy (Dark Base / Light Text)
     - #F4F1E8: Warm Alabaster / Ivory Cream (Light Base / Dark Text)
     - #B49A5A: Signature Antique Champagne Gold (Accent)
  ------------------------------------------------------------- */
  :root, [data-theme="dark"] {
    --bg-base: #101722;
    --surface-card: #16202E;
    --surface-card-hover: #1E2B3E;
    --surface-sunken: #0B1018;
    --accent-gold: #B49A5A;
    --accent-gold-hover: #C5AC6C;
    --text-primary: #F4F1E8;
    --text-muted: rgba(244, 241, 232, 0.75);
    --text-dim: rgba(244, 241, 232, 0.52);
    --border-color: rgba(244, 241, 232, 0.12);
    --border-gold: rgba(180, 154, 90, 0.35);
    --nav-bg: rgba(16, 23, 34, 0.92);
    --footer-bg: #0B1018;
    --color-growth: #7A9B76;
    --color-base: #B49A5A;
    --color-recession: #B5545A;
  }

  [data-theme="light"] {
    --bg-base: #F4F1E8;
    --surface-card: #FFFFFF;
    --surface-card-hover: #FAF7F0;
    --surface-sunken: #EBE6D8;
    --accent-gold: #B49A5A;
    --accent-gold-hover: #9E8548;
    --text-primary: #101722;
    --text-muted: rgba(16, 23, 34, 0.75);
    --text-dim: rgba(16, 23, 34, 0.55);
    --border-color: rgba(16, 23, 34, 0.12);
    --border-gold: rgba(180, 154, 90, 0.45);
    --nav-bg: rgba(244, 241, 232, 0.94);
    --footer-bg: #EAE5D8;
    --color-growth: #4E7B4A;
    --color-base: #B49A5A;
    --color-recession: #A83E44;
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html {
    scroll-behavior: smooth;
  }

  .arctus-public-wrapper, .arctus-landing-wrapper {
    background-color: var(--bg-base);
    color: var(--text-primary);
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    width: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    position: relative;
    min-height: 100vh;
    transition: background-color 220ms ease, color 220ms ease;
  }

  /* Monospace overrides */
  code, pre, .mono, .tabular-numbers, .code-pill, .macro-num, .spec-value {
    font-family: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
  }

  /* -------------------------------------------------------------
     LOGO SWITCHING (LIGHT VS DARK MODE)
  ------------------------------------------------------------- */
  .logo-light { display: none !important; }
  .logo-dark { display: inline-block !important; }
  [data-theme="dark"] .logo-light { display: none !important; }
  [data-theme="dark"] .logo-dark { display: inline-block !important; }
  [data-theme="light"] .logo-dark { display: none !important; }
  [data-theme="light"] .logo-light { display: inline-block !important; }

  /* Ensure navbar and footer are never suppressed */
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

  /* -------------------------------------------------------------
     TOP STICKY GLASSMORPHIC NAVBAR (PIXEL-PERFECT VERTICAL ALIGNMENT)
  ------------------------------------------------------------- */
  .top-navbar, nav.top-navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 72px;
    z-index: 1000;
    background: var(--nav-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-color);
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    transition: background 220ms ease, border-color 220ms ease;
  }

  .nav-container {
    max-width: 1240px;
    width: 100%;
    height: 72px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    box-sizing: border-box;
  }

  .nav-brand {
    display: inline-flex !important;
    align-items: center !important;
    height: 100%;
    gap: 12px;
    text-decoration: none;
    cursor: pointer;
    vertical-align: middle;
    margin: 0;
    padding: 0;
  }

  .nav-logo-img {
    height: 36px;
    width: auto;
    object-fit: contain;
    display: block;
    vertical-align: middle;
    transition: transform 200ms ease;
  }

  .nav-brand:hover .nav-logo-img {
    transform: scale(1.06);
  }

  .nav-brand-text {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: 0.05em;
    display: inline-flex !important;
    align-items: center !important;
    line-height: 1 !important;
    vertical-align: middle;
  }

  .nav-links {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 16px;
    list-style: none;
    height: 100%;
    margin: 0 !important;
    padding: 0 !important;
  }

  @media (max-width: 960px) {
    .nav-links { display: none !important; }
  }

  .nav-links li {
    display: flex !important;
    align-items: center !important;
    height: 100%;
    margin: 0 !important;
    padding: 0 !important;
    list-style: none !important;
  }

  .nav-link {
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-dim);
    font-size: 0.92rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 180ms ease;
    font-family: 'DM Sans', sans-serif;
    text-decoration: none;
    padding: 0 16px;
    height: 38px;
    border-radius: 8px;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    vertical-align: middle;
    box-sizing: border-box;
    margin: 0;
  }

  .nav-link:hover {
    color: var(--accent-gold);
    background: rgba(180, 154, 90, 0.08);
  }

  .nav-link.active {
    color: var(--accent-gold);
    font-weight: 700;
    background: rgba(180, 154, 90, 0.12);
    border: 1px solid rgba(180, 154, 90, 0.35);
  }

  .nav-actions {
    display: inline-flex !important;
    align-items: center !important;
    height: 100%;
    gap: 12px;
    margin: 0;
    padding: 0;
  }

  /* Sun/Moon Theme Toggle Button */
  .theme-toggle-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 50%;
    width: 38px;
    height: 38px;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer;
    font-size: 1.15rem;
    line-height: 1 !important;
    transition: all 200ms ease;
    padding: 0 !important;
    margin: 0;
    color: var(--text-primary);
    box-sizing: border-box;
    vertical-align: middle;
  }

  .theme-toggle-btn:hover {
    border-color: var(--accent-gold);
    transform: scale(1.08) rotate(15deg);
    background: rgba(180, 154, 90, 0.12);
  }

  .theme-icon-sun, .theme-icon-moon {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    font-size: 1.15rem;
    pointer-events: none;
  }

  [data-theme="dark"] .theme-icon-sun { display: inline-flex !important; }
  [data-theme="dark"] .theme-icon-moon { display: none !important; }
  [data-theme="light"] .theme-icon-sun { display: none !important; }
  [data-theme="light"] .theme-icon-moon { display: inline-flex !important; }

  .nav-btn-ghost {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    padding: 0 18px;
    height: 38px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 180ms ease;
    text-decoration: none;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    font-family: 'DM Sans', sans-serif;
    box-sizing: border-box;
    margin: 0;
    vertical-align: middle;
  }

  .nav-btn-ghost:hover {
    border-color: var(--accent-gold);
    color: var(--accent-gold);
    background: rgba(180, 154, 90, 0.08);
  }

  .nav-btn-primary {
    background: var(--accent-gold);
    color: #101722;
    border: 1px solid var(--accent-gold);
    padding: 0 20px;
    height: 38px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 180ms ease;
    box-shadow: 0 2px 14px rgba(180, 154, 90, 0.25);
    text-decoration: none;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    font-family: 'DM Sans', sans-serif;
    box-sizing: border-box;
    margin: 0;
    vertical-align: middle;
  }

  .nav-btn-primary:hover {
    background: var(--accent-gold-hover);
    border-color: var(--accent-gold-hover);
    color: #101722;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(180, 154, 90, 0.4);
  }

  /* -------------------------------------------------------------
     CARD ANIMATIONS & COMMON UTILITIES
  ------------------------------------------------------------- */
  .animated-card {
    position: relative;
    overflow: hidden;
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    transition: transform 280ms cubic-bezier(0.16, 1, 0.3, 1),
                box-shadow 280ms cubic-bezier(0.16, 1, 0.3, 1),
                border-color 280ms ease,
                background-color 220ms ease;
  }

  .animated-card:hover {
    transform: translateY(-6px) scale(1.01);
    border-color: var(--border-gold) !important;
    box-shadow: 0 16px 40px rgba(180, 154, 90, 0.15), 0 0 1px rgba(180, 154, 90, 0.8) !important;
  }

  .animated-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    transition: left 650ms ease;
  }

  .animated-card:hover::before {
    left: 100%;
  }

  /* Live Pulse Indicators */
  @keyframes liveRadar {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(122, 155, 118, 0.7); }
    70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(122, 155, 118, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(122, 155, 118, 0); }
  }

  .live-pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-growth);
    display: inline-block;
    animation: liveRadar 2s infinite;
  }

  .brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 18px;
    background: rgba(180, 154, 90, 0.1);
    border: 1px solid var(--border-gold);
    border-radius: 100px;
    font-size: 0.8rem;
    color: var(--accent-gold);
    margin-bottom: 22px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
  }

  .section {
    width: 100%;
    position: relative;
    padding: 85px 32px;
    border-bottom: 1px solid var(--border-color);
  }

  .container {
    max-width: 1180px;
    width: 100%;
    margin: 0 auto;
    position: relative;
    z-index: 2;
  }

  h1, h2, h3, h4 {
    font-family: 'DM Sans', sans-serif;
    letter-spacing: -0.03em;
    font-weight: 700;
    color: var(--text-primary);
  }

  .gold-text {
    color: var(--accent-gold);
  }

  .muted-text {
    color: var(--text-muted);
    font-size: 1.15rem;
    line-height: 1.68;
    max-width: 720px;
  }

  .cta-primary {
    background: var(--accent-gold);
    color: #101722;
    border: 1px solid var(--accent-gold);
    padding: 14px 34px;
    border-radius: 8px;
    font-size: 1.02rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 200ms ease;
    box-shadow: 0 6px 26px rgba(180, 154, 90, 0.3);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    font-family: 'DM Sans', sans-serif;
  }

  .cta-primary:hover {
    background: var(--accent-gold-hover);
    border-color: var(--accent-gold-hover);
    color: #101722;
    transform: translateY(-2px);
    box-shadow: 0 10px 32px rgba(180, 154, 90, 0.45);
  }

  .cta-secondary {
    background: var(--surface-card);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    padding: 14px 30px;
    border-radius: 8px;
    font-size: 1.02rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 200ms ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Sans', sans-serif;
  }

  .cta-secondary:hover {
    border-color: var(--accent-gold);
    color: var(--accent-gold);
    transform: translateY(-2px);
  }

  .cta-banner {
    background: var(--surface-card);
    border: 1px solid var(--border-gold);
    border-radius: 16px;
    padding: 56px 32px;
    text-align: center;
    margin: 60px 0 0 0;
  }

  /* -------------------------------------------------------------
     ENTERPRISE FOOTER
  ------------------------------------------------------------- */
  .site-footer {
    background-color: var(--footer-bg);
    border-top: 1px solid var(--border-color);
    padding: 60px 32px 28px 32px;
    width: 100%;
    margin: 0;
    transition: background-color 220ms ease;
  }

  .footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 48px;
    max-width: 1180px;
    margin: 0 auto;
  }

  @media (max-width: 900px) {
    .footer-grid { grid-template-columns: 1fr 1fr; }
  }
  @media (max-width: 600px) {
    .footer-grid { grid-template-columns: 1fr; }
  }

  .footer-col-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--accent-gold);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 18px;
  }

  .footer-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 11px;
  }

  .footer-list a {
    color: var(--text-dim);
    text-decoration: none;
    font-size: 0.88rem;
    transition: color 150ms ease;
    cursor: pointer;
  }

  .footer-list a:hover {
    color: var(--text-primary);
  }

  .footer-bottom {
    max-width: 1180px;
    margin: 48px auto 0 auto;
    padding-top: 22px;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 0.82rem;
    color: var(--text-dim);
  }

  .footer-bottom a {
    color: var(--text-dim);
    text-decoration: none;
    margin-left: 20px;
  }

  .footer-bottom a:hover {
    color: var(--accent-gold);
  }

  .reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 350ms cubic-bezier(0.16, 1, 0.3, 1), transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
  }

  .reveal.active {
    opacity: 1;
    transform: translateY(0);
  }
</style>
"""


def get_public_navbar(active_page: str = "landing") -> str:
    """
    Renders the unified Glassmorphic Top Navbar with:
    - Home → How It Works → Product
    - Dark / Light Mode Sun & Moon Toggle button
    - Sign In and Register → actions
    - Dual Light & Dark Mode official brand logos
    - Perfectly centered vertical alignment
    """
    logo_dark_icon = get_logo_dark_icon_b64()
    logo_light_icon = get_logo_light_icon_b64()

    is_landing = "active" if active_page in ["landing", "home"] else ""
    is_hiw = "active" if active_page == "how_it_works" else ""
    is_prod = "active" if active_page == "product" else ""

    return f"""
  <nav class="top-navbar">
    <div class="nav-container">
      <a href="?page=landing" class="nav-brand" data-page="landing">
        <img src="{logo_dark_icon}" alt="Arctus" class="nav-logo-img logo-dark" />
        <img src="{logo_light_icon}" alt="Arctus" class="nav-logo-img logo-light" />
        <span class="nav-brand-text">ARCTUS</span>
      </a>

      <!-- 3-PAGE PUBLIC REALM NAVIGATION (Home → How It Works → Product) -->
      <ul class="nav-links">
        <li><a href="?page=landing" class="nav-link {is_landing}" data-page="landing">Home</a></li>
        <li><a href="?page=how_it_works" class="nav-link {is_hiw}" data-page="how_it_works">How It Works</a></li>
        <li><a href="?page=product" class="nav-link {is_prod}" data-page="product">Product</a></li>
      </ul>

      <div class="nav-actions">
        <!-- Sun & Moon Dark / Light Mode Toggle Button -->
        <button id="themeToggleBtn" class="theme-toggle-btn" data-theme-toggle="true" onclick="window.toggleTheme ? window.toggleTheme() : (function(){{ var t = (document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light'); document.documentElement.setAttribute('data-theme', t); document.body.setAttribute('data-theme', t); document.querySelectorAll('.arctus-landing-wrapper, .arctus-public-wrapper, [class*=\\'stApp\\']').forEach(function(el){{ el.setAttribute('data-theme', t); }}); try{{localStorage.setItem('arctus_theme', t);}}catch(e){{}} }})()" title="Toggle Dark / Light Mode" aria-label="Toggle theme">
          <span class="theme-icon-sun">☀️</span>
          <span class="theme-icon-moon">🌙</span>
        </button>

        <a href="?page=login" class="nav-btn-ghost" data-page="login">Sign In</a>
        <a href="?page=register" class="nav-btn-primary" data-page="register">Register →</a>
      </div>
    </div>
  </nav>
"""


def get_public_footer() -> str:
    """Renders the comprehensive 4-column enterprise footer with dual logos."""
    logo_dark_full = get_logo_dark_full_b64()
    logo_light_full = get_logo_light_full_b64()

    return f"""
  <footer class="site-footer">
    <div class="footer-grid">
      <!-- Col 1: Brand & Mission -->
      <div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
          <img src="{logo_dark_full}" alt="Arctus" class="logo-dark" style="height: 48px; width: auto;" />
          <img src="{logo_light_full}" alt="Arctus" class="logo-light" style="height: 48px; width: auto;" />
        </div>
        <p style="color: var(--text-dim); font-size: 0.88rem; line-height: 1.6; margin-bottom: 18px;">
          Institutional-grade FP&A stress-testing platform built for Indian mid-market CFOs and finance leaders (₹25 Cr – ₹500 Cr). Grounded in live RBI repo rates and MoSPI inflation telemetry.
        </p>
        <div style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.8rem; color: var(--color-growth);">
          <span class="live-pulse-dot"></span>
          Systems Operational • RBI & MoSPI Live Feeds
        </div>
      </div>

      <!-- Col 2: Public Navigation -->
      <div>
        <div class="footer-col-title">Navigation</div>
        <ul class="footer-list">
          <li><a href="?page=landing" data-page="landing">Home</a></li>
          <li><a href="?page=how_it_works" data-page="how_it_works">How It Works</a></li>
          <li><a href="?page=product" data-page="product">Product</a></li>
          <li><a href="?page=login" data-page="login">Login</a></li>
          <li><a href="?page=register" data-page="register">Register</a></li>
        </ul>
      </div>

      <!-- Col 3: Macro Telemetry -->
      <div>
        <div class="footer-col-title">Macro Telemetry</div>
        <ul class="footer-list">
          <li><a href="?page=product" data-page="product">RBI Policy Repo Rate (6.50%)</a></li>
          <li><a href="?page=product" data-page="product">MoSPI Headline CPI (4.85%)</a></li>
          <li><a href="?page=product" data-page="product">ICE Brent Crude Spot ($74.50)</a></li>
          <li><a href="?page=product" data-page="product">10-Year G-Sec Benchmarks (7.02%)</a></li>
          <li><a href="?page=product" data-page="product">Lakhs / Crores Formatting</a></li>
        </ul>
      </div>

      <!-- Col 4: Developers & Platform -->
      <div>
        <div class="footer-col-title">Developers & Platform</div>
        <ul class="footer-list">
          <li><a href="?page=api_docs" data-page="api_docs">REST API Reference</a></li>
          <li><a href="?page=api_docs" data-page="api_docs">POST /api/forecast</a></li>
          <li><a href="?page=api_docs" data-page="api_docs">GET /api/macro</a></li>
          <li><a href="?page=dashboard" data-page="dashboard">Live CFO Simulator</a></li>
          <li><a href="?page=login" data-page="login">Instant Demo Access</a></li>
        </ul>
      </div>
    </div>

    <!-- Bottom Copyright Bar -->
    <div class="footer-bottom">
      <div>
        © 2026 Arctus Technologies Pvt. Ltd. All rights reserved. &nbsp;|&nbsp; Built for Indian CFOs (#101722 • #F4F1E8 • #B49A5A).
      </div>
      <div>
        <a href="javascript:void(0)">Privacy Policy</a>
        <a href="javascript:void(0)">Terms of Service</a>
        <a href="javascript:void(0)">Security & Compliance</a>
        <a href="?page=api_docs" data-page="api_docs">API Docs</a>
      </div>
    </div>
  </footer>
"""


def get_public_scripts() -> str:
    """Returns the shared JavaScript navigation interceptor, theme manager, and scroll observer."""
    return """
<script>
  // Theme Management (Dark / Light with Sun & Moon toggle)
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('arctus_theme', theme);
    } catch(e) {}

    // Synchronize parent frame and wrapper nodes if in iframe/stApp
    try {
      if (window.top && window.top.document) {
        window.top.document.documentElement.setAttribute('data-theme', theme);
        window.top.document.body.setAttribute('data-theme', theme);
      }
    } catch(e) {}
    try {
      if (window.parent && window.parent.document) {
        window.parent.document.documentElement.setAttribute('data-theme', theme);
        window.parent.document.body.setAttribute('data-theme', theme);
      }
    } catch(e) {}

    const wrappers = document.querySelectorAll('.arctus-public-wrapper, .arctus-landing-wrapper, [class*="stApp"], [data-testid="stAppViewContainer"]');
    wrappers.forEach(w => w.setAttribute('data-theme', theme));

    // Notify any canvas renderers
    window.dispatchEvent(new CustomEvent('arctusThemeChanged', { detail: { theme } }));
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || (function() {
      try { return localStorage.getItem('arctus_theme'); } catch(e) { return null; }
    })() || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  }

  // Bind to global window so inline onclicks can always find them
  window.applyTheme = applyTheme;
  window.toggleTheme = toggleTheme;

  // Global delegated click listener for theme toggle
  document.addEventListener('click', function(e) {
    const toggle = e.target.closest('#themeToggleBtn, .theme-toggle-btn, [data-theme-toggle]');
    if (toggle) {
      e.preventDefault();
      e.stopPropagation();
      toggleTheme();
    }
  }, true);

  // Self-executing theme initializer
  (function initTheme() {
    let savedTheme = 'dark';
    try {
      savedTheme = localStorage.getItem('arctus_theme') || 'dark';
    } catch(e) {}
    applyTheme(savedTheme);
  })();

  // Universal Bulletproof Navigation Handler
  function navigateToPage(page) {
    try {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set('page', page);
      window.location.href = currentUrl.toString();
    } catch(e) {
      window.location.href = '/?page=' + page;
    }
  }

  // Intercept all data-page clicks
  document.addEventListener('click', function(e) {
    const link = e.target.closest('a[data-page], button[data-page]');
    if (link) {
      const page = link.getAttribute('data-page');
      if (page) {
        e.preventDefault();
        navigateToPage(page);
      }
    }
  });

  // Scroll-Triggered Reveal via IntersectionObserver
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        if (typeof triggerCurveAnimation === 'function') {
          triggerCurveAnimation();
        }
      }
    });
  }, { threshold: 0.10 });

  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
</script>
"""
