"""
How It Works Page for Arctus.
Comprehensive 4-stage architectural pipeline walkthrough and Excel vs. Arctus comparison.
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


def get_how_it_works_html() -> str:
    """Returns the standalone HTML for the How It Works page."""
    logo_icon = get_logo_icon_b64()

    return f"""
{get_public_css()}

<style>
  /* Dedicated Page Styling for How It Works */
  .hiw-hero {{
    padding: 130px 32px 60px 32px;
    text-align: center;
    background: radial-gradient(circle at 50% 20%, var(--surface-card) 0%, var(--bg-base) 75%);
    border-bottom: 1px solid var(--border-color);
    position: relative;
    overflow: hidden;
  }}

  .hiw-hero::before {{
    content: '';
    position: absolute;
    top: 0; left: 20%; width: 60%; height: 260px;
    background: radial-gradient(ellipse at top, rgba(180, 154, 90, 0.12), transparent 70%);
    pointer-events: none;
  }}

  .hiw-title {{
    font-size: clamp(2.4rem, 4.5vw, 3.8rem);
    line-height: 1.15;
    margin-bottom: 20px;
    font-weight: 800;
  }}

  .pipeline-stage {{
    display: grid;
    grid-template-columns: 80px 1fr 1fr;
    gap: 36px;
    align-items: center;
    padding: 48px 0;
    border-bottom: 1px solid rgba(229, 229, 229, 0.08);
  }}

  @media (max-width: 900px) {{
    .pipeline-stage {{
      grid-template-columns: 1fr;
      gap: 20px;
    }}
  }}

  .stage-number-box {{
    width: 72px;
    height: 72px;
    border-radius: 16px;
    background: var(--surface-card);
    border: 1px solid var(--border-gold);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--accent-gold);
    box-shadow: 0 0 25px rgba(180, 154, 90, 0.2);
  }}

  .stage-info h3 {{
    font-size: 1.55rem;
    margin-bottom: 12px;
    color: var(--text-primary);
  }}

  .stage-info p {{
    color: var(--text-dim);
    font-size: 1.02rem;
    line-height: 1.65;
    margin-bottom: 16px;
  }}

  .stage-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }}

  .stage-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 0.78rem;
    color: var(--text-muted);
  }}

  .stage-tag strong {{
    color: var(--accent-gold);
  }}

  .stage-visual-card {{
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
    position: relative;
    overflow: hidden;
  }}

  .code-pill {{
    font-family: 'Geist Mono', monospace;
    font-size: 0.82rem;
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(180, 154, 90, 0.25);
    padding: 12px 16px;
    border-radius: 8px;
    color: #E5E5E5;
    line-height: 1.5;
  }}

  /* Comparison Matrix Table */
  .comparison-table-wrapper {{
    margin-top: 48px;
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 16px 45px rgba(0,0,0,0.5);
  }}

  .comparison-table {{
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.95rem;
  }}

  .comparison-table th {{
    padding: 20px 24px;
    background: var(--surface-sunken);
    border-bottom: 1px solid var(--border-color);
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.82rem;
    color: var(--text-dim);
  }}

  .comparison-table th.highlight-col {{
    color: var(--accent-gold);
    background: rgba(180, 154, 90, 0.08);
    border-bottom: 1px solid var(--border-gold);
  }}

  .comparison-table td {{
    padding: 18px 24px;
    border-bottom: 1px solid rgba(229, 229, 229, 0.06);
    color: var(--text-muted);
    vertical-align: middle;
  }}

  .comparison-table td.highlight-col {{
    background: rgba(180, 154, 90, 0.04);
    color: var(--text-primary);
    font-weight: 600;
  }}

  .comparison-table tr:hover td {{
    background: rgba(255, 255, 255, 0.02);
  }}

  .comparison-table tr:hover td.highlight-col {{
    background: rgba(180, 154, 90, 0.07);
  }}

  .check-icon {{
    color: var(--color-growth);
    font-weight: 700;
    margin-right: 6px;
  }}

  .cross-icon {{
    color: var(--color-recession);
    font-weight: 700;
    margin-right: 6px;
  }}
</style>

<div class="arctus-public-wrapper">

  <!-- TOP NAVBAR -->
  {get_public_navbar(active_page="how_it_works")}

  <!-- HERO SECTION -->
  <section class="hiw-hero">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">ARCHITECTURE & METHODOLOGY</span>
        <h1 class="hiw-title">
          From Raw Financials to <br>
          <span class="gold-text">CFO Certainty in 30 Seconds</span>
        </h1>
        <p class="muted-text" style="margin: 0 auto;">
          How Arctus replaces 2–3 days of fragile, disconnected Excel formulas with a vectorized,
          macro-grounded Monte Carlo engine built specifically for Indian mid-market enterprises.
        </p>
      </div>
    </div>
  </section>

  <!-- 4-STAGE PIPELINE WALKTHROUGH -->
  <section class="section">
    <div class="container">
      <div style="text-align: center; margin-bottom: 48px;">
        <span class="brand-badge">4-STAGE PIPELINE</span>
        <h2 style="font-size: 2.3rem;">The End-to-End Simulation Architecture</h2>
        <p class="muted-text" style="margin: 12px auto 0 auto; font-size: 1rem;">
          Every forecast run passes through four deterministic, statistically validated stages.
        </p>
      </div>

      <!-- STAGE 1 -->
      <div class="pipeline-stage reveal">
        <div class="stage-number-box">01</div>
        <div class="stage-info">
          <h3>Multi-Period Ingestion & Currency Normalization</h3>
          <p>
            Drop in your raw historical P&L spreadsheet in Excel (.xlsx, .xls) or CSV format. Arctus automatically handles messy corporate headers, multi-period quarterly columns, and converts between Crores, Lakhs, and Raw Rupees without formula truncation.
          </p>
          <div class="stage-tags">
            <span class="stage-tag"><strong>Formats:</strong> XLSX, XLS, CSV</span>
            <span class="stage-tag"><strong>Currency:</strong> ₹ Crores & Lakhs Detection</span>
            <span class="stage-tag"><strong>Integrity:</strong> Zero-Loss Audit Check</span>
          </div>
        </div>
        <div class="stage-visual-card animated-card">
          <div style="font-size: 0.78rem; color: var(--accent-gold); margin-bottom: 8px; font-weight: 600;">
            INGESTION ENGINE DIAGNOSTIC
          </div>
          <div class="code-pill">
            &gt; Parsing 5-Year Quarterly P&L (FY20 to FY25)...<br>
            &gt; Currency detected: <span style="color: var(--accent-gold)">Crores (₹ in Cr)</span><br>
            &gt; Periods mapped: 20 Historical Quarters<br>
            &gt; Integrity Check: <span style="color: var(--color-growth)">PASS (Net Margin Math Validated)</span>
          </div>
        </div>
      </div>

      <!-- STAGE 2 -->
      <div class="pipeline-stage reveal">
        <div class="stage-number-box">02</div>
        <div class="stage-info">
          <h3>RapidFuzz Indian GAAP Schema Reconciliation</h3>
          <p>
            Indian mid-market companies use widely different chart of accounts. Using Levenshtein distance and token-sort fuzzy matching algorithms, Arctus maps custom ledger names to standardized Ind AS / GAAP line items with >95% confidence.
          </p>
          <div class="stage-tags">
            <span class="stage-tag"><strong>Algorithm:</strong> RapidFuzz Levenshtein</span>
            <span class="stage-tag"><strong>Standard:</strong> Ind AS / Schedule III P&L</span>
            <span class="stage-tag"><strong>Confidence:</strong> 98.4% Average Match</span>
          </div>
        </div>
        <div class="stage-visual-card animated-card">
          <div style="font-size: 0.78rem; color: var(--accent-gold); margin-bottom: 8px; font-weight: 600;">
            SEMANTIC SCHEMA RECONCILIATION
          </div>
          <div class="code-pill">
            "Sales Turnover Domestic" ➔ <span style="color: #7A9B76">Revenue from Operations [98%]</span><br>
            "Cost of Raw Material Consumed" ➔ <span style="color: #7A9B76">COGS / Material Cost [96%]</span><br>
            "Salary, Wages & Bonus" ➔ <span style="color: #7A9B76">Employee Benefit Expenses [99%]</span><br>
            "Term Loan Interest" ➔ <span style="color: #7A9B76">Finance Costs [95%]</span>
          </div>
        </div>
      </div>

      <!-- STAGE 3 -->
      <div class="pipeline-stage reveal">
        <div class="stage-number-box">03</div>
        <div class="stage-info">
          <h3>Correlated Vectorized Monte Carlo Engine</h3>
          <p>
            Instead of 3 simplistic linear Excel cases (Base, Bull, Bear), Arctus runs 1,000 to 10,000 simultaneous simulation vectors in milliseconds. A Cholesky decomposition of the covariance matrix preserves empirical correlations between cost inflation, interest rate hikes, and sales volume shocks.
          </p>
          <div class="stage-tags">
            <span class="stage-tag"><strong>Execution:</strong> NumPy Vectorized Arrays</span>
            <span class="stage-tag"><strong>Correlation:</strong> Cholesky Covariance Matrix</span>
            <span class="stage-tag"><strong>Macro Sync:</strong> Live RBI Repo & MoSPI CPI</span>
          </div>
        </div>
        <div class="stage-visual-card animated-card">
          <div style="font-size: 0.78rem; color: var(--accent-gold); margin-bottom: 8px; font-weight: 600;">
            VECTORIZED SIMULATION METRICS
          </div>
          <div class="code-pill">
            &gt; Vectors: 1,000 Correlated Stochastic Paths<br>
            &gt; Execution Latency: <span style="color: var(--accent-gold)">38.2 ms (Parallel In-Memory)</span><br>
            &gt; Macro Factors: RBI Repo 6.50%, CPI 4.85%, Crude $74.5<br>
            &gt; Covariance Matrix: Cholesky Decomposed (L · Lᵀ)
          </div>
        </div>
      </div>

      <!-- STAGE 4 -->
      <div class="pipeline-stage reveal" style="border-bottom: none;">
        <div class="stage-number-box">04</div>
        <div class="stage-info">
          <h3>CFO Prescriptive Analytics & Waterfall Bridges</h3>
          <p>
            Forecast results are instantly transformed into actionable CFO dashboards: P10/P50/P90 percentile fan distributions, margin erosion waterfall bridges, loan covenant breach probability warnings (Interest Coverage &lt; 2.0x), and executive board summaries.
          </p>
          <div class="stage-tags">
            <span class="stage-tag"><strong>Visuals:</strong> Fan Charts & Waterfall Bridges</span>
            <span class="stage-tag"><strong>Covenants:</strong> DSCR & ICR Threshold Watch</span>
            <span class="stage-tag"><strong>Export:</strong> One-Click PDF & Excel Reports</span>
          </div>
        </div>
        <div class="stage-visual-card animated-card">
          <div style="font-size: 0.78rem; color: var(--accent-gold); margin-bottom: 8px; font-weight: 600;">
            EXECUTIVE BOARDROOM SYNTHESIS
          </div>
          <div class="code-pill">
            &gt; Base Case (P50 EBITDA): <span style="color: var(--accent-gold)">₹32.40 Cr (14.2% Margin)</span><br>
            &gt; Severe Stress (P10 EBITDA): <span style="color: var(--color-recession)">₹21.15 Cr (9.8% Margin)</span><br>
            &gt; Bank Covenant Watch: <span style="color: var(--color-growth)">ICR 3.42x &gt; Minimum 2.0x (SAFE)</span><br>
            &gt; Margin Erosion Driver: 62% driven by Raw Material Spike
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- COMPARISON SECTION: EXCEL VS ARCTUS -->
  <section class="section" style="background: var(--bg-base);">
    <div class="container">
      <div style="text-align: center; margin-bottom: 36px;">
        <span class="brand-badge">THE QUANTITATIVE ADVANTAGE</span>
        <h2 style="font-size: 2.3rem;">Excel Financial Models vs. Arctus</h2>
        <p class="muted-text" style="margin: 12px auto 0 auto; font-size: 1rem;">
          Why leading Indian mid-market CFOs are transitioning their quarterly planning from legacy workbooks to Arctus.
        </p>
      </div>

      <div class="comparison-table-wrapper animated-card reveal">
        <table class="comparison-table">
          <thead>
            <tr>
              <th style="width: 25%;">Planning Dimension</th>
              <th style="width: 37%;">Traditional Excel Scenario Modeling</th>
              <th style="width: 38%;" class="highlight-col">⚡ Arctus Vectorized Platform</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Cycle Turnaround Time</strong></td>
              <td><span class="cross-icon">✕</span> 2 to 3 days of manual formula adjustments and table re-linking</td>
              <td class="highlight-col"><span class="check-icon">✓</span> <strong>30 seconds</strong> automated end-to-end execution</td>
            </tr>
            <tr>
              <td><strong>Simulation Breadth</strong></td>
              <td><span class="cross-icon">✕</span> 3 static scenarios (Base, Best, Worst) with arbitrary % guesses</td>
              <td class="highlight-col"><span class="check-icon">✓</span> <strong>1,000+ continuous stochastic paths</strong> with P10/P50/P90 bands</td>
            </tr>
            <tr>
              <td><strong>Correlation Rigor</strong></td>
              <td><span class="cross-icon">✕</span> Disconnected line-by-line formulas ignoring macroeconomic contagion</td>
              <td class="highlight-col"><span class="check-icon">✓</span> <strong>Cholesky Covariance Matrix</strong> preserving macro-financial correlation</td>
            </tr>
            <tr>
              <td><strong>Macroeconomic Context</strong></td>
              <td><span class="cross-icon">✕</span> Static assumptions typed into cells, rarely refreshed in real-time</td>
              <td class="highlight-col"><span class="check-icon">✓</span> <strong>Live telemetry feeds</strong> from RBI Repo Rate and MoSPI CPI inflation</td>
            </tr>
            <tr>
              <td><strong>Covenant Stress Testing</strong></td>
              <td><span class="cross-icon">✕</span> Manual single-point checks prone to formula corruption</td>
              <td class="highlight-col"><span class="check-icon">✓</span> <strong>Probabilistic covenant breach alerts</strong> (e.g. 12.4% risk of ICR &lt; 2.0x)</td>
            </tr>
            <tr>
              <td><strong>Data Sovereignty & Governance</strong></td>
              <td><span class="cross-icon">✕</span> Fragile files emailed across departments with broken VLOOKUPs</td>
              <td class="highlight-col"><span class="check-icon">✓</span> <strong>Enterprise database persistence</strong>, audit logs, and REST API access</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- CTA BANNER -->
      <div class="cta-banner animated-card reveal">
        <h2 style="font-size: 2.1rem; margin-bottom: 14px;">
          Ready to eliminate 3 days of manual scenario modeling?
        </h2>
        <p class="muted-text" style="margin: 0 auto 28px auto; font-size: 1rem;">
          Test your company's P&L against live RBI interest rate decisions and raw material inflation right now.
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


def render_how_it_works_page(on_navigate):
    """Renders the full-bleed How It Works page."""
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

    html_content = get_how_it_works_html()
    st.html(html_content, unsafe_allow_javascript=True)
