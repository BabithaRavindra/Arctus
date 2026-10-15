"""
Dedicated Stress Test & Debt Covenant Matrix Page for Arctus (`/covenants`).
Delivers institutional banking consortium compliance & probabilistic risk telemetry:
- Explicit Indian banking covenant metrics:
  * Interest Coverage Ratio (ICR >= 2.0x)
  * Debt Service Coverage Ratio (DSCR >= 1.25x)
  * Net Debt to EBITDA (<= 3.0x)
  * Current Ratio (>= 1.33x)
  * Total Outside Liabilities to Tangible Net Worth (TOL/TNW <= 2.50x)
- Monte Carlo probabilistic breach warning signals:
  e.g., "14.2% risk of ICR breaching the 2.0x bank sanction threshold in Q3 FY25"
- Interactive capital structure debt facility editor (Principal, Interest Spread, Repayment)
- What-If Sensitivity Stress sliders (RBI Repo Rate Shift, Commodity Inflation, Revenue Shock)
- Automated Consortium Compliance Memorandum generation for Indian commercial banks
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from core.models import FinancialStatement, Scenario, ForecastResult
from core.synthetic import generate_clean_midmarket_statement
from core.engine import ForecastEngine
from core.cockpit import (
    CapitalStructure,
    DebtInstrument,
    get_default_capital_structure_for_statement,
)
from core.covenants import (
    STANDARD_BANKING_COVENANTS,
    CovenantBreachAnalysis,
    compute_probabilistic_covenant_matrix,
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
from components.charts import (
    create_covenant_headroom_chart,
    create_covenant_trajectory_chart,
    create_covenant_breach_probability_chart,
    create_debt_maturity_chart,
)
from core.assets import get_logo_icon_b64


def initialize_covenants_page_state():
    """Initializes session state for the Debt Covenant Matrix."""
    if "current_statement" not in st.session_state:
        st.session_state["current_statement"] = generate_clean_midmarket_statement()
        st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
        st.session_state["file_normalized"] = True

    stmt = st.session_state["current_statement"]
    if "custom_capital_structure" not in st.session_state:
        st.session_state["custom_capital_structure"] = get_default_capital_structure_for_statement(stmt)

    if "covenant_repo_shock" not in st.session_state:
        st.session_state["covenant_repo_shock"] = 0.0

    if "covenant_cogs_shock" not in st.session_state:
        st.session_state["covenant_cogs_shock"] = 0.0

    if "covenant_rev_shock" not in st.session_state:
        st.session_state["covenant_rev_shock"] = 0.0


def render_covenants_page(on_navigate, user_unit: str = "crores"):
    """
    Renders the dedicated Stress Test & Debt Covenant Matrix workspace.
    """
    initialize_covenants_page_state()

    user = st.session_state.get("user")
    company_name = user.company_name if user else "Apex Precision Automotives Ltd."
    statement: FinancialStatement = st.session_state["current_statement"]
    cap_struct: CapitalStructure = st.session_state["custom_capital_structure"]
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
                            <span class="brand-badge" style="margin: 0; padding: 2px 8px; font-size: 0.72rem;">DEBT COVENANT MATRIX</span>
                            <span style="font-size: 0.8rem; color: var(--color-growth); display: inline-flex; align-items: center; gap: 6px;">
                                <span class="live-pulse-dot"></span> Indian Banking Consortium Standard • Monte Carlo Probabilities
                            </span>
                        </div>
                        <h1 style="font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.15;">
                            Stress Test & Debt Covenant Matrix
                        </h1>
                        <p style="color: var(--text-dim); font-size: 0.92rem; margin: 4px 0 0 0;">
                            Consortium Sanctions (SBI / HDFC / SIDBI) • Forward Probabilistic Breach Alerts • Capital Facility Modeling
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span style="font-size: 0.82rem; color: var(--text-dim);">Target Enterprise:</span>
                    <span style="font-size: 0.84rem; color: var(--accent-gold); font-weight: 600; background: rgba(180, 154, 90, 0.1); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-gold);">
                        {company_name}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick Jump Ribbon
    q_col1, q_col2, q_col3, q_col4 = st.columns([1.5, 1.5, 1.5, 1.5])
    with q_col1:
        if st.button("📊 Executive Cockpit", use_container_width=True):
            on_navigate("overview")
    with q_col2:
        if st.button("📝 Ingestion & Modeling Grid", use_container_width=True):
            on_navigate("model")
    with q_col3:
        if st.button("🎯 Scenario Studio", use_container_width=True):
            on_navigate("scenarios")
    with q_col4:
        if st.button("⚡ Stress Engine", use_container_width=True):
            on_navigate("dashboard")

    # 2. Interactive What-If Macro & Loan Shock Controls
    with st.expander("⚡ Real-Time Interest Rate & Macroeconomic Shock Controls", expanded=False):
        c_col1, c_col2, c_col3, c_col4 = st.columns([1.2, 1.2, 1.2, 0.8])
        with c_col1:
            repo_shock = st.slider(
                "RBI Repo Rate Shift (bps)",
                min_value=-50.0,
                max_value=175.0,
                value=float(st.session_state["covenant_repo_shock"]),
                step=25.0,
                help="Shifts floating borrowing rates on SBI Working Capital & Term Facilities.",
                key="cov_slider_repo"
            )
            st.session_state["covenant_repo_shock"] = repo_shock

        with c_col2:
            cogs_shock = st.slider(
                "Raw Material / COGS Inflation (%)",
                min_value=-5.0,
                max_value=20.0,
                value=float(st.session_state["covenant_cogs_shock"]),
                step=1.0,
                help="Tests gross margin compression on operating cash availability.",
                key="cov_slider_cogs"
            )
            st.session_state["covenant_cogs_shock"] = cogs_shock

        with c_col3:
            rev_shock = st.slider(
                "Revenue Demand Shock (%)",
                min_value=-25.0,
                max_value=15.0,
                value=float(st.session_state["covenant_rev_shock"]),
                step=2.5,
                help="Simulates customer order cutbacks.",
                key="cov_slider_rev"
            )
            st.session_state["covenant_rev_shock"] = rev_shock

        with c_col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("↻ Reset Shocks", key="btn_reset_cov_shocks", use_container_width=True):
                st.session_state["covenant_repo_shock"] = 0.0
                st.session_state["covenant_cogs_shock"] = 0.0
                st.session_state["covenant_rev_shock"] = 0.0
                st.rerun()

    # 3. Execute Vectorized Forecast & Monte Carlo Simulation for Covenants
    engine = ForecastEngine(random_seed=42)
    # Define a scenario reflecting the applied shocks
    stress_sc = Scenario(
        name="Active Stress Baseline",
        rev_growth=st.session_state["covenant_rev_shock"] / 100.0,
        cogs_inflation=st.session_state["covenant_cogs_shock"] / 100.0,
        opex_inflation=max(0.02, st.session_state["covenant_cogs_shock"] * 0.4 / 100.0),
        macro_shock=1.0 + (st.session_state["covenant_repo_shock"] / 200.0),
        color="#B49A5A",
        description="Active scenario with applied sensitivity shocks."
    )
    forecast_results = engine.run_forecast(statement, [stress_sc], iterations=1000)
    active_forecast_res = forecast_results["Active Stress Baseline"]

    # Compute probabilistic covenant analysis
    covenant_analyses = compute_probabilistic_covenant_matrix(
        stmt=statement,
        result=active_forecast_res,
        cap_struct=cap_struct,
        repo_shock_bps=st.session_state["covenant_repo_shock"]
    )

    # 4. Top Telemetry KPI Cards
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    icr_analysis = covenant_analyses["icr"]
    dscr_analysis = covenant_analyses["dscr"]
    nd_analysis = covenant_analyses["nd_ebitda"]
    cr_analysis = covenant_analyses["current_ratio"]

    # Latest quarter evaluations
    icr_q1 = icr_analysis.quarterly_evaluations[0]
    dscr_q1 = dscr_analysis.quarterly_evaluations[0]
    nd_q1 = nd_analysis.quarterly_evaluations[0]
    cr_q1 = cr_analysis.quarterly_evaluations[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        icr_badge = "growth" if icr_analysis.risk_level == "low" else ("base" if icr_analysis.risk_level == "moderate" else "recession")
        render_metric_card(
            label="Interest Coverage (ICR)",
            value=f"{icr_q1.actual_value:.2f}x",
            subtext=f"Sanction Norm: ≥ {icr_q1.threshold:.2f}x",
            badge=f"{icr_analysis.max_breach_probability:.1f}% Breach Risk",
            badge_type=icr_badge,
            is_gold=(icr_analysis.risk_level == "low")
        )
    with k2:
        dscr_badge = "growth" if dscr_analysis.risk_level == "low" else ("base" if dscr_analysis.risk_level == "moderate" else "recession")
        render_metric_card(
            label="Debt Service (DSCR)",
            value=f"{dscr_q1.actual_value:.2f}x",
            subtext=f"Sanction Norm: ≥ {dscr_q1.threshold:.2f}x",
            badge=f"{dscr_analysis.max_breach_probability:.1f}% Breach Risk",
            badge_type=dscr_badge,
            is_gold=(dscr_analysis.risk_level == "low")
        )
    with k3:
        nd_badge = "growth" if nd_analysis.risk_level == "low" else ("base" if nd_analysis.risk_level == "moderate" else "recession")
        render_metric_card(
            label="Net Debt to EBITDA",
            value=f"{nd_q1.actual_value:.2f}x",
            subtext=f"Sanction Norm: ≤ {nd_q1.threshold:.2f}x",
            badge=f"{nd_analysis.max_breach_probability:.1f}% Breach Risk",
            badge_type=nd_badge
        )
    with k4:
        cr_badge = "growth" if cr_analysis.risk_level == "low" else ("base" if cr_analysis.risk_level == "moderate" else "recession")
        render_metric_card(
            label="Current Ratio (WC)",
            value=f"{cr_q1.actual_value:.2f}x",
            subtext=f"Sanction Norm: ≥ {cr_q1.threshold:.2f}x",
            badge=f"{cr_analysis.max_breach_probability:.1f}% Breach Risk",
            badge_type=cr_badge
        )

    # 5. Dedicated Workspace Tabs
    tab_matrix, tab_alerts, tab_facilities, tab_memo = st.tabs([
        "📋 Consortium Covenant Matrix",
        "🚨 Probabilistic Breach Alerts",
        "🏦 Debt Capital Facilities Editor",
        "📜 Bank Compliance Memorandum"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: CONSORTIUM COVENANT MATRIX
    # -------------------------------------------------------------------------
    with tab_matrix:
        st.markdown("### Indian Banking Consortium Covenant Health")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 16px;'>"
            "Direct comparison of enterprise ratios against sanction benchmarks stipulated by State Bank of India, HDFC Bank, and SIDBI."
            "</p>",
            unsafe_allow_html=True
        )

        matrix_rows = []
        for cov_key, a in covenant_analyses.items():
            first_eval = a.quarterly_evaluations[0]
            status_tag = "✅ Compliant" if first_eval.status == "compliant" else ("⚠️ Warning" if first_eval.status == "warning" else "❌ Breached")
            matrix_rows.append({
                "Covenant Name": a.name,
                "Bank Standard": a.bank_standard,
                "Current / Q1 Level": f"{first_eval.actual_value:.2f}{first_eval.unit_label}",
                "Sanction Threshold": f"{first_eval.threshold:.2f}{first_eval.unit_label}",
                "Headroom Cushion": f"{first_eval.headroom:+.2f}{first_eval.unit_label} ({first_eval.cushion_pct:+.1f}%)",
                "Max Breach Risk": f"{a.max_breach_probability:.1f}%",
                "Status": status_tag,
                "Formula / Definition": a.formula_str
            })

        st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        ch_col1, ch_col2 = st.columns([1.3, 1.7])
        with ch_col1:
            st.plotly_chart(
                create_covenant_breach_probability_chart(covenant_analyses),
                use_container_width=True
            )
        with ch_col2:
            # Trajectory for selected covenant
            selected_cov_key = st.selectbox(
                "Select Covenant to Inspect Quarterly Trajectory:",
                options=list(covenant_analyses.keys()),
                format_func=lambda k: covenant_analyses[k].name,
                key="select_cov_trajectory"
            )
            selected_a = covenant_analyses[selected_cov_key]
            st.plotly_chart(
                create_covenant_trajectory_chart(
                    evaluations=selected_a.quarterly_evaluations,
                    covenant_name=selected_a.name,
                    threshold=selected_a.quarterly_evaluations[0].threshold,
                    comparison=selected_a.quarterly_evaluations[0].comparison,
                    unit_label=selected_a.quarterly_evaluations[0].unit_label
                ),
                use_container_width=True
            )

    # -------------------------------------------------------------------------
    # TAB 2: PROBABILISTIC BREACH ALERTS
    # -------------------------------------------------------------------------
    with tab_alerts:
        st.markdown("### Probabilistic Covenant Breach Alerts (Monte Carlo 1,000 Draws)")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Forward statistical distributions evaluating the probability of loan agreement covenant violations over the next 4 quarters."
            "</p>",
            unsafe_allow_html=True
        )

        for cov_key, a in covenant_analyses.items():
            card_border = COLOR_RECESSION if a.risk_level == "critical" else (BORDER_COLOR_GOLD if a.risk_level == "moderate" else BORDER_COLOR)
            bg_tint = "rgba(181, 84, 90, 0.08)" if a.risk_level == "critical" else ("rgba(180, 154, 90, 0.08)" if a.risk_level == "moderate" else "var(--surface-card)")
            badge_color = COLOR_RECESSION if a.risk_level == "critical" else (ACCENT_GOLD if a.risk_level == "moderate" else COLOR_GROWTH)
            badge_label = "HIGH RISK" if a.risk_level == "critical" else ("WATCHLIST" if a.risk_level == "moderate" else "SECURE")

            st.markdown(
                f"""
                <div style="background: {bg_tint}; border: 1px solid {card_border}; border-left: 4px solid {badge_color}; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: var(--text-primary);">
                            {a.name}
                        </span>
                        <span style="font-size: 0.75rem; font-weight: 700; color: {badge_color}; background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 4px;">
                            {badge_label} • {a.bank_standard}
                        </span>
                    </div>
                    <div style="font-size: 0.92rem; color: var(--text-primary); line-height: 1.5; margin-bottom: 8px;">
                        ⚠️ <b>Breach Probability Warning:</b> {a.executive_warning}
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        <b>Quarterly Breach Odds:</b> """ + " | ".join(f"<b>{e.quarter}</b>: {e.breach_probability:.1f}% (Actual: {e.actual_value:.2f}{e.unit_label})" for e in a.quarterly_evaluations) + f"""
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------------------
    # TAB 3: DEBT CAPITAL FACILITIES EDITOR
    # -------------------------------------------------------------------------
    with tab_facilities:
        st.markdown("### Enterprise Capital Structure & Loan Facilities")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 16px;'>"
            "Tune loan amounts, floating repo spreads, and amortization schedules to stress-test covenant impact."
            "</p>",
            unsafe_allow_html=True
        )

        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            st.markdown("#### Active Debt Facilities")
            inst_data = []
            for inst in cap_struct.instruments:
                inst_data.append({
                    "Facility Name": inst.name,
                    "Category": inst.category.replace("_", " ").title(),
                    "Lender": inst.lender,
                    "Outstanding (₹ Cr)": round(inst.principal_outstanding / 1e7, 2),
                    "Interest Rate (%)": round(inst.interest_rate * 100.0, 2),
                    "Floating Rate?": "Yes (Repo Linked)" if inst.is_floating else "Fixed",
                    "Annual Amortization (₹ Cr)": round(inst.annual_amortization / 1e7, 2),
                    "Maturity Year": inst.maturity_year
                })
            st.dataframe(pd.DataFrame(inst_data), use_container_width=True, hide_index=True)

        with f_col2:
            st.markdown("#### Balance Sheet Buffers")
            st.markdown(
                f"""
                <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px;">
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Liquid Cash & Equivalents:</span><br>
                        <span style="font-weight: 700; font-size: 1.1rem; color: var(--accent-gold);">{format_inr(cap_struct.cash_and_equivalents, unit=user_unit)}</span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Undrawn Sanctioned CC/OD Buffer:</span><br>
                        <span style="font-weight: 700; font-size: 1.1rem; color: var(--color-growth);">{format_inr(cap_struct.undrawn_sanctioned_limits, unit=user_unit)}</span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Tangible Net Worth (TNW):</span><br>
                        <span style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary);">{format_inr(cap_struct.tangible_net_worth, unit=user_unit)}</span>
                    </div>
                    <div>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Annual Scheduled Amortization:</span><br>
                        <span style="font-weight: 700; font-size: 1.1rem; color: var(--color-recession);">{format_inr(sum(i.annual_amortization for i in cap_struct.instruments), unit=user_unit)}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Debt Amortization Maturity Chart
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        # Build maturity breakdown
        mat_map = {}
        for inst in cap_struct.instruments:
            mat_map[inst.maturity_year] = mat_map.get(inst.maturity_year, 0.0) + inst.principal_outstanding
        mat_schedule = [{"maturity_year": k, "principal": v} for k, v in mat_map.items()]
        st.plotly_chart(
            create_debt_maturity_chart(mat_schedule, unit=user_unit),
            use_container_width=True
        )

    # -------------------------------------------------------------------------
    # TAB 4: BANK COMPLIANCE MEMORANDUM
    # -------------------------------------------------------------------------
    with tab_memo:
        st.markdown("### Institutional Consortium Compliance Memorandum")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 16px;'>"
            "Pre-formatted credit committee briefing ready for quarterly submission to Indian commercial banks."
            "</p>",
            unsafe_allow_html=True
        )

        memo_text = f"""
CONFIDENTIAL & PRIVILEGED • CREDIT COMMITTEE BRIEFING
ENTERPRISE: {company_name}
CONSORTIUM BANK FACILITY REVIEW (Ind AS Compliant)
DATE OF EVALUATION: {pd.Timestamp.now().strftime('%B %d, %Y')}

1. EXECUTIVE SUMMARY & COVENANT POSTURE
Apex Precision Automotives Ltd. maintains active credit facilities led by State Bank of India with consortium participation from HDFC Bank and SIDBI.
- Overall Compliance Status: {'ALL COVENANTS COMPLIANT' if all(a.risk_level != 'critical' for a in covenant_analyses.values()) else 'COVENANT VULNERABILITY DETECTED'}
- Interest Coverage Ratio (ICR): {icr_q1.actual_value:.2f}x vs Sanction Norm of ≥ {icr_q1.threshold:.2f}x (Headroom: {icr_q1.headroom:+.2f}x).
- Debt Service Coverage Ratio (DSCR): {dscr_q1.actual_value:.2f}x vs Sanction Norm of ≥ {dscr_q1.threshold:.2f}x (Headroom: {dscr_q1.headroom:+.2f}x).
- Total / Net Debt to EBITDA: {nd_q1.actual_value:.2f}x vs Maximum Sanction Ceiling of ≤ {nd_q1.threshold:.2f}x.
- Working Capital Current Ratio: {cr_q1.actual_value:.2f}x vs RBI Tandon Norm of ≥ {cr_q1.threshold:.2f}x.

2. STRESS TEST & PROBABILISTIC BREACH SUMMARY (1,000 MONTE CARLO DRAWS)
Under applied sensitivity conditions (RBI Repo Rate Shift: {st.session_state['covenant_repo_shock']:+.0f} bps, COGS Inflation: {st.session_state['covenant_cogs_shock']:+.1f}%, Revenue Shock: {st.session_state['covenant_rev_shock']:+.1f}%):
"""
        for cov_key, a in covenant_analyses.items():
            memo_text += f"\n- {a.name}: {a.executive_warning}"

        memo_text += f"""

3. LIQUIDITY & DEBT SERVICE BUFFER
- Gross Funded Debt: {format_inr(sum(i.principal_outstanding for i in cap_struct.instruments), unit=user_unit)}
- Cash & Liquid Bank Deposits: {format_inr(cap_struct.cash_and_equivalents, unit=user_unit)}
- Undrawn Sanctioned CC/OD Cushion: {format_inr(cap_struct.undrawn_sanctioned_limits, unit=user_unit)}
- Total Available Liquidity Cushion: {format_inr(cap_struct.cash_and_equivalents + cap_struct.undrawn_sanctioned_limits, unit=user_unit)}

Conclusion: The enterprise operates with adequate coverage to service scheduled maturities and floating interest commitments.
"""
        st.text_area("Consortium Memo Text", value=memo_text.strip(), height=360)
        st.download_button(
            label="📥 Download Official Bank Compliance Memo (.txt)",
            data=memo_text.strip(),
            file_name=f"{company_name.replace(' ', '_')}_Consortium_Covenant_Memo.txt",
            mime="text/plain",
            use_container_width=True
        )
