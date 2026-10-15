"""
Scenario Studio Page for Arctus (`/scenarios`).
Enables CFOs and FP&A teams to:
- Author unlimited custom stress-test scenarios beyond the fixed presets.
- Configure macroeconomic assumptions (Revenue Growth, COGS Inflation, OPEX Inflation, Macro Rate Shock).
- Load curated real-world Indian stress presets:
  * US Tariff Shock (-12% Rev, +8% COGS, 1.25x Debt shock)
  * Red Sea Logistics Spike (-4% Rev, +15% COGS freight, 1.20x shock)
  * Steel & Commodity Surge +25% (-2% Rev, +22% COGS, 1.15x shock)
  * SBI Loan Capex Expansion (+24% Rev, +6% COGS, +18% OPEX, 1.35x capital shock)
  * IT Services Bench Crunch (-15% Rev, +2% COGS, +10% OPEX, 1.10x shock)
- Assign custom probability weights (e.g., 20% Recession, 60% Base, 20% Growth).
- Compute dynamic blended probability-weighted forecasts and value-at-risk metrics.
- Seamlessly push tailored scenario sets directly into the Monte Carlo Simulation Engine.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from core.models import FinancialStatement, Scenario, ForecastResult
from core.engine import ForecastEngine
from core.macro import MacroDataFetcher
from core.synthetic import generate_clean_midmarket_statement
from core.database import (
    save_custom_scenario,
    get_custom_scenarios,
    delete_custom_scenario,
    save_scenario_run,
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
    create_scenario_comparison_chart,
    create_scenario_probability_pie_chart,
    create_confidence_band_chart,
)
from core.assets import get_logo_icon_b64


# Real-World Scenario Presets
CURATED_INDUSTRY_SCENARIO_PRESETS = [
    {
        "name": "US Tariff & Export Surcharge Shock",
        "rev_growth": -0.12,
        "cogs_inflation": 0.08,
        "opex_inflation": 0.05,
        "macro_shock": 1.25,
        "color": "#D9534F",
        "description": "Simulates 15% reciprocal tariffs on Indian engineering goods and textiles entering North America.",
        "probability_weight": 0.15,
    },
    {
        "name": "Red Sea Freight & Logistics Spike",
        "rev_growth": -0.04,
        "cogs_inflation": 0.15,
        "opex_inflation": 0.09,
        "macro_shock": 1.20,
        "color": "#E67E22",
        "description": "Container freight tripling around Cape of Good Hope with shipment turnaround delays of 21 days.",
        "probability_weight": 0.20,
    },
    {
        "name": "Domestic Steel & Commodity Surge (+25%)",
        "rev_growth": -0.02,
        "cogs_inflation": 0.22,
        "opex_inflation": 0.06,
        "macro_shock": 1.15,
        "color": "#B5545A",
        "description": "Iron ore and hot-rolled coil domestic price surge cutting gross margins by 450 bps.",
        "probability_weight": 0.25,
    },
    {
        "name": "SBI Consortium Capex Expansion",
        "rev_growth": 0.24,
        "cogs_inflation": 0.06,
        "opex_inflation": 0.16,
        "macro_shock": 1.35,
        "color": "#2ECC71",
        "description": "₹15 Cr term debt facility drawn down for greenfield capacity expansion with 18-month payback.",
        "probability_weight": 0.30,
    },
    {
        "name": "IT Services Bench & Margin Crunch",
        "rev_growth": -0.15,
        "cogs_inflation": 0.02,
        "opex_inflation": 0.12,
        "macro_shock": 1.10,
        "color": "#9B59B6",
        "description": "Discretionary cloud contract cancellations and onshore wage hikes reducing operating EBITDA.",
        "probability_weight": 0.10,
    },
]


def initialize_scenarios_state():
    """Initializes session state for the Scenario Studio."""
    if "current_statement" not in st.session_state:
        st.session_state["current_statement"] = generate_clean_midmarket_statement()
        st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
        st.session_state["file_normalized"] = True

    if "macro_data" not in st.session_state:
        fetcher = MacroDataFetcher()
        st.session_state["macro_data"] = fetcher.fetch_live_macro()

    if "active_scenarios_list" not in st.session_state:
        # Default active scenario set with probability weights
        macro_defaults = MacroDataFetcher.get_scenario_defaults(st.session_state["macro_data"])
        st.session_state["active_scenarios_list"] = [
            Scenario(
                name="Recession / Stress Shock",
                rev_growth=macro_defaults["Recession"]["rev_growth"],
                cogs_inflation=macro_defaults["Recession"]["cogs_inflation"],
                opex_inflation=macro_defaults["Recession"]["opex_inflation"],
                macro_shock=macro_defaults["Recession"]["macro_shock"],
                color=COLOR_RECESSION,
                description="Macro slowdown, commodity inflation spike and rate hikes.",
                probability_weight=0.20,
            ),
            Scenario(
                name="Base / Prevailing Trend",
                rev_growth=macro_defaults["Base"]["rev_growth"],
                cogs_inflation=macro_defaults["Base"]["cogs_inflation"],
                opex_inflation=macro_defaults["Base"]["opex_inflation"],
                macro_shock=macro_defaults["Base"]["macro_shock"],
                color=COLOR_BASE,
                description="Status-quo progression adhering to current Indian CPI and GDP growth.",
                probability_weight=0.60,
            ),
            Scenario(
                name="Expansion / High Growth",
                rev_growth=macro_defaults["Growth"]["rev_growth"],
                cogs_inflation=macro_defaults["Growth"]["cogs_inflation"],
                opex_inflation=macro_defaults["Growth"]["opex_inflation"],
                macro_shock=macro_defaults["Growth"]["macro_shock"],
                color=COLOR_GROWTH,
                description="New client wins and scale efficiencies lifting operating leverage.",
                probability_weight=0.20,
            ),
        ]


def render_scenarios_page(on_navigate, user_unit: str = "crores"):
    """
    Renders the dedicated Scenario Studio workspace.
    """
    initialize_scenarios_state()

    user = st.session_state.get("user")
    user_id = user.id if user else None
    company_name = user.company_name if user else "Apex Precision Automotives Ltd."
    statement: FinancialStatement = st.session_state["current_statement"]
    logo_icon = get_logo_icon_b64()

    # 1. Page Header
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <img src="{logo_icon}" alt="Arctus" style="height: 48px; width: auto; filter: drop-shadow(0 0 12px rgba(180, 154, 90, 0.3));" />
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                            <span class="brand-badge" style="margin: 0; padding: 2px 8px; font-size: 0.72rem;">SCENARIO STUDIO</span>
                            <span style="font-size: 0.8rem; color: var(--accent-gold); display: inline-flex; align-items: center; gap: 6px;">
                                Custom Probability-Weighted Stress Modeling
                            </span>
                        </div>
                        <h1 style="font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.15;">
                            Macro Scenario Studio
                        </h1>
                        <p style="color: var(--text-dim); font-size: 0.92rem; margin: 4px 0 0 0;">
                            Author custom economic shock narratives • Tune probability weights • Compute blended corporate forecasts
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span style="font-size: 0.82rem; color: var(--text-dim);">Active Baseline:</span>
                    <span style="font-size: 0.84rem; color: var(--accent-gold); font-weight: 600; background: rgba(180, 154, 90, 0.1); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-gold);">
                        {st.session_state.get('statement_source', 'Active Financial Statement')}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick Jump Navigation Buttons
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        if st.button("📊 Executive Cockpit", use_container_width=True):
            on_navigate("overview")
    with q_col2:
        if st.button("📝 Ingestion & Modeling Grid", use_container_width=True):
            on_navigate("model")
    with q_col3:
        if st.button("🏦 Covenant Matrix", use_container_width=True):
            on_navigate("covenants")
    with q_col4:
        if st.button("⚡ Stress Engine", use_container_width=True):
            on_navigate("dashboard")

    # Studio Workspace Tabs
    tab_active, tab_author, tab_library = st.tabs([
        "🎯 Active Scenarios & Blended Forecast",
        "➕ Scenario Authoring & Presets",
        "📂 Saved Scenario Library"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: ACTIVE SCENARIOS & BLENDED FORECAST
    # -------------------------------------------------------------------------
    with tab_active:
        scenarios: List[Scenario] = st.session_state["active_scenarios_list"]

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                    <h3 style="margin: 0; font-family: 'DM Sans', sans-serif;">Active Stress Scenarios ({len(scenarios)})</h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: var(--text-dim);">
                        Tune probability weights below to compute blended expected outcomes. Total weights are auto-normalized to 100%.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Probability Weight Controls Card
        total_assigned_weight = sum(s.probability_weight for s in scenarios)
        
        weight_cols = st.columns(len(scenarios))
        new_weights = {}

        for idx, sc in enumerate(scenarios):
            with weight_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: var(--surface-card); border-top: 3px solid {sc.color}; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                        <div style="font-weight: 700; font-size: 0.92rem; color: {sc.color}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{sc.name}">
                            {sc.name}
                        </div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">
                            Rev: {sc.rev_growth*100:+.1f}% | COGS: {sc.cogs_inflation*100:+.1f}% | Shock: {sc.macro_shock:.2f}x
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                w = st.slider(
                    f"Weight %",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(sc.probability_weight * 100.0),
                    step=5.0,
                    key=f"sc_weight_slider_{sc.name}_{idx}"
                )
                sc.probability_weight = w / 100.0
                new_weights[sc.name] = w / 100.0

        # Execute Engine Simulation for active scenarios
        engine = ForecastEngine(random_seed=42)
        results = engine.run_forecast(statement, scenarios, iterations=1000)

        # Compute Blended Probability-Weighted Forecast
        blended_res = engine.compute_blended_forecast(results, weights=new_weights)

        # KPI Summary Cards comparing Blended vs Presets
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if blended_res:
            b_rev = float(np.sum(blended_res.point_forecast["revenue"]))
            b_ebitda = float(np.sum(blended_res.point_forecast["ebitda"]))
            b_loss_prob = blended_res.loss_probability
            b_margin = (b_ebitda / b_rev * 100) if b_rev > 0 else 0.0

            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                render_metric_card(
                    "Blended 4Q Expected Revenue",
                    format_inr(b_rev, unit=user_unit),
                    "Probability-Weighted Sum",
                    is_gold=True
                )
            with kpi_col2:
                render_metric_card(
                    "Blended 4Q Expected EBITDA",
                    format_inr(b_ebitda, unit=user_unit),
                    f"Expected Margin: {b_margin:.1f}%",
                    is_gold=True
                )
            with kpi_col3:
                badge_type = "growth" if b_loss_prob < 5.0 else ("base" if b_loss_prob < 20.0 else "recession")
                render_metric_card(
                    "Composite Value-at-Risk",
                    f"{b_loss_prob:.1f}%",
                    "Chance of forward EBITDA loss",
                    badge="VaR Signal",
                    badge_type=badge_type
                )
            with kpi_col4:
                render_metric_card(
                    "Scenario Sample Breadth",
                    f"{len(scenarios)} Scenarios",
                    "1,000 Monte Carlo draws each",
                    badge="Vectorized",
                    badge_type="growth"
                )

        # Charts Section: Probability Donut + Grouped Trajectory Bar
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns([1.1, 2.2])

        with chart_col1:
            st.plotly_chart(
                create_scenario_probability_pie_chart(scenarios),
                use_container_width=True
            )

        with chart_col2:
            st.plotly_chart(
                create_scenario_comparison_chart(results, metric="ebitda", unit=user_unit),
                use_container_width=True
            )

        # Confidence Band Fan Chart for Blended Forecast
        if blended_res:
            st.markdown("#### Blended Expected EBITDA Trajectory (Confidence Bands)")
            st.plotly_chart(
                create_confidence_band_chart(blended_res, metric="ebitda", unit=user_unit),
                use_container_width=True
            )

        # Active Scenarios Management Table
        st.markdown("#### Active Scenario Specifications")
        sc_table_data = []
        for s in scenarios:
            res_s = results.get(s.name)
            s_ebitda = float(np.sum(res_s.point_forecast["ebitda"])) if res_s else 0.0
            sc_table_data.append({
                "Scenario Name": s.name,
                "Probability Weight": f"{s.probability_weight * 100.0:.0f}%",
                "Revenue Growth": f"{s.rev_growth * 100.0:+.1f}%",
                "COGS Inflation": f"{s.cogs_inflation * 100.0:+.1f}%",
                "OPEX Inflation": f"{s.opex_inflation * 100.0:+.1f}%",
                "Macro Shock Multiplier": f"{s.macro_shock:.2f}x",
                "4Q Projected EBITDA": format_inr(s_ebitda, unit=user_unit),
                "Loss Probability (VaR)": f"{res_s.loss_probability:.1f}%" if res_s else "N/A",
                "Narrative / Notes": s.description
            })
        st.dataframe(pd.DataFrame(sc_table_data), use_container_width=True, hide_index=True)

        # Actions Ribbon
        act_col1, act_col2, act_col3 = st.columns([1.5, 1.5, 2])
        with act_col1:
            if st.button("💾 Save Run to History", type="primary", use_container_width=True):
                run_id = save_scenario_run(
                    user_id=user_id,
                    run_name=f"Blended Run ({len(scenarios)} Scenarios)",
                    company_name=company_name,
                    statement=statement,
                    scenarios=scenarios,
                    results=results
                )
                st.success(f"Scenario run persisted successfully (Run ID: #{run_id})!")
        with act_col2:
            if st.button("⚡ Push to Stress Engine", use_container_width=True):
                # Update global simulation session state
                st.session_state["forecast_results"] = results
                on_navigate("dashboard")
        with act_col3:
            if st.button("↻ Reset to Standard 3-Preset Scenarios", use_container_width=True):
                macro_defaults = MacroDataFetcher.get_scenario_defaults(st.session_state["macro_data"])
                st.session_state["active_scenarios_list"] = [
                    Scenario("Recession / Stress Shock", macro_defaults["Recession"]["rev_growth"], macro_defaults["Recession"]["cogs_inflation"], macro_defaults["Recession"]["opex_inflation"], macro_defaults["Recession"]["macro_shock"], color=COLOR_RECESSION, probability_weight=0.20),
                    Scenario("Base / Prevailing Trend", macro_defaults["Base"]["rev_growth"], macro_defaults["Base"]["cogs_inflation"], macro_defaults["Base"]["opex_inflation"], macro_defaults["Base"]["macro_shock"], color=COLOR_BASE, probability_weight=0.60),
                    Scenario("Expansion / High Growth", macro_defaults["Growth"]["rev_growth"], macro_defaults["Growth"]["cogs_inflation"], macro_defaults["Growth"]["opex_inflation"], macro_defaults["Growth"]["macro_shock"], color=COLOR_GROWTH, probability_weight=0.20),
                ]
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: SCENARIO AUTHORING & REAL-WORLD PRESETS
    # -------------------------------------------------------------------------
    with tab_author:
        st.markdown("### Author a Custom Stress Scenario")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Design tailored geopolitical, supply-chain, or financing shocks and add them directly to your simulation queue."
            "</p>",
            unsafe_allow_html=True
        )

        # Quick Load from Real-World Indian Industry Presets
        st.markdown("#### ⚡ Quick-Load Curated Real-World Presets")
        preset_cols = st.columns(len(CURATED_INDUSTRY_SCENARIO_PRESETS))

        for idx, preset in enumerate(CURATED_INDUSTRY_SCENARIO_PRESETS):
            with preset_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: var(--surface-card); border-top: 3px solid {preset['color']}; border-radius: 8px; padding: 12px; height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="font-weight: 700; font-size: 0.84rem; color: {preset['color']};">
                                {preset['name']}
                            </div>
                            <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; line-height: 1.3;">
                                {preset['description']}
                            </div>
                        </div>
                        <div style="font-size: 0.72rem; color: var(--accent-gold); font-weight: 600;">
                            Rev: {preset['rev_growth']*100:+.0f}% | COGS: {preset['cogs_inflation']*100:+.0f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("➕ Add Preset", key=f"btn_add_preset_{idx}", use_container_width=True):
                    # Check if already in active list
                    existing_names = [s.name for s in st.session_state["active_scenarios_list"]]
                    if preset["name"] in existing_names:
                        st.warning(f"'{preset['name']}' is already in your active scenarios.")
                    else:
                        st.session_state["active_scenarios_list"].append(
                            Scenario(
                                name=preset["name"],
                                rev_growth=preset["rev_growth"],
                                cogs_inflation=preset["cogs_inflation"],
                                opex_inflation=preset["opex_inflation"],
                                macro_shock=preset["macro_shock"],
                                color=preset["color"],
                                description=preset["description"],
                                probability_weight=preset["probability_weight"],
                            )
                        )
                        st.success(f"Added '{preset['name']}' to active scenarios!")
                        st.rerun()

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🛠️ Custom Scenario Parameter Builder")

        with st.form("custom_scenario_builder_form"):
            b_col1, b_col2 = st.columns([1.5, 1])

            with b_col1:
                sc_name = st.text_input(
                    "Scenario Name",
                    placeholder="e.g. Red Sea Freight Escalation + Capex Delay",
                    help="Descriptive title identifying this business case."
                )
                sc_desc = st.text_area(
                    "Narrative & Context",
                    placeholder="Describe underlying macro triggers, customer volume changes, supply chain dynamics...",
                    height=85
                )

            with b_col2:
                sc_color = st.color_picker("Visual Color Code", value="#E67E22")
                sc_prob = st.slider(
                    "Default Probability Weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=20.0,
                    step=5.0,
                    help="Relative probability likelihood for blended forecast weighting."
                ) / 100.0

            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            with p_col1:
                sc_rev_g = st.number_input(
                    "Annual Revenue Growth (%)",
                    min_value=-50.0,
                    max_value=100.0,
                    value=-5.0,
                    step=1.0,
                    help="Topline revenue shift compared to historical TTM."
                ) / 100.0

            with p_col2:
                sc_cogs_i = st.number_input(
                    "COGS / Raw Material Inflation (%)",
                    min_value=-20.0,
                    max_value=50.0,
                    value=8.0,
                    step=1.0,
                    help="Direct procurement and freight cost escalation."
                ) / 100.0

            with p_col3:
                sc_opex_i = st.number_input(
                    "OPEX Inflation (%)",
                    min_value=-20.0,
                    max_value=50.0,
                    value=6.0,
                    step=1.0,
                    help="Overheads, employee compensation, and admin cost inflation."
                ) / 100.0

            with p_col4:
                sc_macro_s = st.number_input(
                    "Macro Capital Rate Shock (Multiplier)",
                    min_value=0.5,
                    max_value=2.5,
                    value=1.15,
                    step=0.05,
                    help="Multiplier on financing interest and benchmark borrowing spreads (1.0 = neutral)."
                )

            save_to_library = st.checkbox("Also save to permanent scenario library in SQLite database", value=True)
            submit_scenario = st.form_submit_button("🚀 Add to Active Scenarios Queue", use_container_width=True)

            if submit_scenario:
                if not sc_name.strip():
                    st.error("Please provide a name for your custom scenario.")
                else:
                    new_sc = Scenario(
                        name=sc_name.strip(),
                        rev_growth=sc_rev_g,
                        cogs_inflation=sc_cogs_i,
                        opex_inflation=sc_opex_i,
                        macro_shock=sc_macro_s,
                        color=sc_color,
                        description=sc_desc.strip(),
                        probability_weight=sc_prob,
                    )

                    # Add to session
                    st.session_state["active_scenarios_list"].append(new_sc)

                    if save_to_library:
                        save_custom_scenario(
                            user_id=user_id,
                            name=sc_name.strip(),
                            rev_growth=sc_rev_g,
                            cogs_inflation=sc_cogs_i,
                            opex_inflation=sc_opex_i,
                            macro_shock=sc_macro_s,
                            color=sc_color,
                            description=sc_desc.strip(),
                            probability_weight=sc_prob,
                        )

                    st.success(f"Custom scenario '{sc_name}' added to active simulation queue!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: SAVED SCENARIO LIBRARY
    # -------------------------------------------------------------------------
    with tab_library:
        st.markdown("### Saved Scenario Library")
        st.markdown(
            "<p style='color: var(--text-dim); font-size: 0.9rem; margin-top: -6px; margin-bottom: 20px;'>"
            "Repository of enterprise scenarios stored in the local SQLite database."
            "</p>",
            unsafe_allow_html=True
        )

        saved_scenarios = get_custom_scenarios(user_id=user_id)

        if not saved_scenarios:
            st.info("No custom scenarios saved to the library yet. Author one in the previous tab!")
        else:
            for sc_record in saved_scenarios:
                with st.expander(f"📁 {sc_record['name']} (Created: {sc_record['created_at']})", expanded=False):
                    l_col1, l_col2 = st.columns([3, 1])
                    with l_col1:
                        st.markdown(f"**Narrative:** {sc_record['description'] or 'No description provided.'}")
                        st.markdown(
                            f"- **Revenue Growth:** `{sc_record['rev_growth']*100:+.1f}%`\n"
                            f"- **COGS Inflation:** `{sc_record['cogs_inflation']*100:+.1f}%`\n"
                            f"- **OPEX Inflation:** `{sc_record['opex_inflation']*100:+.1f}%`\n"
                            f"- **Macro Shock:** `{sc_record['macro_shock']:.2f}x`\n"
                            f"- **Default Weight:** `{sc_record['probability_weight']*100:.0f}%`"
                        )
                    with l_col2:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        if st.button("➕ Load into Active Queue", key=f"load_lib_sc_{sc_record['id']}", use_container_width=True):
                            existing_names = [s.name for s in st.session_state["active_scenarios_list"]]
                            if sc_record["name"] in existing_names:
                                st.warning("Scenario is already in your active queue.")
                            else:
                                st.session_state["active_scenarios_list"].append(
                                    Scenario(
                                        name=sc_record["name"],
                                        rev_growth=sc_record["rev_growth"],
                                        cogs_inflation=sc_record["cogs_inflation"],
                                        opex_inflation=sc_record["opex_inflation"],
                                        macro_shock=sc_record["macro_shock"],
                                        color=sc_record["color"],
                                        description=sc_record["description"],
                                        probability_weight=sc_record["probability_weight"],
                                    )
                                )
                                st.success(f"Loaded '{sc_record['name']}' into active queue!")
                                st.rerun()

                        if st.button("🗑️ Delete from Library", key=f"del_lib_sc_{sc_record['id']}", use_container_width=True):
                            delete_custom_scenario(sc_record["id"])
                            st.success(f"Deleted scenario from library.")
                            st.rerun()
