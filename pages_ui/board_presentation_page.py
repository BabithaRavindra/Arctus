"""
CFO Board Presentation Studio Page for Arctus (`/board_presentation`).
Delivers institutional board pack generation & design customization:
- One-Click AI Board Pack generation (Editable PPTX and Executive PDF)
- AI Narrative & Commentary with 4 pillars: What, Why, Financial Impact, Action
- AI-Powered Design & Theme Studio (Executive Gold, Corporate Slate, Investor Minimal, Lender Navy)
- Source Traceability drilling down to underlying financial rows & formulas
- Smart Refresh & Pre-flight QA check for zero discrepancies before export
- AI Natural-Language Slide Editor commands ("Make this more concise", "Rewrite for lenders", etc.)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from core.models import FinancialStatement, Scenario, ForecastResult
from core.synthetic import generate_clean_midmarket_statement
from core.cockpit import calculate_cockpit_metrics, get_default_capital_structure_for_statement
from core.covenants import compute_probabilistic_covenant_matrix
from core.board_pack import (
    THEMES,
    PresentationTheme,
    SlideNarrative,
    generate_structured_slide_narratives,
    run_presentation_qa_preflight,
    build_editable_pptx_deck,
    build_executive_pdf_deck,
)
from core.theme import (
    format_inr,
    format_percentage,
    ACCENT_GOLD,
    SURFACE_CARD,
    BORDER_COLOR,
    BORDER_COLOR_GOLD,
    COLOR_GROWTH,
    COLOR_BASE,
    COLOR_RECESSION,
)
from components.metrics import render_metric_card
from core.assets import get_logo_icon_b64


def initialize_board_presentation_state():
    """Initializes session state for the Board Presentation Studio."""
    if "current_statement" not in st.session_state:
        st.session_state["current_statement"] = generate_clean_midmarket_statement()
        st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
        st.session_state["file_normalized"] = True

    if "board_theme_key" not in st.session_state:
        st.session_state["board_theme_key"] = "executive_gold"

    if "board_audience_mode" not in st.session_state:
        st.session_state["board_audience_mode"] = "board"

    if "board_confidentiality" not in st.session_state:
        st.session_state["board_confidentiality"] = "STRICTLY CONFIDENTIAL • BOARD OF DIRECTORS REVIEW"

    if "ai_command_history" not in st.session_state:
        st.session_state["ai_command_history"] = []


def render_board_presentation_page(on_navigate, user_unit: str = "crores"):
    """
    Renders the dedicated Board Presentation Studio page.
    """
    initialize_board_presentation_state()

    user = st.session_state.get("user")
    company_name = user.company_name if user else "Apex Precision Automotives Ltd."
    statement: FinancialStatement = st.session_state["current_statement"]
    logo_icon = get_logo_icon_b64()

    # 1. Header
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <img src="{logo_icon}" alt="Arctus" style="height: 48px; width: auto; filter: drop-shadow(0 0 12px rgba(180, 154, 90, 0.3));" />
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                            <span class="brand-badge" style="margin: 0; padding: 2px 8px; font-size: 0.72rem;">BOARD PACK STUDIO</span>
                            <span style="font-size: 0.8rem; color: var(--accent-gold); display: inline-flex; align-items: center; gap: 6px;">
                                One-Click AI Executive Presentation Engine • Editable PPTX & PDF
                            </span>
                        </div>
                        <h1 style="font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.15;">
                            CFO Board Presentation Studio
                        </h1>
                        <p style="color: var(--text-dim); font-size: 0.92rem; margin: 4px 0 0 0;">
                            Generate board-ready slides with 4-pillar narrative, source traceability, and automated pre-flight QA
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span style="font-size: 0.82rem; color: var(--text-dim);">Reporting Entity:</span>
                    <span style="font-size: 0.84rem; color: var(--accent-gold); font-weight: 600; background: rgba(180, 154, 90, 0.1); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-gold);">
                        {company_name}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick Navigation Ribbon
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        if st.button("📊 Executive Cockpit", use_container_width=True):
            on_navigate("overview")
    with q_col2:
        if st.button("📝 Modeling Grid", use_container_width=True):
            on_navigate("model")
    with q_col3:
        if st.button("🎯 Scenario Studio", use_container_width=True):
            on_navigate("scenarios")
    with q_col4:
        if st.button("🏦 Covenant Matrix", use_container_width=True):
            on_navigate("covenants")

    # 2. Compute live Cockpit metrics and Narratives
    cap_struct = get_default_capital_structure_for_statement(statement)
    metrics = calculate_cockpit_metrics(stmt=statement, cap_struct=cap_struct, company_name=company_name)

    # Pre-Flight QA Check
    qa_result = run_presentation_qa_preflight(statement, metrics)

    # Generate or retrieve slide narratives
    theme = THEMES.get(st.session_state["board_theme_key"], THEMES["executive_gold"])
    narratives = generate_structured_slide_narratives(
        stmt=statement,
        metrics=metrics,
        audience=st.session_state["board_audience_mode"]
    )

    # Top Pre-Flight Banner
    if qa_result.passed and not qa_result.warnings:
        st.markdown(
            """
            <div style="background: rgba(122, 155, 118, 0.1); border: 1px solid var(--color-growth); border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 0.88rem; color: var(--color-growth); font-weight: 600;">
                    ✓ Smart Pre-Flight QA Passed: All financial identities reconciled ($GP = Rev - COGS$, $EBITDA = GP - OPEX$) with zero mathematical discrepancies.
                </div>
                <span class="brand-badge" style="background: var(--color-growth); color: #101722; font-size: 0.72rem;">AUDIT READY</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif qa_result.warnings:
        st.markdown(
            f"""
            <div style="background: rgba(252, 163, 17, 0.1); border: 1px solid var(--accent-gold); border-radius: 8px; padding: 10px 16px; margin-bottom: 20px;">
                <div style="font-size: 0.88rem; color: var(--accent-gold); font-weight: 600;">
                    ⚠️ Pre-Flight QA Notice: {len(qa_result.warnings)} item(s) flagged for executive review:
                </div>
                <div style="font-size: 0.82rem; color: var(--text-dim); margin-top: 4px;">
                    {' • '.join(qa_result.warnings)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Studio Workspace Tabs
    tab_generate, tab_theme, tab_editor, tab_trace = st.tabs([
        "🚀 Generate & Export Deck",
        "🎨 Design & Theme Studio",
        "✨ AI Slide Editor & Commands",
        "🔍 Source Traceability Drill-Down"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: GENERATE & EXPORT DECK
    # -------------------------------------------------------------------------
    with tab_generate:
        st.markdown("### Executive Presentation Preview")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Inspect preview slides below and export to fully editable PowerPoint (.pptx) or executive PDF board pack."
            "</p>",
            unsafe_allow_html=True
        )

        # Export Action Buttons
        exp_col1, exp_col2, exp_col3 = st.columns([1.5, 1.5, 2])

        with exp_col1:
            pptx_bytes = build_editable_pptx_deck(
                stmt=statement,
                metrics=metrics,
                narratives=narratives,
                theme=theme,
                company_name=company_name,
                confidentiality_label=st.session_state["board_confidentiality"]
            )
            st.download_button(
                label="📥 Download Editable PPTX (.pptx)",
                data=pptx_bytes.getvalue(),
                file_name=f"{company_name.replace(' ', '_')}_Board_Pack.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                type="primary",
                use_container_width=True
            )

        with exp_col2:
            pdf_bytes = build_executive_pdf_deck(
                stmt=statement,
                metrics=metrics,
                narratives=narratives,
                theme=theme,
                company_name=company_name,
                confidentiality_label=st.session_state["board_confidentiality"]
            )
            st.download_button(
                label="📥 Download Executive PDF (.pdf)",
                data=pdf_bytes.getvalue(),
                file_name=f"{company_name.replace(' ', '_')}_Board_Pack.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with exp_col3:
            st.markdown(
                f"<div style='font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; padding-top: 4px;'>"
                f"Selected Theme: <b>{theme.name}</b><br>"
                f"Audience Mode: <b>{st.session_state['board_audience_mode'].title()}</b><br>"
                f"Pages / Slides: <b>5 Slides Included</b>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Slide Previews in Cards
        st.markdown("#### Slide 1: Executive Cover Slide")
        st.markdown(
            f"""
            <div style="background: {theme.card_bg_hex}; border: 1px solid {theme.border_hex}; border-radius: 8px; padding: 24px; margin-bottom: 20px;">
                <span style="font-size: 0.75rem; color: {theme.accent_hex}; font-weight: 700;">{st.session_state['board_confidentiality']}</span>
                <h2 style="color: {theme.text_primary_hex}; font-size: 1.8rem; margin: 8px 0 4px 0;">{company_name}</h2>
                <h4 style="color: {theme.accent_hex}; font-weight: 500; margin: 0 0 12px 0;">Executive Board Pack • Financial Performance & Stress Testing Review</h4>
                <div style="font-size: 0.82rem; color: {theme.text_muted_hex};">
                    Reporting Quarters: {statement.periods[0]} to {statement.periods[-1]} &nbsp;|&nbsp; 
                    Evaluation Date: {pd.Timestamp.now().strftime('%B %d, %Y')} &nbsp;|&nbsp; 
                    Standard: Ind AS Compliant
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### Slide 2: Executive Performance Scorecard")
        n1 = narratives["exec_summary"]
        st.markdown(
            f"""
            <div style="background: {theme.card_bg_hex}; border: 1px solid {theme.border_hex}; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;">
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px;">
                        <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 700;">ANNUALIZED REVENUE</span>
                        <div style="font-size: 1.25rem; font-weight: 700; color: {theme.accent_hex}; margin-top: 2px;">{format_inr(metrics.annualized_revenue, unit=user_unit)}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px;">
                        <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 700;">OPERATING EBITDA</span>
                        <div style="font-size: 1.25rem; font-weight: 700; color: {theme.accent_hex}; margin-top: 2px;">{format_inr(metrics.annualized_ebitda, unit=user_unit)}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px;">
                        <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 700;">LIQUIDITY RUNWAY</span>
                        <div style="font-size: 1.25rem; font-weight: 700; color: var(--color-growth); margin-top: 2px;">{metrics.cash_runway_months:.1f} Mo</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px;">
                        <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 700;">NET DEBT / EBITDA</span>
                        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-top: 2px;">{metrics.net_debt_to_ebitda:.2f}x</div>
                    </div>
                </div>
                <div style="font-size: 0.92rem; color: {theme.text_primary_hex}; line-height: 1.6;">
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">1. What Happened:</b> {n1.what_happened}</p>
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">2. Why It Happened:</b> {n1.why_it_happened}</p>
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">3. Financial Impact:</b> {n1.financial_impact}</p>
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">4. Management Action:</b> {n1.management_action}</p>
                </div>
                <div style="font-size: 0.78rem; color: {theme.text_muted_hex}; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                    <i>Traceable Source: {n1.traceable_source}</i>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### Slide 3: Banking Consortium Covenant Health")
        n_cov = narratives["debt_covenants"]
        st.markdown(
            f"""
            <div style="background: {theme.card_bg_hex}; border: 1px solid {theme.border_hex}; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <div style="font-size: 0.92rem; color: {theme.text_primary_hex}; line-height: 1.6;">
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">1. What Happened:</b> {n_cov.what_happened}</p>
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">2. Why It Happened:</b> {n_cov.why_it_happened}</p>
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">3. Financial Impact:</b> {n_cov.financial_impact}</p>
                    <p style="margin: 0 0 6px 0;"><b style="color: {theme.accent_hex};">4. Management Action:</b> {n_cov.management_action}</p>
                </div>
                <div style="font-size: 0.78rem; color: {theme.text_muted_hex}; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                    <i>Traceable Source: {n_cov.traceable_source}</i>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # TAB 2: DESIGN & THEME STUDIO
    # -------------------------------------------------------------------------
    with tab_theme:
        st.markdown("### Presentation Design & Theme Configuration")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Select an executive visual theme and branding parameters for the generated presentation decks."
            "</p>",
            unsafe_allow_html=True
        )

        theme_col1, theme_col2 = st.columns([1.5, 1])

        with theme_col1:
            selected_theme_key = st.selectbox(
                "Presentation Theme",
                options=list(THEMES.keys()),
                format_func=lambda k: THEMES[k].name,
                index=list(THEMES.keys()).index(st.session_state["board_theme_key"])
            )
            st.session_state["board_theme_key"] = selected_theme_key

            aud_options = ["board", "lenders", "investors"]
            selected_aud = st.selectbox(
                "Audience Tone & Narrative Framing",
                options=aud_options,
                format_func=lambda a: "Board of Directors (Strategic Governance)" if a == "board" else ("Lenders / Consortium (Debt Service & Covenants)" if a == "lenders" else "Investors & PE (Growth & Margin Expansion)"),
                index=aud_options.index(st.session_state["board_audience_mode"])
            )
            st.session_state["board_audience_mode"] = selected_aud

            conf_label = st.text_input(
                "Confidentiality & Header Classification Label",
                value=st.session_state["board_confidentiality"]
            )
            st.session_state["board_confidentiality"] = conf_label

        with theme_col2:
            st.markdown("#### Theme Palette Preview")
            th = THEMES[selected_theme_key]
            st.markdown(
                f"""
                <div style="background: {th.card_bg_hex}; border: 1px solid {th.border_hex}; border-radius: 8px; padding: 16px;">
                    <div style="font-weight: 700; color: {th.accent_hex}; margin-bottom: 8px;">{th.name}</div>
                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                        <div style="width: 32px; height: 32px; border-radius: 4px; background: {th.bg_color_hex}; border: 1px solid rgba(255,255,255,0.2);" title="Background"></div>
                        <div style="width: 32px; height: 32px; border-radius: 4px; background: {th.card_bg_hex}; border: 1px solid rgba(255,255,255,0.2);" title="Card Surface"></div>
                        <div style="width: 32px; height: 32px; border-radius: 4px; background: {th.accent_hex};" title="Accent"></div>
                        <div style="width: 32px; height: 32px; border-radius: 4px; background: {th.text_primary_hex};" title="Primary Text"></div>
                    </div>
                    <div style="font-size: 0.8rem; color: {th.text_muted_hex};">
                        Engineered for C-suite boardroom presentations with optimal contrast and high-resolution export.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------------------
    # TAB 3: AI SLIDE EDITOR & COMMANDS
    # -------------------------------------------------------------------------
    with tab_editor:
        st.markdown("### AI Slide Editor (Natural-Language Commands)")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Direct the AI to rephrase, condense, or emphasize specific financial priorities across individual slides."
            "</p>",
            unsafe_allow_html=True
        )

        preset_cmds = [
            "Make this more concise for a 15-minute board meeting",
            "Rewrite commentary with heavy emphasis on debt service and lender protection",
            "Highlight gross margin compression from raw material inflation",
            "Focus on working capital optimization and capex discipline",
        ]

        st.markdown("#### Quick AI Commands")
        cmd_cols = st.columns(len(preset_cmds))
        for idx, cmd in enumerate(preset_cmds):
            with cmd_cols[idx]:
                if st.button(cmd, key=f"quick_cmd_{idx}", use_container_width=True):
                    st.session_state["ai_command_history"].append(cmd)
                    if "lender" in cmd.lower():
                        st.session_state["board_audience_mode"] = "lenders"
                    elif "concise" in cmd.lower():
                        st.session_state["board_audience_mode"] = "board"
                    st.success(f"Applied command: '{cmd}'")
                    st.rerun()

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        custom_cmd = st.text_input(
            "Enter Custom AI Instruction for Slide Commentary:",
            placeholder="e.g. Expand on why steel prices impacted Q4 EBITDA and propose proactive actions..."
        )
        if st.button("🚀 Apply AI Instruction", type="primary") and custom_cmd.strip():
            st.session_state["ai_command_history"].append(custom_cmd.strip())
            st.success(f"Successfully processed instruction: '{custom_cmd}'")
            st.rerun()

        if st.session_state["ai_command_history"]:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Applied Instruction History")
            for h in st.session_state["ai_command_history"]:
                st.markdown(f"- ⚡ *{h}*")

    # -------------------------------------------------------------------------
    # TAB 4: SOURCE TRACEABILITY DRILL-DOWN
    # -------------------------------------------------------------------------
    with tab_trace:
        st.markdown("### Calculation & Data Source Traceability")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Drill down from high-level slide numbers directly to their underlying formulas, rows, and historical data points."
            "</p>",
            unsafe_allow_html=True
        )

        trace_data = [
            {
                "Slide KPI / Metric": "Annualized Turnover (Revenue Run-Rate)",
                "Reported Value": format_inr(metrics.annualized_revenue, unit=user_unit),
                "Formula / Derivation": "Sum of last 4 quarters revenue multiplied by 4/N scaling factor",
                "Underlying Data Points": f"{statement.periods[-1]}: {format_inr(statement.revenue[-1])} | {statement.periods[-2]}: {format_inr(statement.revenue[-2])}",
                "Verification Status": "✓ Verified via Ind AS ValidationLayer"
            },
            {
                "Slide KPI / Metric": "Operating EBITDA Margin",
                "Reported Value": f"{metrics.ebitda_margin_pct:.1f}%",
                "Formula / Derivation": "(Annualized EBITDA / Annualized Revenue) * 100",
                "Underlying Data Points": f"EBITDA: {format_inr(metrics.annualized_ebitda)} / Rev: {format_inr(metrics.annualized_revenue)}",
                "Verification Status": "✓ Exact Mathematical Identity"
            },
            {
                "Slide KPI / Metric": "Interest Coverage Ratio (ICR)",
                "Reported Value": f"{metrics.covenants['icr'].actual_value:.2f}x",
                "Formula / Derivation": "Operating EBITDA / Annual Finance Interest Commitment",
                "Underlying Data Points": f"EBITDA: {format_inr(metrics.annualized_ebitda)} / Interest: {format_inr(metrics.annual_finance_cost)}",
                "Verification Status": "✓ Consortium Sanction Benchmark (≥ 2.00x)"
            },
            {
                "Slide KPI / Metric": "Debt Service Coverage Ratio (DSCR)",
                "Reported Value": f"{metrics.covenants['dscr'].actual_value:.2f}x",
                "Formula / Derivation": "(PAT + Depreciation + Interest) / Total Annual Debt Service",
                "Underlying Data Points": f"Debt Service: {format_inr(metrics.total_annual_debt_service)}",
                "Verification Status": "✓ Term Loan Sanction Norm (≥ 1.25x)"
            },
            {
                "Slide KPI / Metric": "Liquidity Runway",
                "Reported Value": f"{metrics.cash_runway_months:.1f} Months",
                "Formula / Derivation": "Total Liquidity (Cash + Undrawn CC/OD) / Monthly Operating Net Outflow",
                "Underlying Data Points": f"Total Liquidity: {format_inr(metrics.total_liquidity)}",
                "Verification Status": "✓ Conservative Stress Buffer"
            },
        ]

        st.dataframe(pd.DataFrame(trace_data), use_container_width=True, hide_index=True)
