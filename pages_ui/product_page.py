"""
Product Capabilities Page for Arctus.
Deep-dive into platform modules, quantitative engine specs, and Indian mid-market design.
Full-bleed Black & Gold Elegance layout using native st.html.
"""

import streamlit as st
from components.public_ui import (
    get_public_css,
    get_public_navbar,
    get_public_footer,
    get_public_scripts,
)
from core.assets import get_logo_icon_b64


def get_product_html() -> str:
    """Returns the standalone HTML for the Product page."""
    logo_icon = get_logo_icon_b64()

    return f"""
{get_public_css()}

<style>
  /* Dedicated Page Styling for Product */
  .product-hero {{
    padding: 130px 32px 60px 32px;
    text-align: center;
    background: radial-gradient(circle at 50% 20%, var(--surface-card) 0%, var(--bg-base) 75%);
    border-bottom: 1px solid var(--border-color);
    position: relative;
    overflow: hidden;
  }}

  .product-hero::before {{
    content: '';
    position: absolute;
    top: 0; left: 20%; width: 60%; height: 260px;
    background: radial-gradient(ellipse at top, rgba(180, 154, 90, 0.12), transparent 70%);
    pointer-events: none;
  }}

  .product-title {{
    font-size: clamp(2.4rem, 4.5vw, 3.8rem);
    line-height: 1.15;
    margin-bottom: 20px;
    font-weight: 800;
  }}

  .modules-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
    margin-top: 40px;
  }}

  @media (max-width: 1024px) {{
    .modules-grid {{ grid-template-columns: repeat(2, 1fr); }}
  }}
  @media (max-width: 680px) {{
    .modules-grid {{ grid-template-columns: 1fr; }}
  }}

  .module-card {{
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 32px 26px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 250ms ease, border-color 250ms ease, box-shadow 250ms ease;
  }}

  .module-icon-wrap {{
    width: 52px;
    height: 52px;
    border-radius: 12px;
    background: rgba(180, 154, 90, 0.1);
    border: 1px solid var(--border-gold);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    color: var(--accent-gold);
    margin-bottom: 20px;
  }}

  .module-card h3 {{
    font-size: 1.35rem;
    margin-bottom: 12px;
    color: var(--text-primary);
  }}

  .module-card p {{
    color: var(--text-dim);
    font-size: 0.94rem;
    line-height: 1.62;
    margin-bottom: 20px;
  }}

  .module-feature-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 16px;
  }}

  .module-feature-list li {{
    font-size: 0.82rem;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .module-feature-list li::before {{
    content: '▪';
    color: var(--accent-gold);
  }}

  /* Specs Grid */
  .specs-container {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-top: 36px;
  }}

  @media (max-width: 900px) {{
    .specs-container {{ grid-template-columns: 1fr 1fr; }}
  }}
  @media (max-width: 520px) {{
    .specs-container {{ grid-template-columns: 1fr; }}
  }}

  .spec-box {{
    background: var(--surface-sunken);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
  }}

  .spec-value {{
    font-family: 'DM Sans', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--accent-gold);
    margin-bottom: 6px;
  }}

  .spec-title {{
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
  }}

  .spec-desc {{
    font-size: 0.78rem;
    color: var(--text-dim);
    line-height: 1.4;
  }}
</style>

<div class="arctus-public-wrapper">

  <!-- TOP NAVBAR -->
  {get_public_navbar(active_page="product")}

  <!-- HERO SECTION -->
  <section class="product-hero">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">PRODUCT SUITE & CAPABILITIES</span>
        <h1 class="product-title">
          The Quantitative Engine Built for <br>
          <span class="gold-text">India's ₹25–₹500 Cr Mid-Market</span>
        </h1>
        <p class="muted-text" style="margin: 0 auto;">
          An institutional-grade FP&A platform combining correlated Monte Carlo simulation, live RBI macroeconomic feeds,
          and Ind AS financial schema alignment into a sub-second executive workbench.
        </p>
      </div>
    </div>
  </section>

  <!-- 6 CORE MODULES SECTION -->
  <section class="section">
    <div class="container">
      <div style="text-align: center; margin-bottom: 12px;">
        <span class="brand-badge">CORE CAPABILITIES</span>
        <h2 style="font-size: 2.3rem;">Engineered Across Six Pillars</h2>
        <p class="muted-text" style="margin: 12px auto 0 auto; font-size: 1rem;">
          Every module is purpose-built to address the real-world operational challenges of Indian manufacturing, distribution, and services enterprises.
        </p>
      </div>

      <div class="modules-grid">
        <!-- Module 1: Monte Carlo Engine -->
        <div class="module-card animated-card reveal">
          <div>
            <div class="module-icon-wrap">⚡</div>
            <h3>Vectorized Monte Carlo Engine</h3>
            <p>
              Computes 1,000 to 10,000 stochastic simulation trajectories in under 40 milliseconds using vectorized NumPy tensor mathematics. Preserves macroeconomic cross-variable dependencies through Cholesky decomposition of empirical covariance.
            </p>
          </div>
          <ul class="module-feature-list">
            <li>NumPy in-memory parallel matrix computation</li>
            <li>Cholesky covariance decomposition</li>
            <li>P10, P50 (Base), and P90 confidence spreads</li>
            <li>Extreme tail-risk probability calculation</li>
          </ul>
        </div>

        <!-- Module 2: Live Macro Telemetry -->
        <div class="module-card animated-card reveal" style="transition-delay: 60ms;">
          <div>
            <div class="module-icon-wrap">📡</div>
            <h3>Live Indian Macro Telemetry Hub</h3>
            <p>
              Direct live connectors to the Reserve Bank of India (RBI) repo rate, Ministry of Statistics & Programme Implementation (MoSPI) CPI inflation index, ICE Brent crude benchmarks, and 10-year Indian G-Sec sovereign debt curves.
            </p>
          </div>
          <ul class="module-feature-list">
            <li>RBI Policy Repo Rate: 6.50%</li>
            <li>MoSPI Headline CPI: 4.85%</li>
            <li>ICE Brent Crude Oil: $74.50 / barrel</li>
            <li>10Y G-Sec Sovereign Benchmark: 7.02%</li>
          </ul>
        </div>

        <!-- Module 3: Visualization & Waterfalls -->
        <div class="module-card animated-card reveal" style="transition-delay: 120ms;">
          <div>
            <div class="module-icon-wrap">📊</div>
            <h3>CFO Visualization & Waterfall Suite</h3>
            <p>
              Board-ready visual analytics including interactive fan charts with shaded confidence cones, margin erosion waterfall bridges isolating cost inflation vs. interest rate impact, and dynamic sensitivity tornado charts.
            </p>
          </div>
          <ul class="module-feature-list">
            <li>Interactive fan chart confidence cones</li>
            <li>EBITDA & Net Profit margin erosion bridges</li>
            <li>Tornado diagrams for driver sensitivity</li>
            <li>One-click export to Boardroom PDF & Excel</li>
          </ul>
        </div>

        <!-- Module 4: Ind AS & Indian GAAP -->
        <div class="module-card animated-card reveal" style="transition-delay: 180ms;">
          <div>
            <div class="module-icon-wrap">🏛️</div>
            <h3>Indian GAAP & Ind AS Compliance</h3>
            <p>
              Specifically aligned to Indian Schedule III corporate reporting standards. Native support for ₹ Crores and ₹ Lakhs notation, Section 115BAA corporate tax regime (25.17%), and RapidFuzz reconciliation of custom ERP account ledgers.
            </p>
          </div>
          <ul class="module-feature-list">
            <li>Native ₹ Crores & Lakhs numerical formatting</li>
            <li>Corporate Tax Section 115BAA (25.17%)</li>
            <li>RapidFuzz semantic ledger mapping (&gt;95%)</li>
            <li>Turnover tiers: ₹25 Cr – ₹500 Cr+</li>
          </ul>
        </div>

        <!-- Module 5: High-Throughput REST API -->
        <div class="module-card animated-card reveal" style="transition-delay: 240ms;">
          <div>
            <div class="module-icon-wrap">🔌</div>
            <h3>High-Throughput REST API</h3>
            <p>
              Integrate quantitative stress-testing directly into your existing enterprise stack. Exposes clean JSON endpoints for programmatic forecast execution, real-time macro telemetry, and ERP data pipelines (SAP, Tally, Zoho Books).
            </p>
          </div>
          <ul class="module-feature-list">
            <li>POST /api/forecast (sub-50ms execution)</li>
            <li>GET /api/macro (live telemetry feeds)</li>
            <li>Interactive Swagger & OpenAPI documentation</li>
            <li>ERP connectors for SAP, Tally Prime, Zoho</li>
          </ul>
        </div>

        <!-- Module 6: Data Sovereignty -->
        <div class="module-card animated-card reveal" style="transition-delay: 300ms;">
          <div>
            <div class="module-icon-wrap">🔒</div>
            <h3>Enterprise Security & Sovereignty</h3>
            <p>
              Strict adherence to Indian data sovereignty standards. All financial P&L models remain confidential, encrypted with AES-256 at rest and TLS 1.3 in transit. Zero data ingestion by third-party public AI providers.
            </p>
          </div>
          <ul class="module-feature-list">
            <li>AES-256 encryption at rest, TLS 1.3 in transit</li>
            <li>Compliant with Indian RBI data localization</li>
            <li>Zero training on third-party commercial LLMs</li>
            <li>Deployable on-premise or sovereign Indian cloud</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- PERFORMANCE & ARCHITECTURE SPECS -->
  <section class="section" style="background: var(--bg-base);">
    <div class="container">
      <div style="text-align: center; margin-bottom: 24px;">
        <span class="brand-badge">PERFORMANCE BENCHMARKS</span>
        <h2 style="font-size: 2.3rem;">Engineered for Sub-Second Precision</h2>
        <p class="muted-text" style="margin: 12px auto 0 auto; font-size: 1rem;">
          Architectural benchmarks measured across enterprise P&L datasets.
        </p>
      </div>

      <div class="specs-container reveal">
        <div class="spec-box animated-card">
          <div class="spec-value">&lt; 40 ms</div>
          <div class="spec-title">Simulation Latency</div>
          <div class="spec-desc">1,000 correlated Monte Carlo paths computed in-memory via NumPy</div>
        </div>

        <div class="spec-box animated-card">
          <div class="spec-value">&gt; 98.4%</div>
          <div class="spec-title">Schema Match Accuracy</div>
          <div class="spec-desc">RapidFuzz Levenshtein matching on custom enterprise ledger lines</div>
        </div>

        <div class="spec-box animated-card">
          <div class="spec-value">30 Sec</div>
          <div class="spec-title">Full Workflow Speed</div>
          <div class="spec-desc">From raw multi-period spreadsheet upload to executive dashboard</div>
        </div>

        <div class="spec-box animated-card">
          <div class="spec-value">100%</div>
          <div class="spec-title">Data Sovereignty</div>
          <div class="spec-desc">Zero external AI dependencies; self-contained mathematical engine</div>
        </div>
      </div>

      <!-- CTA BANNER -->
      <div class="cta-banner animated-card reveal" style="margin-top: 56px;">
        <h2 style="font-size: 2.1rem; margin-bottom: 14px;">
          Empower your finance team with quantitative certainty
        </h2>
        <p class="muted-text" style="margin: 0 auto 28px auto; font-size: 1rem;">
          Eliminate manual spreadsheet errors and present stress-tested quarterly forecasts to your Board of Directors.
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
          <a href="?page=dashboard" class="cta-primary" data-page="dashboard">
            ⚡ Launch CFO Simulator →
          </a>
          <a href="?page=register" class="cta-secondary" data-page="register">
            Register Enterprise Account
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- ENTERPRISE FOOTER -->
  {get_public_footer()}

</div>

{get_public_scripts()}
"""


def render_product_page(on_navigate):
    """Renders the full-bleed Product page."""
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
        </style>
        """,
        unsafe_allow_html=True
    )

    html_content = get_product_html()
    st.html(html_content, unsafe_allow_javascript=True)
