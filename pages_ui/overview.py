"""
Executive Overview & Cockpit Page for Arctus.
Institutional high-level executive dashboard providing:
- Cash & Liquidity Runway (Months of operating cushion)
- Annualized EBITDA Run-Rate & Operating Efficiency
- Debt Capital Structure & Amortization Maturity Profile
- Indian Banking Covenant Matrix (ICR, DSCR, Net Debt/EBITDA, Current Ratio, TOL/TNW)
- Real-time What-If sensitivity shock recalculations with zero spreadsheet manipulation.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from core.models import FinancialStatement
from core.synthetic import generate_clean_midmarket_statement
from core.cockpit import (
    calculate_cockpit_metrics,
    generate_executive_commentary,
    CockpitMetrics,
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
from components.metrics import render_metric_card, render_macro_ticker
from components.charts import (
    create_liquidity_runway_chart,
    create_debt_maturity_chart,
    create_covenant_headroom_chart,
    create_cash_driver_waterfall,
)
from core.assets import get_logo_icon_b64


def initialize_overview_state():
    """Initializes session state for the Executive Cockpit."""
    if "current_statement" not in st.session_state:
        st.session_state["current_statement"] = generate_clean_midmarket_statement()
        st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
        st.session_state["file_normalized"] = True

    if "cockpit_repo_shock" not in st.session_state:
        st.session_state["cockpit_repo_shock"] = 0.0

    if "cockpit_cogs_shock" not in st.session_state:
        st.session_state["cockpit_cogs_shock"] = 0.0

    if "cockpit_rev_shock" not in st.session_state:
        st.session_state["cockpit_rev_shock"] = 0.0


def render_overview_page(on_navigate, user_unit: str = "crores"):
    """
    Renders the dedicated Executive Cockpit and Summary screen.
    """
    initialize_overview_state()

    user = st.session_state.get("user")
    company_name = user.company_name if user else "Apex Precision Automotives Ltd."
    statement: FinancialStatement = st.session_state["current_statement"]
    logo_icon = get_logo_icon_b64()

    # 1. Executive Cockpit Header
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <img src="{logo_icon}" alt="Arctus" style="height: 48px; width: auto; filter: drop-shadow(0 0 12px rgba(180, 154, 90, 0.3));" />
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                            <span class="brand-badge" style="margin: 0; padding: 2px 8px; font-size: 0.72rem;">EXECUTIVE COCKPIT</span>
                            <span style="font-size: 0.8rem; color: var(--color-growth); display: inline-flex; align-items: center; gap: 6px;">
                                <span class="live-pulse-dot"></span> Ind AS Compliant • Consortium Sanctions Active
                            </span>
                        </div>
                        <h1 style="font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.15;">
                            {company_name}
                        </h1>
                        <p style="color: var(--text-dim); font-size: 0.92rem; margin: 4px 0 0 0;">
                            C-Suite Financial Health • Debt Service Amortization • Banking Covenant Headroom
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span style="font-size: 0.82rem; color: var(--text-dim);">Model Source:</span>
                    <span style="font-size: 0.84rem; color: var(--accent-gold); font-weight: 600; background: rgba(180, 154, 90, 0.1); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-gold);">
                        {st.session_state.get('statement_source', 'Active Financial Statement')}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick Jump to Modeling Grid, Scenario Studio, Covenants, Board Deck & Stress Engine Ribbon
    q_col1, q_col2, q_col3, q_col4, q_col5 = st.columns(5)
    with q_col1:
        if st.button("📝 Modeling Grid", use_container_width=True, help="Tweak historical numbers, add ledger accounts or custom quarters"):
            on_navigate("model")
    with q_col2:
        if st.button("🎯 Scenario Studio", use_container_width=True, help="Author custom scenarios and probability weights"):
            on_navigate("scenarios")
    with q_col3:
        if st.button("🏦 Covenant Matrix", use_container_width=True, help="Inspect Indian banking consortium covenant headroom & breach probabilities"):
            on_navigate("covenants")
    with q_col4:
        if st.button("📑 Board Deck", use_container_width=True, help="Generate executive board presentation decks (PPTX / PDF)"):
            on_navigate("board_presentation")
    with q_col5:
        if st.button("⚡ Stress Engine", use_container_width=True, help="Run Monte Carlo simulations and macroeconomic sensitivity tests"):
            on_navigate("dashboard")

    # 2. Interactive What-If Shock Control Panel (Zero Spreadsheet Manipulation)
    with st.expander("⚡ Real-Time Macro Shock Simulator (What-If Controls)", expanded=False):
        st.markdown(
            "<p style='color: var(--text-muted); font-size: 0.88rem; margin-top: -4px; margin-bottom: 16px;'>"
            "Instantly test how changes in the RBI Repo Rate, raw material inflation, or revenue shocks impact "
            "your cash runway and loan covenants without touching raw spreadsheets."
            "</p>",
            unsafe_allow_html=True
        )

        c_col1, c_col2, c_col3, c_col4 = st.columns([1.2, 1.2, 1.2, 0.8])
        with c_col1:
            repo_shock = st.slider(
                "RBI Repo Rate Shift (bps)",
                min_value=-50.0,
                max_value=150.0,
                value=float(st.session_state["cockpit_repo_shock"]),
                step=25.0,
                help="Applies directly to floating-rate working capital and term loans.",
                key="cockpit_slider_repo"
            )
            st.session_state["cockpit_repo_shock"] = repo_shock

        with c_col2:
            cogs_shock = st.slider(
                "Raw Material / COGS Inflation (%)",
                min_value=-5.0,
                max_value=15.0,
                value=float(st.session_state["cockpit_cogs_shock"]),
                step=1.0,
                help="Simulates commodity price inflation (Steel, Crude derivatives, Chemicals).",
                key="cockpit_slider_cogs"
            )
            st.session_state["cockpit_cogs_shock"] = cogs_shock

        with c_col3:
            rev_shock = st.slider(
                "Revenue Demand Shift (%)",
                min_value=-20.0,
                max_value=15.0,
                value=float(st.session_state["cockpit_rev_shock"]),
                step=2.5,
                help="Simulates volume changes in customer orders and market demand.",
                key="cockpit_slider_rev"
            )
            st.session_state["cockpit_rev_shock"] = rev_shock

        with c_col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("↻ Reset Shocks", use_container_width=True):
                st.session_state["cockpit_repo_shock"] = 0.0
                st.session_state["cockpit_cogs_shock"] = 0.0
                st.session_state["cockpit_rev_shock"] = 0.0
                st.rerun()

    # Calculate live cockpit metrics based on active statement and sensitivity sliders
    metrics: CockpitMetrics = calculate_cockpit_metrics(
        stmt=statement,
        repo_rate_shock_bps=st.session_state["cockpit_repo_shock"],
        cogs_inflation_pct=st.session_state["cockpit_cogs_shock"],
        revenue_shock_pct=st.session_state["cockpit_rev_shock"],
        company_name=company_name
    )

    # 3. Top 4 Executive KPI Telemetry Cards
    icr = metrics.covenants["icr"]
    dscr = metrics.covenants["dscr"]

    # Runway Badge Type
    runway_badge_type = "growth" if metrics.runway_status == "healthy" else ("base" if metrics.runway_status == "adequate" else "recession")
    runway_badge_label = f"{metrics.cash_runway_months:.1f} Mo Runway"

    # Covenant Overall Status Badge
    cov_badge_type = "growth" if metrics.all_covenants_compliant else "recession"
    cov_badge_label = f"{metrics.covenants_passed_count}/{metrics.covenants_total_count} Compliant"

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        render_metric_card(
            label="Cash & Liquidity Cushion",
            value=format_inr(metrics.total_liquidity, unit=user_unit),
            subtext=f"Cash + Undrawn CC/OD limits ({metrics.cash_runway_months:.1f} Mo buffer)",
            is_gold=True,
            badge=runway_badge_label,
            badge_type=runway_badge_type
        )
    with col_k2:
        render_metric_card(
            label="Annualized Operating EBITDA",
            value=format_inr(metrics.annualized_ebitda, unit=user_unit),
            subtext=f"Margin: {metrics.ebitda_margin_pct:.1f}% | Revenue: {format_inr(metrics.annualized_revenue, unit=user_unit)}",
            is_gold=True
        )
    with col_k3:
        nd_status = "growth" if metrics.net_debt_to_ebitda <= 2.5 else ("base" if metrics.net_debt_to_ebitda <= 3.0 else "recession")
        render_metric_card(
            label="Consortium Net Debt / EBITDA",
            value=f"{metrics.net_debt_to_ebitda:.2f}x",
            subtext=f"Net Debt: {format_inr(metrics.net_debt, unit=user_unit)} (Cap: ≤3.00x)",
            badge=f"Gearing {metrics.covenants['tol_tnw'].actual_value:.2f}x",
            badge_type=nd_status
        )
    with col_k4:
        icr_badge_type = "growth" if icr.status == "compliant" else ("base" if icr.status == "warning" else "recession")
        render_metric_card(
            label="Interest Coverage Ratio (ICR)",
            value=f"{icr.actual_value:.2f}x",
            subtext=f"Covenant Floor: ≥2.00x (Headroom: {icr.cushion_pct:+.1f}%)",
            badge=cov_badge_label,
            badge_type=cov_badge_type
        )

    # Covenant Warning Banner if shocks cause covenant breach
    if not metrics.all_covenants_compliant:
        st.markdown(
            f"""
            <div style="background: rgba(181, 84, 90, 0.12); border: 1px solid var(--color-recession); border-radius: 10px; padding: 12px 18px; margin: 16px 0;">
                <strong style="color: var(--color-recession);">⚠️ Bank Covenant Stress Warning:</strong>
                <span style="color: var(--text-primary); font-size: 0.9rem;">
                    One or more consortium covenants are approaching or breaching banking thresholds under the active shock scenario.
                    Review the Covenant Health tab below to inspect headroom cushions.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Executive Navigation & Action Ribbon
    act_col1, act_col2, act_col3 = st.columns([2.2, 1.2, 1.0])
    with act_col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; height: 100%;">
                <span style="font-size: 0.85rem; color: var(--text-dim);">Executive Actions:</span>
                <span style="font-size: 0.85rem; color: var(--accent-gold); font-weight: 600;">
                    • 12-Month Liquidity Forecast Active &nbsp;• Blended Debt Cost: {metrics.blended_interest_rate_pct:.2f}%
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with act_col2:
        # One-Click Export Brief
        brief_data = pd.DataFrame([
            {"Metric": "Company Name", "Value": company_name},
            {"Metric": "Annualized Revenue", "Value": format_inr(metrics.annualized_revenue, unit=user_unit)},
            {"Metric": "Annualized EBITDA", "Value": format_inr(metrics.annualized_ebitda, unit=user_unit)},
            {"Metric": "EBITDA Margin", "Value": f"{metrics.ebitda_margin_pct:.2f}%"},
            {"Metric": "Total Liquid Cushion", "Value": format_inr(metrics.total_liquidity, unit=user_unit)},
            {"Metric": "Cash Runway (Months)", "Value": f"{metrics.cash_runway_months:.1f}"},
            {"Metric": "Gross Debt", "Value": format_inr(metrics.gross_debt, unit=user_unit)},
            {"Metric": "Net Debt", "Value": format_inr(metrics.net_debt, unit=user_unit)},
            {"Metric": "Net Debt / EBITDA", "Value": f"{metrics.net_debt_to_ebitda:.2f}x"},
            {"Metric": "Interest Coverage Ratio (ICR)", "Value": f"{icr.actual_value:.2f}x"},
            {"Metric": "Debt Service Coverage Ratio (DSCR)", "Value": f"{dscr.actual_value:.2f}x"},
            {"Metric": "Current Ratio", "Value": f"{metrics.covenants['current_ratio'].actual_value:.2f}x"},
            {"Metric": "TOL / TNW Gearing", "Value": f"{metrics.covenants['tol_tnw'].actual_value:.2f}x"},
            {"Metric": "All Covenants Compliant", "Value": "Yes" if metrics.all_covenants_compliant else "No"},
        ])
        st.download_button(
            label="📥 Export Executive Brief (CSV)",
            data=brief_data.to_csv(index=False).encode("utf-8"),
            file_name=f"Arctus_Executive_Brief_{company_name.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with act_col3:
        if st.button("⚡ Open Stress Engine →", type="primary", use_container_width=True):
            on_navigate("dashboard")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 5. Core Analytical Cockpit Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌊 Liquidity & Cash Runway",
        "🏛 Debt Capital Structure",
        "⚖ Bank Covenant Headroom",
        "📝 Executive Board Commentary"
    ])

    # TAB 1: LIQUIDITY RUNWAY
    with tab1:
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.88rem; margin-top: 4px; margin-bottom: 16px;'>"
            "Month-by-month liquidity balance projection accounting for operating cash flows, working capital cycles, "
            "and scheduled debt service against a conservative 4% operational buffer."
            "</p>",
            unsafe_allow_html=True
        )

        c_liq1, c_liq2 = st.columns([2.4, 1.2])
        with c_liq1:
            st.plotly_chart(
                create_liquidity_runway_chart(metrics.monthly_liquidity_trajectory, unit=user_unit),
                use_container_width=True
            )
        with c_liq2:
            st.markdown("#### Liquidity Schedule")
            df_liq = pd.DataFrame([
                {
                    "Month": item["month_label"],
                    "Balance": format_inr(item["liquidity_balance"], unit=user_unit),
                    "Net Flow": format_inr(item["net_cash_flow"], unit=user_unit),
                    "Status": "Safe" if item["is_above_buffer"] else "Low Buffer"
                }
                for item in metrics.monthly_liquidity_trajectory
            ])
            st.dataframe(df_liq, use_container_width=True, height=330, hide_index=True)

    # TAB 2: DEBT CAPITAL STRUCTURE & MATURITY
    with tab2:
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.88rem; margin-top: 4px; margin-bottom: 16px;'>"
            "Consolidated enterprise debt structure, active lender consortium facilities, interest rate benchmarking, "
            "and annual debt service amortization schedule."
            "</p>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            create_debt_maturity_chart(metrics.debt_maturity_schedule, unit=user_unit),
            use_container_width=True
        )

        st.markdown("#### Debt Facilities & Lender Terms")
        df_debt = pd.DataFrame([
            {
                "Facility Name": d["facility_name"],
                "Lender": d["lender"],
                "Category": d["category"],
                "Principal Outstanding": format_inr(d["principal"], unit=user_unit),
                "Interest Rate": f"{d['interest_rate_pct']:.2f}%",
                "Rate Type": "Floating (Repo-Linked)" if d["is_floating"] else "Fixed",
                "Annual Amortization": format_inr(d["annual_amortization"], unit=user_unit),
                "Maturity": d["maturity_year"]
            }
            for d in metrics.debt_maturity_schedule
        ])
        st.dataframe(df_debt, use_container_width=True, hide_index=True)

        st.markdown(
            f"""
            <div style="display: flex; gap: 24px; padding: 14px 18px; background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; margin-top: 14px; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase;">Total Gross Debt:</span>
                    <strong style="font-size: 1rem; color: var(--text-primary); margin-left: 6px;">{format_inr(metrics.gross_debt, unit=user_unit)}</strong>
                </div>
                <div>
                    <span style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase;">Annual Finance Cost:</span>
                    <strong style="font-size: 1rem; color: var(--accent-gold); margin-left: 6px;">{format_inr(metrics.annual_finance_cost, unit=user_unit)}</strong>
                </div>
                <div>
                    <span style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase;">Annual Principal Repayment:</span>
                    <strong style="font-size: 1rem; color: var(--color-growth); margin-left: 6px;">{format_inr(metrics.annual_principal_repayment, unit=user_unit)}</strong>
                </div>
                <div>
                    <span style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase;">Blended Rate of Borrowing:</span>
                    <strong style="font-size: 1rem; color: var(--text-primary); margin-left: 6px;">{metrics.blended_interest_rate_pct:.2f}% p.a.</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # TAB 3: BANK COVENANT HEADROOM
    with tab3:
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.88rem; margin-top: 4px; margin-bottom: 16px;'>"
            "Consortium loan covenant matrix based on RBI guidelines and Indian commercial bank sanction letters "
            "(SBI, HDFC, ICICI, SIDBI). Evaluates headroom cushion against financial default covenants."
            "</p>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            create_covenant_headroom_chart(metrics.covenants),
            use_container_width=True
        )

        st.markdown("#### Covenant Compliance Matrix")
        cov_rows = []
        for key, cov in metrics.covenants.items():
            status_indicator = "✅ Compliant" if cov.status == "compliant" else ("⚠️ Warning" if cov.status == "warning" else "❌ Breached")
            headroom_str = f"{cov.headroom:+.2f}{cov.unit_label} ({cov.cushion_pct:+.1f}%)"
            cov_rows.append({
                "Covenant Name": cov.name,
                "Actual Ratio": f"{cov.actual_value:.2f}{cov.unit_label}",
                "Sanction Threshold": f"{cov.threshold:.2f}{cov.unit_label}",
                "Headroom Cushion": headroom_str,
                "Compliance Status": status_indicator,
                "Bank Standard": cov.bank_standard,
                "Description": cov.description
            })

        df_cov = pd.DataFrame(cov_rows)
        st.dataframe(df_cov, use_container_width=True, hide_index=True)

    # TAB 4: EXECUTIVE COMMENTARY & CASH WATERFALL
    with tab4:
        st.markdown("#### Institutional CFO Briefing")
        commentary = generate_executive_commentary(metrics)
        st.markdown(
            f"""
            <div style="background: var(--surface-card); border-left: 4px solid var(--accent-gold); border-radius: 8px; padding: 20px 24px; margin-bottom: 24px;">
                <div style="font-size: 0.98rem; line-height: 1.7; color: var(--text-primary);">
                    {commentary}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(
            create_cash_driver_waterfall(metrics, unit=user_unit),
            use_container_width=True
        )
