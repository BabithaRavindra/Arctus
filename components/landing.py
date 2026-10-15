"""
Landing Page Component for Arctus.
Institutional FP&A Stress-Testing Platform for Indian Mid-Market Enterprises.

Key Architecture Features:
- Native DOM embedding via st.html (no iframe sandbox, natural content height, zero bottom blank void)
- Bulletproof page navigation via native <a href="?page=..."> links + universal JavaScript routing
- Fixed glassmorphic top navigation bar with native CSS scroll-margin smooth anchor scrolling
- Unique Hero Animations:
  * Liquid molten-gold typography shimmer gradient
  * Official Arctus emblem with breathing radial energy halo
  * Floating glassmorphic holographic telemetry badges (1,000 paths, RBI Repo 6.50%, ₹500 Cr tested)
  * Real-time Monte Carlo wave simulation preview with laser-stream pulse paths
  * Constellation particle canvas with proximity connection physics
- Animated cards across all sections (Problem, Solution, Workflow, Macro, API)
- High-end 4-column enterprise footer terminating cleanly at viewport end
"""

from components.public_ui import (
    get_public_css,
    get_public_navbar,
    get_public_footer,
    get_public_scripts,
)
from core.assets import (
    get_logo_dark_icon_b64,
    get_logo_dark_full_b64,
    get_logo_light_icon_b64,
    get_logo_light_full_b64,
)


def get_landing_html() -> str:
    """
    Returns the complete standalone HTML document for the landing experience.
    """
    logo_dark_icon = get_logo_dark_icon_b64()
    logo_light_icon = get_logo_light_icon_b64()
    logo_dark_full = get_logo_dark_full_b64()
    logo_light_full = get_logo_light_full_b64()

    return f"""
{get_public_css()}

<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Geist+Mono:wght@100..900&display=swap');

  :root, [data-theme="dark"] {{
    --bg-base: #101722;
    --surface-card: #16202E;
    --surface-card-hover: #1E2B3E;
    --accent-gold: #B49A5A;
    --accent-gold-hover: #C5AC6C;
    --text-primary: #F4F1E8;
    --text-muted: rgba(244, 241, 232, 0.75);
    --text-dim: rgba(244, 241, 232, 0.52);
    --border-color: rgba(244, 241, 232, 0.12);
    --border-gold: rgba(180, 154, 90, 0.35);
    --color-growth: #7A9B76;
    --color-base: #B49A5A;
    --color-recession: #B5545A;
  }}

  [data-theme="light"] {{
    --bg-base: #F4F1E8;
    --surface-card: #FFFFFF;
    --surface-card-hover: #FAF7F0;
    --accent-gold: #B49A5A;
    --accent-gold-hover: #9E8548;
    --text-primary: #101722;
    --text-muted: rgba(16, 23, 34, 0.75);
    --text-dim: rgba(16, 23, 34, 0.55);
    --border-color: rgba(16, 23, 34, 0.12);
    --border-gold: rgba(180, 154, 90, 0.45);
    --color-growth: #4E7B4A;
    --color-base: #B49A5A;
    --color-recession: #A83E44;
  }}

  /* Explicit Logo Switching Rules for Landing Page */
  .logo-light {{ display: none !important; }}
  .logo-dark {{ display: inline-block !important; }}
  [data-theme="dark"] .logo-light {{ display: none !important; }}
  [data-theme="dark"] .logo-dark {{ display: inline-block !important; }}
  [data-theme="light"] .logo-dark {{ display: none !important; }}
  [data-theme="light"] .logo-light {{ display: inline-block !important; }}

  /* Ensure top-navbar and footer are never suppressed */
  .top-navbar, nav.top-navbar {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
  }}
  .site-footer, footer.site-footer {{
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
  }}

  [data-theme="light"] #hero {{
    background: radial-gradient(circle at 50% 12%, rgba(255, 255, 255, 0.95) 0%, #F4F1E8 70%) !important;
  }}
  [data-theme="light"] .hero-title {{
    color: #101722 !important;
  }}
  [data-theme="light"] .hero-chip {{
    background: rgba(255, 255, 255, 0.88) !important;
    border: 1px solid rgba(180, 154, 90, 0.45) !important;
    color: #101722 !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08) !important;
  }}
  [data-theme="light"] .hero-sim-chamber,
  [data-theme="light"] .excel-card,
  [data-theme="light"] .solution-canvas-wrapper,
  [data-theme="light"] .step-card,
  [data-theme="light"] .macro-item,
  [data-theme="light"] .cta-banner {{
    background: #FFFFFF !important;
    border-color: rgba(16, 23, 34, 0.12) !important;
  }}
  [data-theme="light"] .chamber-header,
  [data-theme="light"] .excel-header {{
    border-color: rgba(16, 23, 34, 0.1) !important;
    color: #101722 !important;
  }}

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  html {{
    scroll-behavior: smooth;
  }}

  .arctus-landing-wrapper {{
    background-color: var(--bg-base);
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
    width: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    position: relative;
  }}

  /* Offset for fixed 72px navbar */
  section[id] {{
    scroll-margin-top: 76px;
  }}

  /* -------------------------------------------------------------
     CARD ANIMATION SUITE
  ------------------------------------------------------------- */
  .animated-card {{
    position: relative;
    overflow: hidden;
    transition: transform 280ms cubic-bezier(0.16, 1, 0.3, 1),
                box-shadow 280ms cubic-bezier(0.16, 1, 0.3, 1),
                border-color 280ms ease;
  }}

  .animated-card:hover {{
    transform: translateY(-7px) scale(1.012);
    border-color: var(--border-gold) !important;
    box-shadow: 0 16px 45px rgba(180, 154, 90, 0.2), 0 0 1px var(--border-gold) !important;
  }}

  .animated-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    transition: left 650ms ease;
  }}

  .animated-card:hover::before {{
    left: 100%;
  }}

  /* Live Pulse Indicators */
  @keyframes liveRadar {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(122, 155, 118, 0.7); }}
    70% {{ transform: scale(1.15); box-shadow: 0 0 0 9px rgba(122, 155, 118, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(122, 155, 118, 0); }}
  }}

  .live-pulse-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-growth);
    display: inline-block;
    animation: liveRadar 2s infinite;
  }}

  @keyframes goldRadar {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(252, 163, 17, 0.7); }}
    70% {{ transform: scale(1.15); box-shadow: 0 0 0 9px rgba(252, 163, 17, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(252, 163, 17, 0); }}
  }}

  .live-gold-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-gold);
    display: inline-block;
    animation: goldRadar 2s infinite;
  }}

  /* -------------------------------------------------------------
     HERO SECTION & UNIQUE ANIMATIONS
  ------------------------------------------------------------- */
  #hero {{
    min-height: auto;
    position: relative;
    padding-top: 104px;
    padding-bottom: 72px;
    background: radial-gradient(circle at 50% 12%, rgba(22, 32, 46, 0.88) 0%, var(--bg-base) 70%);
    overflow: hidden;
  }}

  .hero-canvas {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    pointer-events: none;
  }}

  .hero-content-wrapper {{
    position: relative;
    z-index: 2;
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 24px;
    text-align: center;
  }}

  /* Logo Halo & Energy Aura */
  .hero-logo-box {{
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
  }}

  .hero-logo-halo {{
    position: absolute;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(252, 163, 17, 0.45) 0%, rgba(20, 33, 61, 0.25) 50%, transparent 72%);
    animation: haloPulse 3.8s ease-in-out infinite alternate;
    pointer-events: none;
    filter: blur(10px);
  }}

  .hero-logo-img {{
    position: relative;
    height: 72px;
    width: auto;
    filter: drop-shadow(0 0 24px rgba(252, 163, 17, 0.55));
    animation: emblemFloat 4.2s ease-in-out infinite alternate;
  }}

  @keyframes haloPulse {{
    0% {{ transform: scale(0.85); opacity: 0.45; }}
    100% {{ transform: scale(1.32); opacity: 0.95; }}
  }}

  @keyframes emblemFloat {{
    0% {{ transform: translateY(0px) rotate(0deg); }}
    100% {{ transform: translateY(-7px) rotate(0.8deg); }}
  }}

  .brand-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 18px;
    background: rgba(252, 163, 17, 0.08);
    border: 1px solid var(--border-gold);
    border-radius: 100px;
    font-size: 0.8rem;
    color: var(--accent-gold);
    margin-bottom: 22px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
  }}

  /* Animated Liquid Molten Gold Headline */
  .hero-title {{
    font-family: 'DM Sans', sans-serif;
    font-size: clamp(2.8rem, 5.8vw, 5rem);
    font-weight: 800;
    line-height: 1.06;
    letter-spacing: -0.035em;
    margin-bottom: 20px;
    color: #FFFFFF;
  }}

  .hero-fluid-gold {{
    background: linear-gradient(
      90deg,
      #FCA311 0%,
      #FFE599 25%,
      #FFFFFF 48%,
      #FFE599 72%,
      #FCA311 100%
    );
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: moltenGoldFlow 5s linear infinite;
    text-shadow: 0 0 45px rgba(252, 163, 17, 0.35);
    display: inline-block;
  }}

  @keyframes moltenGoldFlow {{
    0% {{ background-position: 0% center; }}
    100% {{ background-position: 200% center; }}
  }}

  .muted-text {{
    color: var(--text-muted);
    font-size: 1.15rem;
    line-height: 1.68;
    max-width: 720px;
    margin: 0 auto;
  }}

  /* Floating Holographic Telemetry Badges */
  .hero-chips-container {{
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 24px;
    margin-bottom: 28px;
  }}

  .hero-chip {{
    display: inline-flex;
    align-items: center;
    gap: 9px;
    padding: 8px 16px;
    background: rgba(20, 33, 61, 0.72);
    border: 1px solid rgba(252, 163, 17, 0.32);
    border-radius: 50px;
    font-size: 0.84rem;
    color: #FFFFFF;
    backdrop-filter: blur(14px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
    transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
  }}

  .hero-chip:hover {{
    transform: translateY(-4px);
    border-color: var(--accent-gold);
    box-shadow: 0 10px 30px rgba(252, 163, 17, 0.22);
  }}

  .hero-chip strong {{
    color: var(--accent-gold);
  }}

  @keyframes chipFloat1 {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-6px); }}
  }}
  @keyframes chipFloat2 {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-8px); }}
  }}
  @keyframes chipFloat3 {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-5px); }}
  }}

  .chip-anim-1 {{ animation: chipFloat1 5.2s ease-in-out infinite; }}
  .chip-anim-2 {{ animation: chipFloat2 6.4s ease-in-out infinite 0.6s; }}
  .chip-anim-3 {{ animation: chipFloat3 5.8s ease-in-out infinite 1.2s; }}

  /* CTA Buttons */
  .hero-cta-group {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    margin-top: 10px;
    margin-bottom: 42px;
    flex-wrap: wrap;
  }}

  .cta-primary {{
    background: var(--accent-gold);
    color: #000000;
    border: 1px solid var(--accent-gold);
    padding: 14px 34px;
    border-radius: 8px;
    font-size: 1.02rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 200ms ease;
    box-shadow: 0 6px 26px rgba(252, 163, 17, 0.3);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }}

  .cta-primary::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
    transition: left 600ms ease;
  }}

  .cta-primary:hover {{
    background: #FFFFFF;
    border-color: #FFFFFF;
    color: #000000;
    transform: translateY(-2px);
    box-shadow: 0 10px 36px rgba(252, 163, 17, 0.45);
  }}

  .cta-primary:hover::before {{
    left: 100%;
  }}

  .cta-secondary {{
    background: rgba(20, 33, 61, 0.45);
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
    backdrop-filter: blur(10px);
  }}

  .cta-secondary:hover {{
    border-color: var(--accent-gold);
    color: var(--accent-gold);
    background: var(--surface-card);
    transform: translateY(-2px);
  }}

  /* -------------------------------------------------------------
     INTERACTIVE LIVE MONTE CARLO WAVE CHAMBER (HERO FEATURE)
  ------------------------------------------------------------- */
  .hero-sim-chamber {{
    max-width: 960px;
    margin: 0 auto;
    background: var(--surface-card);
    border: 1px solid var(--border-gold);
    border-radius: 14px;
    padding: 22px 28px;
    box-shadow: 0 16px 50px rgba(0, 0, 0, 0.4), 0 0 1px var(--border-gold);
    position: relative;
    overflow: hidden;
  }}

  .chamber-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 12px;
    margin-bottom: 16px;
    font-size: 0.78rem;
    color: var(--text-dim);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    flex-wrap: wrap;
    gap: 8px;
  }}

  .chamber-status {{
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--color-growth);
    font-weight: 600;
  }}

  .chamber-badges {{
    display: flex;
    gap: 16px;
    font-size: 0.76rem;
    color: rgba(255, 255, 255, 0.5);
  }}

  .chamber-badges span {{
    color: var(--accent-gold);
    font-weight: 600;
  }}

  .sim-svg-wrapper {{
    position: relative;
    width: 100%;
    height: 150px;
  }}

  @keyframes dashStream {{
    0% {{ stroke-dashoffset: 80; }}
    100% {{ stroke-dashoffset: 0; }}
  }}

  .stream-growth {{
    stroke: var(--color-growth);
    stroke-width: 2.5;
    fill: none;
    stroke-dasharray: 10 5;
    animation: dashStream 2.6s linear infinite;
  }}

  .stream-base {{
    stroke: var(--accent-gold);
    stroke-width: 3;
    fill: none;
    stroke-dasharray: 12 6;
    animation: dashStream 2.2s linear infinite;
  }}

  .stream-recession {{
    stroke: var(--color-recession);
    stroke-width: 2.5;
    fill: none;
    stroke-dasharray: 10 5;
    animation: dashStream 3s linear infinite;
  }}

  .sim-legend-strip {{
    display: flex;
    justify-content: space-around;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 12px;
    margin-top: 8px;
    font-size: 0.8rem;
    flex-wrap: wrap;
    gap: 12px;
  }}

  .sim-legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  /* -------------------------------------------------------------
     SECTIONS & LAYOUT (FULL-BLEED)
  ------------------------------------------------------------- */
  .section {{
    width: 100%;
    position: relative;
    padding: 85px 32px;
    border-bottom: 1px solid var(--border-color);
  }}

  .container {{
    max-width: 1180px;
    width: 100%;
    margin: 0 auto;
    position: relative;
    z-index: 2;
  }}

  h1, h2, h3, h4 {{
    font-family: 'DM Sans', sans-serif;
    letter-spacing: -0.03em;
    font-weight: 700;
    color: var(--text-primary);
  }}

  .gold-text {{
    color: var(--accent-gold);
    text-shadow: 0 0 35px rgba(252, 163, 17, 0.25);
  }}

  /* Problem Grid */
  .problem-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
    align-items: center;
    margin-top: 40px;
  }}

  @media (max-width: 860px) {{
    .problem-grid {{ grid-template-columns: 1fr; }}
  }}

  .excel-card {{
    background: #0B111E;
    border: 1px solid rgba(181, 84, 90, 0.35);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.7);
  }}

  .excel-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
    margin-bottom: 16px;
    font-size: 0.8rem;
    color: #B5545A;
  }}

  .excel-row {{
    display: flex;
    justify-content: space-between;
    padding: 9px 12px;
    font-size: 0.85rem;
    font-family: monospace;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  }}

  .excel-error {{
    color: #B5545A;
    background: rgba(181, 84, 90, 0.15);
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
  }}

  /* Solution Curves */
  .solution-canvas-wrapper {{
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 32px;
    margin-top: 36px;
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.7);
  }}

  .scenario-legend {{
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }}

  .legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 500;
  }}

  .legend-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }}

  /* Workflow Steps */
  .steps-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin-top: 40px;
  }}

  @media (max-width: 960px) {{
    .steps-row {{ grid-template-columns: 1fr 1fr; }}
  }}
  @media (max-width: 540px) {{
    .steps-row {{ grid-template-columns: 1fr; }}
  }}

  .step-card {{
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 28px 22px;
  }}

  .step-num {{
    font-family: 'DM Sans', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 10px;
    transition: transform 250ms ease;
  }}

  .step-card:hover .step-num {{
    transform: scale(1.1) translateX(4px);
  }}

  .step-title {{
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 10px;
  }}

  /* Macro Grid */
  .macro-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-top: 36px;
  }}

  @media (max-width: 900px) {{
    .macro-grid {{ grid-template-columns: 1fr 1fr; }}
  }}
  @media (max-width: 500px) {{
    .macro-grid {{ grid-template-columns: 1fr; }}
  }}

  .macro-item {{
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 26px 22px;
    text-align: center;
  }}

  .macro-label {{
    font-size: 0.8rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }}

  .macro-num {{
    font-family: 'DM Sans', sans-serif;
    font-size: 2.7rem;
    font-weight: 700;
    color: var(--accent-gold);
    letter-spacing: -0.02em;
  }}

  .macro-src {{
    font-size: 0.75rem;
    color: rgba(229, 229, 229, 0.45);
    margin-top: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }}

  /* REST API Preview */
  .api-preview-card {{
    background: #080D1A;
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 28px;
    margin-top: 36px;
    font-family: monospace;
    font-size: 0.88rem;
    color: #E5E5E5;
    overflow-x: auto;
  }}

  .terminal-bar {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }}

  .dot-red {{ width: 10px; height: 10px; border-radius: 50%; background: #FF5F56; }}
  .dot-yellow {{ width: 10px; height: 10px; border-radius: 50%; background: #FFBD2E; }}
  .dot-green {{ width: 10px; height: 10px; border-radius: 50%; background: #27C93F; }}

  /* Pre-Footer CTA Banner */
  .cta-banner {{
    background: radial-gradient(circle at 50% 0%, var(--surface-card) 0%, var(--bg-base) 80%);
    border: 1px solid var(--border-gold);
    border-radius: 16px;
    padding: 56px 32px;
    text-align: center;
    margin: 60px 0 0 0;
  }}

  /* Scroll Reveal Utilities */
  .reveal {{
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 350ms cubic-bezier(0.16, 1, 0.3, 1), transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
  }}

  .reveal.active {{
    opacity: 1;
    transform: translateY(0);
  }}
</style>

<div class="arctus-landing-wrapper">

  <!-- TOP NAVBAR -->
  {get_public_navbar(active_page="landing")}

  <!-- SECTION 1: HERO WITH UNIQUE ANIMATIONS -->
  <section class="section" id="hero">
    <canvas id="particleCanvas" class="hero-canvas"></canvas>
    <div class="hero-content-wrapper">
      
      <!-- Pulsating Official Logo with Floating Halo -->
      <div class="reveal">
        <div class="hero-logo-box">
          <div class="hero-logo-halo"></div>
          <img src="{logo_dark_icon}" alt="Arctus Emblem" class="hero-logo-img logo-dark" />
          <img src="{logo_light_icon}" alt="Arctus Emblem" class="hero-logo-img logo-light" />
        </div>
        <br>
        <span class="brand-badge">Institutional FP&A • Indian Mid-Market</span>
      </div>

      <!-- Animated Liquid Molten Gold Headline -->
      <h1 class="hero-title reveal" style="transition-delay: 80ms;">
        Financial certainty,<br>
        <span class="hero-fluid-gold">simulated in seconds.</span>
      </h1>

      <p class="muted-text reveal" style="transition-delay: 160ms;">
        Replace 2–3 days of manual Excel-based scenario planning with a 30-second automated,
        statistically rigorous Monte Carlo forecasting platform grounded in live RBI Repo Rate and CPI macroeconomic data.
      </p>

      <!-- Floating Holographic Telemetry Badges -->
      <div class="hero-chips-container reveal" style="transition-delay: 220ms;">
        <div class="hero-chip chip-anim-1">
          <span class="live-pulse-dot"></span>
          <span><strong>1,000 Monte Carlo Paths</strong> • 0.04s Vectorized</span>
        </div>
        <div class="hero-chip chip-anim-2">
          <span class="live-gold-dot"></span>
          <span><strong>RBI Repo Rate: 6.50%</strong> • Live Macro Sync</span>
        </div>
        <div class="hero-chip chip-anim-3">
          <span class="live-pulse-dot"></span>
          <span><strong>₹500 Cr P&L Tested</strong> • 99.2% Confidence</span>
        </div>
      </div>

      <!-- Hero CTA Buttons -->
      <div class="hero-cta-group reveal" style="transition-delay: 280ms;">
        <a href="?page=dashboard" class="cta-primary" data-page="dashboard">
          ⚡ Launch Live Platform →
        </a>
        <a href="?page=login" class="cta-secondary" data-page="login">
          CFO Demo Login
        </a>
      </div>

      <!-- Interactive Real-Time Monte Carlo Simulation Wave Chamber -->
      <div class="hero-sim-chamber animated-card reveal" style="transition-delay: 340ms;">
        <div class="chamber-header">
          <div class="chamber-status">
            <span class="live-pulse-dot"></span>
            SIMULATION ENGINE: ACTIVE
          </div>
          <div class="chamber-badges">
            <div>VECTORS: <span>1,000 RUNS</span></div>
            <div>LATENCY: <span>28ms</span></div>
            <div>HORIZON: <span>4 QUARTERS</span></div>
            <div>STATUS: <span>GROUNDED</span></div>
          </div>
        </div>

        <!-- Animated Laser Pulse Stream Curves -->
        <div class="sim-svg-wrapper">
          <svg viewBox="0 0 900 150" width="100%" height="100%" preserveAspectRatio="none">
            <!-- Grid Lines -->
            <line x1="0" y1="30" x2="900" y2="30" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
            <line x1="0" y1="75" x2="900" y2="75" stroke="rgba(255,255,255,0.07)" stroke-width="1" stroke-dasharray="4 4" />
            <line x1="0" y1="120" x2="900" y2="120" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
            
            <!-- Shaded Confidence Band -->
            <path d="M 50,75 C 220,55 420,30 650,22 C 780,18 850,20 880,22 L 880,132 C 850,130 780,128 650,122 C 420,110 220,95 50,75 Z"
                  fill="rgba(252, 163, 17, 0.06)" />

            <!-- Trajectory 1: Bull Growth Path (Green) -->
            <path class="stream-growth"
                  d="M 50,75 C 200,60 400,38 600,28 S 800,20 880,18" />

            <!-- Trajectory 2: Base Case (Gold) -->
            <path class="stream-base"
                  d="M 50,75 C 200,72 400,66 600,58 S 800,48 880,44" />

            <!-- Trajectory 3: Severe Stress Recession (Coral) -->
            <path class="stream-recession"
                  d="M 50,75 C 200,85 400,105 600,120 S 800,135 880,138" />

            <!-- Glowing Terminal Milestone Nodes -->
            <circle cx="880" cy="18" r="5" fill="#7A9B76" filter="drop-shadow(0 0 8px #7A9B76)" />
            <circle cx="880" cy="44" r="5" fill="#FCA311" filter="drop-shadow(0 0 8px #FCA311)" />
            <circle cx="880" cy="138" r="5" fill="#B5545A" filter="drop-shadow(0 0 8px #B5545A)" />
          </svg>
        </div>

        <div class="sim-legend-strip">
          <div class="sim-legend-item">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--color-growth);"></span>
            <span>Bull Expansion (+18.4% EBITDA)</span>
          </div>
          <div class="sim-legend-item">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--accent-gold);"></span>
            <span>Base Baseline (+6.2% EBITDA)</span>
          </div>
          <div class="sim-legend-item">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: var(--color-recession);"></span>
            <span>Severe Recession (-14.1% EBITDA)</span>
          </div>
        </div>
      </div>

    </div>
  </section>

  <!-- SECTION 2: THE PROBLEM -->
  <section class="section" id="problem">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">The Excel Bottleneck</span>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.2rem); margin-bottom: 16px;">
          Fragile Spreadsheets Cost Indian CFOs Days.
        </h2>
        <p class="muted-text">
          Mid-market finance teams spend 70% of scenario planning time wrestling with broken VLOOKUPs, unmerged cells, and static assumptions instead of analyzing risks.
        </p>
      </div>

      <div class="problem-grid">
        <!-- Broken Excel Mockup -->
        <div class="excel-card animated-card reveal" style="transition-delay: 100ms;">
          <div class="excel-header">
            <span>ANNUAL_BUDGET_V14_FINAL_FINAL.XLSX</span>
            <span style="color: #B5545A;">● 3 ERRORS DETECTED</span>
          </div>
          <div class="excel-row">
            <span style="color: #A0AEC0;">COGS / Raw Materials</span>
            <span class="excel-error">#REF!</span>
          </div>
          <div class="excel-row">
            <span style="color: #A0AEC0;">EBITDA (Q3 FY25)</span>
            <span class="excel-error">#VALUE!</span>
          </div>
          <div class="excel-row">
            <span style="color: #A0AEC0;">Repo Rate Sensitivity</span>
            <span style="color: #E2E8F0;">Static 6.50%</span>
          </div>
          <div class="excel-row">
            <span style="color: #A0AEC0;">Simulation Iterations</span>
            <span style="color: #B5545A;">1 (Manual)</span>
          </div>
          <div class="excel-row" style="border-bottom: none;">
            <span style="color: #A0AEC0;">Turnaround Time</span>
            <span style="color: #B5545A; font-weight: 700;">48 Hours</span>
          </div>
        </div>

        <!-- The Arctus Contrast -->
        <div class="reveal" style="transition-delay: 200ms;">
          <h3 style="font-size: 1.8rem; margin-bottom: 20px; color: var(--accent-gold);">
            Why Manual Models Break Under Pressure
          </h3>
          <ul style="list-style: none; display: flex; flex-direction: column; gap: 18px; color: var(--text-muted); font-size: 1.02rem;">
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #B5545A; font-size: 1.2rem; line-height: 1;">✕</span>
              <span><strong>Static Single-Point Estimates:</strong> Excel scenarios test 2–3 arbitrary cases, completely missing multi-variable tail risks.</span>
            </li>
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #B5545A; font-size: 1.2rem; line-height: 1;">✕</span>
              <span><strong>Isolated from Macro Data:</strong> Assumptions are entered manually without live links to RBI Repo decisions or MoSPI inflation benchmarks.</span>
            </li>
            <li style="display: flex; gap: 12px; align-items: flex-start;">
              <span style="color: #7A9B76; font-size: 1.2rem; line-height: 1;">✓</span>
              <span><strong>The Arctus Advantage:</strong> 1,000 vectorized Monte Carlo paths computed in 0.04s, outputting CFO-grade EBITDA probability distributions.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- SECTION 3: THE SOLUTION -->
  <section class="section" id="solution">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">Vectorized Intelligence</span>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.2rem); margin-bottom: 16px;">
          Institutional-Grade Stress-Testing
        </h2>
        <p class="muted-text">
          Run 1,000 statistical simulations across 4 forward quarters with correlated economic shocks.
        </p>
      </div>

      <div class="solution-canvas-wrapper animated-card reveal" style="transition-delay: 150ms;">
        <div class="scenario-legend">
          <div class="legend-item">
            <div class="legend-dot" style="background: var(--color-growth);"></div>
            <span>Growth Case (+15% Rev, -50bps Repo)</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: var(--color-base);"></div>
            <span>Base Plan (+8% Rev, 0bps Repo)</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: var(--color-recession);"></div>
            <span>Stagflation (+100bps Repo, +12% COGS)</span>
          </div>
        </div>

        <svg id="scenarioSvg" viewBox="0 0 900 280" width="100%" height="280">
          <defs>
            <linearGradient id="growthGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#7A9B76" stop-opacity="0.25"/>
              <stop offset="100%" stop-color="#7A9B76" stop-opacity="0.0"/>
            </linearGradient>
            <linearGradient id="recessionGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#B5545A" stop-opacity="0.0"/>
              <stop offset="100%" stop-color="#B5545A" stop-opacity="0.25"/>
            </linearGradient>
          </defs>

          <!-- Axes -->
          <line x1="60" y1="240" x2="860" y2="240" stroke="rgba(229,229,229,0.15)" stroke-width="1"/>
          <line x1="60" y1="20" x2="60" y2="240" stroke="rgba(229,229,229,0.15)" stroke-width="1"/>

          <!-- Quarter Markers -->
          <text x="60" y="262" fill="rgba(255,255,255,0.4)" font-size="12" font-family="sans-serif">Q4 FY24 (Base)</text>
          <text x="260" y="262" fill="rgba(255,255,255,0.4)" font-size="12" font-family="sans-serif">Q1 FY25</text>
          <text x="460" y="262" fill="rgba(255,255,255,0.4)" font-size="12" font-family="sans-serif">Q2 FY25</text>
          <text x="660" y="262" fill="rgba(255,255,255,0.4)" font-size="12" font-family="sans-serif">Q3 FY25</text>
          <text x="840" y="262" fill="rgba(255,255,255,0.4)" font-size="12" font-family="sans-serif">Q4 FY25</text>

          <!-- Shaded Area Between Paths -->
          <path d="M 60,150 C 260,110 460,70 860,40 L 860,225 C 460,195 260,165 60,150 Z"
                fill="url(#growthGrad)" />

          <!-- Growth Curve -->
          <path id="growthPath"
                d="M 60,150 C 260,110 460,70 860,40"
                fill="none" stroke="#7A9B76" stroke-width="3"
                stroke-dasharray="1000" stroke-dashoffset="1000"/>

          <!-- Base Curve -->
          <path id="basePath"
                d="M 60,150 C 260,135 460,120 860,105"
                fill="none" stroke="#FCA311" stroke-width="3"
                stroke-dasharray="1000" stroke-dashoffset="1000"/>

          <!-- Recession Curve -->
          <path id="recessionPath"
                d="M 60,150 C 260,165 460,195 860,225"
                fill="none" stroke="#B5545A" stroke-width="3"
                stroke-dasharray="1000" stroke-dashoffset="1000"/>

          <!-- Milestone Dots -->
          <circle cx="60" cy="150" r="5" fill="#FFFFFF"/>
          <circle cx="860" cy="40" r="6" fill="#7A9B76"/>
          <circle cx="860" cy="105" r="6" fill="#FCA311"/>
          <circle cx="860" cy="225" r="6" fill="#B5545A"/>
        </svg>
      </div>
    </div>
  </section>

  <!-- SECTION 4: HOW IT WORKS -->
  <section class="section" id="workflow">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">Automated Pipeline</span>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.2rem); margin-bottom: 16px;">How Arctus Operates</h2>
        <p class="muted-text">From messy spreadsheet to board-ready stress-test forecast in 4 automated stages.</p>
      </div>

      <div class="steps-row">
        <div class="step-card animated-card reveal" style="transition-delay: 100ms;">
          <div class="step-num">01</div>
          <div class="step-title">Ingest P&L</div>
          <p style="color: var(--text-dim); font-size: 0.92rem; line-height: 1.6;">
            Upload messy multi-sheet Excel, transposed CSVs, or unmerged cell formats. The RawNormalizer automatically cleans headers and aligns periods.
          </p>
        </div>

        <div class="step-card animated-card reveal" style="transition-delay: 200ms;">
          <div class="step-num">02</div>
          <div class="step-title">Auto-Reconcile</div>
          <p style="color: var(--text-dim); font-size: 0.92rem; line-height: 1.6;">
            RapidFuzz matching maps Indian accounting line items with >=78% confidence, with instant manual overrides and accounting validation rules.
          </p>
        </div>

        <div class="step-card animated-card reveal" style="transition-delay: 300ms;">
          <div class="step-num">03</div>
          <div class="step-title">Simulate</div>
          <p style="color: var(--text-dim); font-size: 0.92rem; line-height: 1.6;">
            Execute 1,000 vectorized Monte Carlo paths across 4 quarters with live RBI interest rate and inflation distributions.
          </p>
        </div>

        <div class="step-card animated-card reveal" style="transition-delay: 400ms;">
          <div class="step-num">04</div>
          <div class="step-title">Prescribe</div>
          <p style="color: var(--text-dim); font-size: 0.92rem; line-height: 1.6;">
            Receive CFO-grade Plotly visualizers: EBITDA Waterfall bridges, percentile fan charts, tornado sensitivity, and audit-ready CSV exports.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- SECTION 5: LIVE MACRO TELEMETRY -->
  <section class="section" id="macro">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">Real-Time Telemetry</span>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.2rem); margin-bottom: 16px;">Live Indian Macro Telemetry</h2>
        <p class="muted-text">
          Arctus anchors your stress tests in verified, live macroeconomic indicators from official Indian sources.
        </p>
      </div>

      <div class="macro-grid">
        <div class="macro-item animated-card reveal" style="transition-delay: 100ms;">
          <div class="macro-label">RBI Policy Repo Rate</div>
          <div class="macro-num">6.50%</div>
          <div class="macro-src">
            <span class="live-pulse-dot"></span>
            Reserve Bank of India • MPC
          </div>
        </div>

        <div class="macro-item animated-card reveal" style="transition-delay: 200ms;">
          <div class="macro-label">Headline CPI Inflation</div>
          <div class="macro-num">4.85%</div>
          <div class="macro-src">
            <span class="live-pulse-dot"></span>
            MoSPI • Monthly Release
          </div>
        </div>

        <div class="macro-item animated-card reveal" style="transition-delay: 300ms;">
          <div class="macro-label">Brent Crude Benchmark</div>
          <div class="macro-num">$74.50</div>
          <div class="macro-src">
            <span class="live-pulse-dot"></span>
            ICE Futures • Spot Barrel
          </div>
        </div>

        <div class="macro-item animated-card reveal" style="transition-delay: 400ms;">
          <div class="macro-label">10-Year G-Sec Yield</div>
          <div class="macro-num">7.02%</div>
          <div class="macro-src">
            <span class="live-pulse-dot"></span>
            CCIL Sovereign Yield Curve
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- SECTION 6: REST API PREVIEW -->
  <section class="section" id="api">
    <div class="container">
      <div class="reveal">
        <span class="brand-badge">Programmatic REST API</span>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.2rem); margin-bottom: 16px;">Call the Forecasting Engine via API</h2>
        <p class="muted-text">
          Integrate the Arctus Monte Carlo engine directly into ERPs (SAP, Tally Prime, Zoho Books) or your proprietary data stack.
        </p>
      </div>

      <div class="api-preview-card animated-card reveal">
        <div class="terminal-bar">
          <span class="dot-red"></span>
          <span class="dot-yellow"></span>
          <span class="dot-green"></span>
          <span style="font-size: 0.8rem; color: rgba(255,255,255,0.4); margin-left: 8px;">bash — curl — 80x24</span>
        </div>
        <div style="color: #FCA311; margin-bottom: 8px;">POST /api/forecast HTTP/1.1</div>
        <div style="color: rgba(255,255,255,0.4); margin-bottom: 14px;">Host: localhost:5000 &nbsp;|&nbsp; Content-Type: application/json</div>
        <pre style="color: #A0C0E0;">curl -X POST "http://localhost:5000/api/forecast" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "statement": {{ "periods": ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"], "revenue": [125000000, 132000000, 140000000, 155000000] }},
    "scenarios": [{{ "name": "Recession", "rev_growth": -0.06, "cogs_inflation": 0.08, "macro_shock": 1.25 }}],
    "iterations": 1000
  }}'</pre>
      </div>

      <!-- PRE-FOOTER CTA BANNER -->
      <div class="cta-banner animated-card reveal">
        <img src="{logo_dark_icon}" alt="Arctus" class="logo-dark" style="height: 54px; margin-bottom: 16px;" />
        <img src="{logo_light_icon}" alt="Arctus" class="logo-light" style="height: 54px; margin-bottom: 16px;" />
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.2rem); margin-bottom: 16px;">
          Ready to Stress-Test Your Financial Strategy?
        </h2>
        <p style="color: var(--text-muted); max-width: 620px; margin: 0 auto 32px auto; font-size: 1.05rem;">
          Simulate 1,000 Monte Carlo scenarios grounded in live RBI and CPI macroeconomic data in under 30 seconds.
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
          <a href="?page=dashboard" class="cta-primary" data-page="dashboard">
            ⚡ Launch Live Demo Platform →
          </a>
          <a href="?page=register" class="cta-secondary" data-page="register">
            Create Enterprise Account
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- ENTERPRISE FOOTER -->
  {get_public_footer()}

</div>

{get_public_scripts()}

<script>
  // SVG Scenario Curve Draw-in
  function triggerCurveAnimation() {{
    ['growthPath', 'basePath', 'recessionPath'].forEach((id, idx) => {{
      const path = document.getElementById(id);
      if (path) {{
        path.style.transition = `stroke-dashoffset 900ms ease ${{idx * 120}}ms`;
        path.style.strokeDashoffset = '0';
      }}
    }});
  }}

  // Constellation Particle Canvas Animation
  (function initConstellationCanvas() {{
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.offsetWidth || window.innerWidth;
    let height = canvas.height = canvas.parentElement.offsetHeight || 600;

    window.addEventListener('resize', () => {{
      width = canvas.width = canvas.parentElement.offsetWidth || window.innerWidth;
      height = canvas.height = canvas.parentElement.offsetHeight || 600;
    }});

    const particles = [];
    const numParticles = 48;
    for (let i = 0; i < numParticles; i++) {{
      particles.push({{
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.6 + 0.6,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.45 + 0.15
      }});
    }}

    function renderParticles() {{
      ctx.clearRect(0, 0, width, height);

      // Draw connecting constellation lines
      for (let i = 0; i < particles.length; i++) {{
        for (let j = i + 1; j < particles.length; j++) {{
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 95) {{
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = 'rgba(180, 154, 90, ' + (0.22 * (1 - dist / 95)) + ')';
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }}
        }}
      }}

      // Draw particle nodes
      particles.forEach(p => {{
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(180, 154, 90, ${{p.alpha}})`;
        ctx.fill();
      }});
      requestAnimationFrame(renderParticles);
    }}
    renderParticles();
  }})();
</script>
"""
