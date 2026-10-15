"""
Scenario History View for Arctus.
Enables finance teams to review, reload, compare, and delete past stress-testing runs
persisted in the SQLite database.
"""

import streamlit as st
import pandas as pd
from core.database import get_scenario_runs, delete_scenario_run, get_scenario_run_by_id
from core.models import FinancialStatement
from core.theme import (
    format_inr,
    ACCENT_GOLD,
    SURFACE_CARD,
    BORDER_COLOR,
    BORDER_COLOR_GOLD,
    COLOR_GROWTH,
    COLOR_RECESSION,
)
from components.metrics import render_metric_card


def render_history_page(on_navigate, user_unit: str = "crores"):
    """
    Renders saved scenario history timeline and past execution details.
    """
    user = st.session_state.get("user")
    user_id = user.id if user else None

    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; margin-bottom: 4px;">
                Scenario Stress-Test History
            </h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">
                Review, audit, and reload past Monte Carlo simulation runs for your enterprise.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    runs = get_scenario_runs(user_id=user_id)

    if not runs:
        st.markdown(
            f"""
            <div style="
                background: {SURFACE_CARD}; border: 1px dashed {BORDER_COLOR}; border-radius: 12px;
                padding: 48px 24px; text-align: center; margin: 40px 0;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">📋</div>
                <h3 style="margin-bottom: 8px;">No Saved Scenario Runs Yet</h3>
                <p style="color: rgba(255,255,255,0.6); max-width: 500px; margin: 0 auto 24px auto;">
                    Execute a Monte Carlo simulation in the Main Dashboard and click "Save Run to Scenario History" to track audit versions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Go to Main Dashboard →", type="primary"):
            on_navigate("dashboard")
        return

    st.markdown(f"**Total Saved Runs:** {len(runs)}")

    for run in runs:
        run_id = run["id"]
        run_name = run["run_name"]
        ts = run["timestamp"]
        summary = run["summary"]

        base_sum = summary.get("Base", {})
        rec_sum = summary.get("Recession", {})

        rev_val = base_sum.get("annual_revenue", 0.0)
        ebitda_val = base_sum.get("annual_ebitda", 0.0)
        loss_p = rec_sum.get("loss_probability", 0.0)

        with st.container():
            st.markdown(
                f"""
                <div style="
                    background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 12px;
                    padding: 20px 24px; margin-bottom: 16px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">
                                {run_name}
                            </span>
                            <span style="font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-left: 12px;">
                                {ts} &nbsp;|&nbsp; Run #{run_id}
                            </span>
                        </div>
                        <span style="
                            background: rgba(252, 163, 17, 0.12); color: {ACCENT_GOLD};
                            border: 1px solid {BORDER_COLOR_GOLD}; padding: 3px 10px; border-radius: 6px;
                            font-size: 0.75rem; font-weight: 600;
                        ">{run['company_name']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Summary Metrics for this run
            c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
            with c1:
                render_metric_card("Base Revenue", format_inr(rev_val, unit=user_unit), "4-Quarter Forecast")
            with c2:
                render_metric_card("Base EBITDA", format_inr(ebitda_val, unit=user_unit), f"Margin: {(ebitda_val/rev_val*100 if rev_val else 0):.1f}%")
            with c3:
                badge_type = "growth" if loss_p < 5 else ("base" if loss_p < 20 else "recession")
                render_metric_card("Recession VaR", format_inr(rec_sum.get("p10_ebitda", 0.0), unit=user_unit), f"Loss Risk: {loss_p:.1f}%", badge=f"{loss_p:.1f}% Risk", badge_type=badge_type)
            with c4:
                st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                if st.button(f"Load Run #{run_id} into Workspace", key=f"load_run_{run_id}", use_container_width=True):
                    # Restore financial statement and redirect
                    raw_actuals = run["actuals"]
                    stmt = FinancialStatement.from_dict(raw_actuals)
                    st.session_state["current_statement"] = stmt
                    st.session_state["statement_source"] = f"Loaded from History: {run_name}"
                    st.session_state["forecast_results"] = None
                    st.success(f"Loaded {run_name} into Main Dashboard!")
                    on_navigate("dashboard")

                if st.button("Delete", key=f"del_run_{run_id}", use_container_width=True):
                    delete_scenario_run(run_id)
                    st.rerun()

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
