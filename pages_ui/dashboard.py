"""
Main Dashboard View for Arctus.
The core FP&A stress-testing experience featuring:
- Illustrative demo state on launch (never an empty blank page)
- File uploader (CSV / Excel) with multi-sheet auto-detection
- Stage 1 RawNormalizer audit log
- Stage 2 SchemaMapper with RapidFuzz and interactive manual override dropdowns
- Stage 3 ValidationLayer sanity checks & missing quarter interpolation
- Live Indian macroeconomic ticker
- Interactive scenario assumption sliders (Recession, Base, Growth)
- Monte Carlo simulation engine with 1,000 iterations
- CFO-grade Plotly visual dashboard (Comparison, Waterfall, Fan Chart, Tornado)
- CSV export & SQLite scenario run persistence
"""

import time
import streamlit as st
import pandas as pd
import numpy as np

from core.models import FinancialStatement, Scenario, ForecastResult
from core.normalizer import RawNormalizer
from core.mapper import SchemaMapper
from core.validator import ValidationLayer, ValidationError
from core.engine import ForecastEngine
from core.macro import MacroDataFetcher
from core.synthetic import generate_clean_midmarket_statement
from core.database import save_scenario_run
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
    create_scenario_comparison_chart,
    create_waterfall_bridge_chart,
    create_confidence_band_chart,
    create_tornado_chart,
)


def initialize_dashboard_state():
    """Ensures dashboard state variables are initialized with demo data by default."""
    if "current_statement" not in st.session_state:
        # Load realistic demo statement so app is never blank
        st.session_state["current_statement"] = generate_clean_midmarket_statement()
        st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
        st.session_state["file_normalized"] = True
        st.session_state["manual_overrides"] = {}

    if "macro_data" not in st.session_state:
        fetcher = MacroDataFetcher()
        st.session_state["macro_data"] = fetcher.fetch_live_macro()

    if "forecast_results" not in st.session_state:
        st.session_state["forecast_results"] = None


def render_dashboard(user_unit: str = "crores", on_navigate=None):
    """
    Renders the complete Arctus stress-testing workspace.
    """
    initialize_dashboard_state()
    user = st.session_state.get("user")
    company_name = user.company_name if user else "Apex Precision Automotives Ltd."

    from core.assets import get_logo_icon_b64
    logo_icon = get_logo_icon_b64()

    # Top Header
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <img src="{logo_icon}" alt="Arctus" style="height: 48px; width: auto; filter: drop-shadow(0 0 12px rgba(180, 154, 90, 0.3));" />
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                            <span class="brand-badge" style="margin: 0; padding: 2px 8px; font-size: 0.72rem;">QUANTITATIVE ENGINE</span>
                        </div>
                        <h1 style="font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin-bottom: 2px;">
                            FP&A Stress-Testing Engine
                        </h1>
                        <p style="color: var(--text-dim); font-size: 0.92rem; margin: 0;">
                            Target: <span style="color: {ACCENT_GOLD}; font-weight: 600;">{company_name}</span> &nbsp;|&nbsp; Source: {st.session_state.get('statement_source', 'Uploaded File')}
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with h_col2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if on_navigate:
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            with m_col1:
                if st.button("📊 Cockpit", use_container_width=True, help="View Executive Overview"):
                    on_navigate("overview")
            with m_col2:
                if st.button("📝 Grid", use_container_width=True, help="Edit Historical Ingestion & Modeling Grid"):
                    on_navigate("model")
            with m_col3:
                if st.button("🎯 Studio", use_container_width=True, help="Author Custom Scenarios & Probability Weights"):
                    on_navigate("scenarios")
            with m_col4:
                if st.button("🏦 Covenants", use_container_width=True, help="Indian Banking Consortium Covenant Headroom"):
                    on_navigate("covenants")
            with m_col5:
                if st.button("📑 Deck", use_container_width=True, help="Generate Executive Board Presentation"):
                    on_navigate("board_presentation")

    # 1. Live Indian Macroeconomic Telemetry Strip
    render_macro_ticker(st.session_state["macro_data"])

    # 2. File Upload & Ingestion Accordion
    with st.expander("📁 Ingest New P&L Statement (Excel / CSV)", expanded=False):
        up_col1, up_col2 = st.columns([2.5, 1.5])
        with up_col1:
            uploaded_file = st.file_uploader(
                "Drop your company P&L spreadsheet (.xlsx, .xls, .csv)",
                type=["xlsx", "xls", "csv"],
                help="Supports multi-sheet workbooks, merged headers, and Indian accounting formats."
            )
        with up_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("↻ Reload Default ₹50 Cr Demo Model", use_container_width=True):
                st.session_state["current_statement"] = generate_clean_midmarket_statement()
                st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
                st.session_state["forecast_results"] = None
                st.session_state["manual_overrides"] = {}
                st.rerun()

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name

            # Run Stage 1: RawNormalizer
            normalizer = RawNormalizer()
            try:
                norm_res = normalizer.process(file_bytes, filename)
                df_norm = norm_res["dataframe"]
                line_col = norm_res["line_item_column"]
                period_cols = norm_res["period_columns"]
                raw_labels = df_norm[line_col].astype(str).tolist()

                st.success(f"Stage 1 Normalization Complete: Extracted {len(period_cols)} periods across {len(df_norm)} line items.")
                
                with st.expander("Inspection: Normalizer Audit Trail", expanded=False):
                    for entry in norm_res["audit_trail"]:
                        st.markdown(f"• <span style='font-family: monospace; font-size: 0.85rem; color: #E5E5E5;'>{entry}</span>", unsafe_allow_html=True)

                # Check period continuity
                continuity = ValidationLayer.check_period_continuity(period_cols)
                if not continuity["is_continuous"]:
                    st.warning(
                        f"Missing periods detected in chronology: {', '.join(continuity['missing_quarters'])}. "
                        "Would you like Arctus to interpolate missing quarters linearly?"
                    )
                    if st.button("Interpolate Missing Quarters Linearly"):
                        df_norm, period_cols = ValidationLayer.interpolate_missing_quarters(
                            df_norm.set_index(line_col), period_cols, continuity["missing_quarters"]
                        )
                        df_norm = df_norm.reset_index()
                        st.success("Quarters interpolated successfully.")

                # Stage 2: SchemaMapper
                mapper = SchemaMapper()
                map_res = mapper.auto_map_schema(
                    raw_labels=raw_labels,
                    manual_overrides=st.session_state.get("manual_overrides", {})
                )

                st.markdown("#### Schema Mapping Review")
                st.markdown(
                    "<p style='font-size: 0.85rem; color: rgba(255,255,255,0.7);'>"
                    "Verify auto-mapped Indian accounting rows. If confidence is low, pick the appropriate row from the dropdown."
                    "</p>",
                    unsafe_allow_html=True
                )

                # Mapping Table and Override Controls
                col_m1, col_m2 = st.columns(2)
                override_dict = st.session_state.get("manual_overrides", {}).copy()

                metrics_to_show = list(mapper.STANDARD_METRICS)
                for idx, metric in enumerate(metrics_to_show):
                    curr_col = col_m1 if idx % 2 == 0 else col_m2
                    with curr_col:
                        assigned_label = map_res["mapping"].get(metric)
                        conf = map_res["confidence_scores"].get(metric, 0.0)

                        conf_color = COLOR_GROWTH if conf >= 80 else (COLOR_BASE if conf >= 60 else COLOR_RECESSION)
                        options = ["-- None / Auto Derive --"] + raw_labels
                        default_idx = (options.index(assigned_label) if assigned_label in options else 0)

                        selected_label = st.selectbox(
                            f"{metric.upper()} (Confidence: {conf}%)",
                            options=options,
                            index=default_idx,
                            key=f"map_select_{metric}"
                        )

                        if selected_label != "-- None / Auto Derive --":
                            override_dict[metric] = selected_label
                        elif metric in override_dict:
                            del override_dict[metric]

                st.session_state["manual_overrides"] = override_dict

                if st.button("Apply Mapping & Ingest into Engine", type="primary"):
                    std_df = mapper.construct_standardized_statement(
                        df_norm, line_col, period_cols, map_res["mapping"]
                    )
                    stmt, issues = ValidationLayer.create_verified_statement(std_df, period_cols)
                    st.session_state["current_statement"] = stmt
                    st.session_state["statement_source"] = f"Uploaded: {filename}"
                    st.session_state["forecast_results"] = None
                    st.success("Financial statement verified and loaded into the stress-testing engine!")
                    st.rerun()

            except Exception as e:
                st.error(f"Ingestion Notice: {str(e)}")
                st.info("Ensure your file contains recognized P&L columns or utilize the demo model to explore.")

    # 3. Current Statement Summary Bar
    stmt: FinancialStatement = st.session_state["current_statement"]
    run_rate = stmt.get_run_rate()

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        render_metric_card("Historical Revenue Run-Rate", format_inr(run_rate["annualized_revenue"], unit=user_unit), f"Across {len(stmt.periods)} quarters", is_gold=True)
    with col_k2:
        render_metric_card("Operating EBITDA Run-Rate", format_inr(run_rate["annualized_ebitda"], unit=user_unit), f"Margin: {run_rate['latest_ebitda_margin']:.1f}%", is_gold=True)
    with col_k3:
        render_metric_card("Gross Profit Margin", f"{run_rate['latest_gross_margin']:.1f}%", "Latest historical quarter")
    with col_k4:
        render_metric_card("Data Health & Continuity", "Continuous", f"{stmt.periods[0]} to {stmt.periods[-1]}", badge="Verified", badge_type="growth")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Macroeconomic Scenario Sliders
    st.markdown("### Economic Scenario Assumptions")
    st.markdown(
        "<p style='color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: -6px; margin-bottom: 16px;'>"
        "Parameters are pre-seeded using live Indian economic data (RBI 6.50% repo rate, MoSPI 4.85% CPI inflation). Adjust to simulate shocks."
        "</p>",
        unsafe_allow_html=True
    )

    macro_defaults = MacroDataFetcher.get_scenario_defaults(st.session_state["macro_data"])

    sc_col1, sc_col2, sc_col3 = st.columns(3)

    # Scenario 1: Recession
    with sc_col1:
        st.markdown(
            f"""
            <div style="background: rgba(181, 84, 90, 0.08); border: 1px solid {COLOR_RECESSION}; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px;">
                <span style="color: {COLOR_RECESSION}; font-weight: 700;">Recession / Stress Shock</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        rec_growth = st.slider("Revenue Growth (%)", -25.0, 10.0, float(macro_defaults["Recession"]["rev_growth"] * 100), step=0.5, key="rec_g") / 100.0
        rec_cogs = st.slider("COGS Inflation (%)", 0.0, 20.0, float(macro_defaults["Recession"]["cogs_inflation"] * 100), step=0.5, key="rec_c") / 100.0
        rec_opex = st.slider("OPEX Inflation (%)", 0.0, 20.0, float(macro_defaults["Recession"]["opex_inflation"] * 100), step=0.5, key="rec_o") / 100.0
        rec_shock = st.slider("Macro Rate Shock Multiplier", 1.0, 1.5, float(macro_defaults["Recession"]["macro_shock"]), step=0.05, key="rec_s")

    # Scenario 2: Base
    with sc_col2:
        st.markdown(
            f"""
            <div style="background: rgba(252, 163, 17, 0.08); border: 1px solid {COLOR_BASE}; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px;">
                <span style="color: {COLOR_BASE}; font-weight: 700;">Base / Prevailing Trend</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        base_growth = st.slider("Revenue Growth (%)", -10.0, 25.0, float(macro_defaults["Base"]["rev_growth"] * 100), step=0.5, key="base_g") / 100.0
        base_cogs = st.slider("COGS Inflation (%)", 0.0, 15.0, float(macro_defaults["Base"]["cogs_inflation"] * 100), step=0.5, key="base_c") / 100.0
        base_opex = st.slider("OPEX Inflation (%)", 0.0, 15.0, float(macro_defaults["Base"]["opex_inflation"] * 100), step=0.5, key="base_o") / 100.0
        base_shock = st.slider("Macro Rate Shock Multiplier", 0.8, 1.3, float(macro_defaults["Base"]["macro_shock"]), step=0.05, key="base_s")

    # Scenario 3: Growth
    with sc_col3:
        st.markdown(
            f"""
            <div style="background: rgba(122, 155, 118, 0.08); border: 1px solid {COLOR_GROWTH}; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px;">
                <span style="color: {COLOR_GROWTH}; font-weight: 700;">Expansion / Growth</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        growth_rev = st.slider("Revenue Growth (%)", 0.0, 40.0, float(macro_defaults["Growth"]["rev_growth"] * 100), step=0.5, key="grow_g") / 100.0
        growth_cogs = st.slider("COGS Inflation (%)", 0.0, 12.0, float(macro_defaults["Growth"]["cogs_inflation"] * 100), step=0.5, key="grow_c") / 100.0
        growth_opex = st.slider("OPEX Inflation (%)", 0.0, 12.0, float(macro_defaults["Growth"]["opex_inflation"] * 100), step=0.5, key="grow_o") / 100.0
        growth_shock = st.slider("Macro Rate Shock Multiplier", 0.7, 1.2, float(macro_defaults["Growth"]["macro_shock"]), step=0.05, key="grow_s")

    # Construct Scenario objects
    scenarios = [
        Scenario("Recession", rec_growth, rec_cogs, rec_opex, rec_shock, color=COLOR_RECESSION),
        Scenario("Base", base_growth, base_cogs, base_opex, base_shock, color=COLOR_BASE),
        Scenario("Growth", growth_rev, growth_cogs, growth_opex, growth_shock, color=COLOR_GROWTH),
    ]

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 5. Execution Trigger
    r_col1, r_col2, r_col3 = st.columns([1, 1.5, 1])
    with r_col2:
        run_btn = st.button("⚡ Run Monte Carlo Stress Test (1,000 Iterations)", type="primary", use_container_width=True)

    # Auto-run on first load or manual button trigger
    if run_btn or st.session_state["forecast_results"] is None:
        with st.spinner("Simulating 1,000 Monte Carlo trajectories across Indian macro shocks..."):
            engine = ForecastEngine(random_seed=42)
            results = engine.run_forecast(stmt, scenarios, iterations=1000)
            st.session_state["forecast_results"] = results
            time.sleep(0.1)

    results = st.session_state["forecast_results"]

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # 6. Stress Test Key Output Metrics Bar
    base_res = results["Base"]
    rec_res = results["Recession"]
    growth_res = results["Growth"]

    fwd_base_rev = float(sum(base_res.point_forecast["revenue"]))
    fwd_base_ebitda = float(sum(base_res.point_forecast["ebitda"]))
    fwd_rec_ebitda = float(sum(rec_res.point_forecast["ebitda"]))
    var_90 = float(sum(rec_res.confidence_bands["ebitda"]["p10"]))

    st.markdown("### Stress-Test Output Telemetry")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        render_metric_card("FY25 Base Forecast Revenue", format_inr(fwd_base_rev, unit=user_unit), "4-quarter cumulative projection", is_gold=True)
    with m_col2:
        render_metric_card("FY25 Base Operating EBITDA", format_inr(fwd_base_ebitda, unit=user_unit), f"Margin: {(fwd_base_ebitda/fwd_base_rev*100):.1f}%", is_gold=True)
    with m_col3:
        render_metric_card("Recession Stress EBITDA", format_inr(fwd_rec_ebitda, unit=user_unit), f"Downside: {format_inr(fwd_rec_ebitda - fwd_base_ebitda, unit=user_unit)}", badge="Downside", badge_type="recession")
    with m_col4:
        loss_prob = rec_res.loss_probability
        badge_type = "growth" if loss_prob < 5 else ("base" if loss_prob < 20 else "recession")
        render_metric_card("90% Value at Risk (VaR)", format_inr(var_90, unit=user_unit), f"Loss Probability: {loss_prob:.1f}%", badge=f"{loss_prob:.1f}% Risk", badge_type=badge_type)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 7. CFO Visual Dashboard Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Scenario Comparison",
        "🌊 EBITDA Waterfall Bridge",
        "📈 Monte Carlo Probability Fan",
        "🌪 Tornado Sensitivity",
        "📋 Full Financial Statement Table",
    ])

    with tab1:
        st.plotly_chart(
            create_scenario_comparison_chart(results, metric="ebitda", unit=user_unit),
            use_container_width=True
        )

    with tab2:
        sc_choice = st.selectbox("Select Scenario for Waterfall Bridge", ["Recession", "Base", "Growth"], index=0)
        st.plotly_chart(
            create_waterfall_bridge_chart(stmt, results[sc_choice], unit=user_unit),
            use_container_width=True
        )

    with tab3:
        fan_sc = st.selectbox("Select Scenario for Confidence Envelope", ["Base", "Recession", "Growth"], index=0)
        st.plotly_chart(
            create_confidence_band_chart(stmt, results[fan_sc], metric="ebitda", unit=user_unit),
            use_container_width=True
        )

    with tab4:
        st.markdown("#### Assumption Sensitivity Ranking")
        st.markdown(
            "<p style='color: rgba(255,255,255,0.7); font-size: 0.85rem;'>"
            "Measures EBITDA variance generated by a ±10% relative perturbation in each individual assumption."
            "</p>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            create_tornado_chart(base_res.tornado_sensitivities, unit=user_unit),
            use_container_width=True
        )

    with tab5:
        st.markdown("#### Standardized P&L Statement (Historical & Forecast)")
        # Construct comparative table
        fwd_periods = base_res.forecast_periods
        all_periods = list(stmt.periods) + fwd_periods

        metrics = ["Revenue", "COGS", "Gross Profit", "OPEX", "EBITDA", "PBT", "PAT"]
        table_rows = []

        for m in metrics:
            m_key = m.lower().replace(" ", "_")
            hist_vals = getattr(stmt, m_key)
            fwd_vals = base_res.point_forecast[m_key]
            combined = list(hist_vals) + list(fwd_vals)
            formatted = [format_inr(v, unit=user_unit) for v in combined]
            table_rows.append([m] + formatted)

        df_display = pd.DataFrame(table_rows, columns=["Line Item"] + all_periods)
        st.dataframe(df_display.set_index("Line Item"), use_container_width=True)

    # 8. Report Export & Run Persistence
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 1])

    with exp_col1:
        # Export CSV Report
        csv_data = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Stress-Test Report (CSV)",
            data=csv_data,
            file_name=f"Arctus_Stress_Test_{company_name.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col2:
        run_label = st.text_input("Run Name", value=f"Q4 Stress Test - {company_name}", label_visibility="collapsed")

    with exp_col3:
        if st.button("💾 Save Run to Scenario History", use_container_width=True):
            user_id = user.id if user else None
            run_id = save_scenario_run(
                user_id=user_id,
                run_name=run_label,
                company_name=company_name,
                statement=stmt,
                scenarios=scenarios,
                results=results
            )
            st.success(f"Run #{run_id} successfully saved to Scenario History!")
