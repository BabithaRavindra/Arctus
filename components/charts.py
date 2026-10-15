"""
Plotly Chart Builders for Arctus.
CFO-grade interactive financial visualizers strictly adhering to the "Black & Gold Elegance"
design system. All charts reuse the centralized template and palette from core.theme.
"""

from typing import Dict, List, Any, Optional
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core.models import FinancialStatement, Scenario, ForecastResult
from core.theme import (
    BG_BASE,
    SURFACE_CARD,
    ACCENT_GOLD,
    TEXT_PRIMARY,
    TEXT_MUTED,
    BORDER_COLOR,
    COLOR_GROWTH,
    COLOR_BASE,
    COLOR_RECESSION,
    format_inr,
)


def create_scenario_comparison_chart(
    results: Dict[str, ForecastResult],
    metric: str = "ebitda",
    unit: str = "auto"
) -> go.Figure:
    """
    Side-by-side comparison of projected quarterly trajectory across all active scenarios.
    """
    fig = go.Figure()

    metric_title = "Operating EBITDA" if metric == "ebitda" else "Total Revenue"
    color_map = {
        "Recession": COLOR_RECESSION,
        "Base": COLOR_BASE,
        "Growth": COLOR_GROWTH,
    }

    # Grouped quarterly bar or line traces
    for sc_name, res in results.items():
        vals = res.point_forecast[metric]
        color = color_map.get(sc_name, res.scenario.color)
        fwd_periods = res.forecast_periods

        fig.add_trace(go.Bar(
            name=f"{sc_name} Scenario",
            x=fwd_periods,
            y=vals,
            marker_color=color,
            marker_line=dict(width=1, color="rgba(255,255,255,0.15)"),
            hovertemplate=f"<b>{sc_name}</b><br>Period: %{{x}}<br>{metric_title}: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        title=f"Quarterly {metric_title} Projections Across Scenarios",
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        yaxis_title=f"{metric_title} ({unit.capitalize() if unit != 'auto' else 'INR'})",
        xaxis_title="Forecast Period",
        template="arctus_black_gold",
        height=380,
    )
    return fig


def create_waterfall_bridge_chart(
    stmt: FinancialStatement,
    result: ForecastResult,
    unit: str = "auto"
) -> go.Figure:
    """
    EBITDA waterfall bridge from last actual historical quarter to the 4-quarter forward projected average,
    decomposing Revenue Growth, COGS Inflation, OPEX Shift, and Macro Shock.
    """
    hist_ebitda = float(stmt.ebitda[-1])
    fwd_ebitda_avg = float(np.mean(result.point_forecast["ebitda"]))

    # Decompose driver variances
    # Revenue driver impact
    hist_rev = float(stmt.revenue[-1])
    fwd_rev_avg = float(np.mean(result.point_forecast["revenue"]))
    hist_gp_margin = float(stmt.gross_profit[-1] / hist_rev) if hist_rev > 0 else 0.40
    rev_growth_driver = (fwd_rev_avg - hist_rev) * hist_gp_margin

    # COGS inflation impact
    hist_cogs = float(stmt.cogs[-1])
    fwd_cogs_avg = float(np.mean(result.point_forecast["cogs"]))
    cogs_inflation_driver = -(fwd_cogs_avg - (fwd_rev_avg * (hist_cogs / hist_rev))) if hist_rev > 0 else 0.0

    # OPEX driver impact
    hist_opex = float(stmt.opex[-1])
    fwd_opex_avg = float(np.mean(result.point_forecast["opex"]))
    opex_driver = -(fwd_opex_avg - hist_opex)

    # Residual / Macro Shock driver
    accounted = hist_ebitda + rev_growth_driver + cogs_inflation_driver + opex_driver
    macro_driver = fwd_ebitda_avg - accounted

    x_labels = [
        f"Actuals ({stmt.periods[-1]})",
        "Volume & Revenue Growth",
        "COGS Inflation",
        "OPEX Adjustments",
        "Macro Shock & Overheads",
        f"Forecast Run-Rate ({result.scenario.name})",
    ]

    measures = ["absolute", "relative", "relative", "relative", "relative", "total"]
    y_values = [
        hist_ebitda,
        rev_growth_driver,
        cogs_inflation_driver,
        opex_driver,
        macro_driver,
        fwd_ebitda_avg,
    ]

    fig = go.Figure(go.Waterfall(
        name="EBITDA Bridge",
        orientation="v",
        measure=measures,
        x=x_labels,
        textposition="outside",
        text=[format_inr(y, unit=unit) for y in y_values],
        y=y_values,
        connector={"line": {"color": "rgba(229, 229, 229, 0.25)", "dash": "dot"}},
        decreasing={"marker": {"color": COLOR_RECESSION}},
        increasing={"marker": {"color": COLOR_GROWTH}},
        totals={"marker": {"color": ACCENT_GOLD}},
        hovertemplate="<b>%{x}</b><br>Impact: %{y}<extra></extra>",
    ))

    fig.update_layout(
        title=f"EBITDA Waterfall Bridge — Actuals to {result.scenario.name} Forecast",
        showlegend=False,
        template="arctus_black_gold",
        height=400,
    )
    return fig


def create_confidence_band_chart(
    stmt: FinancialStatement,
    result: ForecastResult,
    metric: str = "ebitda",
    unit: str = "auto"
) -> go.Figure:
    """
    Monte Carlo fan chart showing historical actual trajectory connecting into
    median forecast trajectory, with 10%–90% shaded probability envelope.
    """
    fig = go.Figure()

    # 1. Historical Actuals Line
    hist_periods = stmt.periods
    hist_vals = getattr(stmt, metric)

    fig.add_trace(go.Scatter(
        name="Historical Actuals",
        x=hist_periods,
        y=hist_vals,
        mode="lines+markers",
        line=dict(color="#FFFFFF", width=2.5),
        marker=dict(size=6, color="#FFFFFF"),
        hovertemplate="<b>Actuals</b><br>Period: %{x}<br>Value: %{y}<extra></extra>",
    ))

    # Connect bridge point from last historical to first forward quarter
    bridge_period = [hist_periods[-1]] + result.forecast_periods
    bridge_median = [hist_vals[-1]] + list(result.confidence_bands[metric]["median"])
    bridge_p10 = [hist_vals[-1]] + list(result.confidence_bands[metric]["p10"])
    bridge_p90 = [hist_vals[-1]] + list(result.confidence_bands[metric]["p90"])

    # 2. 90% Confidence Upper Bound
    fig.add_trace(go.Scatter(
        name="90th Percentile (Optimistic)",
        x=bridge_period,
        y=bridge_p90,
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ))

    # 3. 10% Confidence Lower Bound (Shaded fill)
    fig.add_trace(go.Scatter(
        name="10% - 90% Confidence Envelope",
        x=bridge_period,
        y=bridge_p10,
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(252, 163, 17, 0.14)",
        hovertemplate="10th - 90th CI<extra></extra>",
    ))

    # 4. Monte Carlo Median Line
    fig.add_trace(go.Scatter(
        name=f"{result.scenario.name} Median Forecast",
        x=bridge_period,
        y=bridge_median,
        mode="lines+markers",
        line=dict(color=ACCENT_GOLD, width=3, dash="solid"),
        marker=dict(size=7, color=ACCENT_GOLD),
        hovertemplate="<b>Forecast Median</b><br>Period: %{x}<br>Value: %{y}<extra></extra>",
    ))

    metric_name = "EBITDA" if metric == "ebitda" else "Revenue"
    fig.update_layout(
        title=f"Monte Carlo Probability Fan Chart ({result.scenario.name} Scenario, 1000 Iterations)",
        xaxis_title="Quarterly Timeline",
        yaxis_title=f"{metric_name} ({unit.capitalize() if unit != 'auto' else 'INR'})",
        template="arctus_black_gold",
        height=420,
    )
    return fig


def create_tornado_chart(
    tornado_sensitivities: List[Dict[str, Any]],
    unit: str = "auto"
) -> go.Figure:
    """
    Horizontal tornado sensitivity bar chart showing EBITDA swing for each macroeconomic lever.
    """
    fig = go.Figure()

    params = [item["parameter"] for item in tornado_sensitivities][::-1]
    downsides = [item["downside_impact"] for item in tornado_sensitivities][::-1]
    upsides = [item["upside_impact"] for item in tornado_sensitivities][::-1]

    # Downside bars (Muted Red)
    fig.add_trace(go.Bar(
        name="Downside (-10% shock)",
        y=params,
        x=downsides,
        orientation="h",
        marker_color=COLOR_RECESSION,
        marker_line=dict(width=1, color="rgba(255,255,255,0.1)"),
        hovertemplate="<b>%{y}</b><br>Downside Impact: %{x}<extra></extra>",
    ))

    # Upside bars (Muted Green / Gold)
    fig.add_trace(go.Bar(
        name="Upside (+10% shock)",
        y=params,
        x=upsides,
        orientation="h",
        marker_color=COLOR_GROWTH,
        marker_line=dict(width=1, color="rgba(255,255,255,0.1)"),
        hovertemplate="<b>%{y}</b><br>Upside Impact: %{x}<extra></extra>",
    ))

    fig.update_layout(
        title="Tornado Sensitivity Analysis — Impact on Cumulative Forward EBITDA",
        barmode="overlay",
        xaxis=dict(
            zeroline=True,
            zerolinecolor=ACCENT_GOLD,
            zerolinewidth=2,
            title=f"EBITDA Variance from Baseline ({unit.capitalize() if unit != 'auto' else 'INR'})",
        ),
        yaxis=dict(title=""),
        template="arctus_black_gold",
        height=320,
    )
    return fig


def create_liquidity_runway_chart(
    monthly_trajectory: List[Dict[str, Any]],
    unit: str = "crores"
) -> go.Figure:
    """
    Renders 12-month forward projected liquidity balance against minimum operational buffer.
    """
    fig = go.Figure()
    months = [item["month_label"] for item in monthly_trajectory]
    balances = [item["liquidity_balance"] for item in monthly_trajectory]
    min_buffers = [item["minimum_buffer"] for item in monthly_trajectory]

    # Minimum Buffer Floor Line (Red dashed line)
    fig.add_trace(go.Scatter(
        name="Minimum Operating Reserve (Buffer)",
        x=months,
        y=min_buffers,
        mode="lines",
        line=dict(color=COLOR_RECESSION, width=2, dash="dash"),
        hovertemplate="<b>Minimum Buffer</b><br>Month: %{x}<br>Level: %{y}<extra></extra>"
    ))

    # Cash Balance Line & Fill
    fig.add_trace(go.Scatter(
        name="Projected Available Liquidity",
        x=months,
        y=balances,
        mode="lines+markers",
        line=dict(color=ACCENT_GOLD, width=3),
        marker=dict(size=7, color=ACCENT_GOLD, line=dict(width=1, color="#FFFFFF")),
        fill="tonexty",
        fillcolor="rgba(180, 154, 90, 0.12)",
        hovertemplate="<b>Available Liquidity</b><br>Month: %{x}<br>Balance: %{y}<extra></extra>"
    ))

    latest_bal = balances[-1]
    unit_str = "₹ Cr" if unit == "crores" else ("₹ L" if unit == "lakhs" else "₹")

    fig.update_layout(
        title="12-Month Forward Liquidity Trajectory & Operating Buffer",
        xaxis=dict(title="Forward Month", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(
            title=f"Liquid Assets ({unit.capitalize()})",
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False
        ),
        template="arctus_black_gold",
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def create_debt_maturity_chart(
    debt_schedule: List[Dict[str, Any]],
    unit: str = "crores"
) -> go.Figure:
    """
    Visualizes debt capital structure breakdown and scheduled amortization maturities.
    """
    fig = go.Figure()

    facilities = [d["facility_name"] for d in debt_schedule]
    principals = [d["principal"] for d in debt_schedule]
    amortizations = [d["annual_amortization"] for d in debt_schedule]
    interest_rates = [f"{d['interest_rate_pct']:.2f}%" for d in debt_schedule]
    lenders = [d["lender"] for d in debt_schedule]
    maturities = [d["maturity_year"] for d in debt_schedule]

    # Principal Outstanding Bar
    fig.add_trace(go.Bar(
        name="Principal Outstanding",
        x=facilities,
        y=principals,
        marker_color=ACCENT_GOLD,
        marker_line=dict(width=1, color="rgba(255,255,255,0.15)"),
        customdata=list(zip(lenders, interest_rates, maturities)),
        hovertemplate="<b>%{x}</b><br>Lender: %{customdata[0]}<br>Rate: %{customdata[1]}<br>Maturity: %{customdata[2]}<br>Principal: %{y}<extra></extra>"
    ))

    # Annual Amortization Bar
    fig.add_trace(go.Bar(
        name="Annual Debt Service (Amortization)",
        x=facilities,
        y=amortizations,
        marker_color=COLOR_GROWTH,
        marker_line=dict(width=1, color="rgba(255,255,255,0.15)"),
        hovertemplate="<b>%{x}</b><br>Annual Amortization: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="Debt Capital Structure & Annual Amortization by Facility",
        barmode="group",
        xaxis=dict(title="", tickangle=-12),
        yaxis=dict(title=f"Amount ({unit.capitalize()})", gridcolor="rgba(255,255,255,0.06)"),
        template="arctus_black_gold",
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_covenant_headroom_chart(
    covenants: Dict[str, Any]
) -> go.Figure:
    """
    Horizontal bar chart showing Actual Value vs Threshold for Indian banking covenants.
    """
    fig = go.Figure()

    names = []
    actuals = []
    thresholds = []
    colors = []
    hover_texts = []

    for key, cov in covenants.items():
        names.append(cov.name)
        actuals.append(cov.actual_value)
        thresholds.append(cov.threshold)

        color = COLOR_GROWTH if cov.status == "compliant" else (COLOR_BASE if cov.status == "warning" else COLOR_RECESSION)
        colors.append(color)

        hover_texts.append(
            f"<b>{cov.name}</b><br>Actual: {cov.actual_value:.2f}{cov.unit_label}<br>"
            f"Sanction Limit: {cov.threshold:.2f}{cov.unit_label}<br>"
            f"Headroom Cushion: {cov.cushion_pct:+.1f}%<br>"
            f"Status: {cov.status.upper()}"
        )

    # Actual Ratio Bar
    fig.add_trace(go.Bar(
        name="Actual Level",
        y=names[::-1],
        x=actuals[::-1],
        orientation="h",
        marker_color=colors[::-1],
        marker_line=dict(width=1, color="rgba(255,255,255,0.2)"),
        hoverinfo="text",
        text=hover_texts[::-1],
    ))

    # Bank Sanction Threshold Marker
    fig.add_trace(go.Scatter(
        name="Bank Sanction Benchmark Limit",
        y=names[::-1],
        x=thresholds[::-1],
        mode="markers",
        marker=dict(size=14, color="#FFFFFF", symbol="line-ns-open", line=dict(width=3, color="#FFFFFF")),
        hoverinfo="text",
        hovertext=[f"Threshold: {t:.2f}" for t in thresholds[::-1]]
    ))

    fig.update_layout(
        title="Consortium Bank Covenant Health & Headroom Cushion",
        xaxis=dict(title="Multiple / Ratio Level", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title=""),
        template="arctus_black_gold",
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_cash_driver_waterfall(
    metrics: Any,
    unit: str = "crores"
) -> go.Figure:
    """
    Waterfalls Annualized Revenue -> Operating Costs -> Debt Service -> Net Free Cash Flow.
    """
    rev = metrics.annualized_revenue
    ebitda = metrics.annualized_ebitda
    cogs_and_opex = rev - ebitda
    fin_cost = metrics.annual_finance_cost
    amort = metrics.annual_principal_repayment
    net_fcf = ebitda - fin_cost - amort

    fig = go.Figure(go.Waterfall(
        name="Cash Flow Conversion",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "relative", "total"],
        x=["Annualized Revenue", "COGS & Operating Expenses", "Operating EBITDA", "Annual Finance Costs", "Debt Principal Amortization", "Net Free Cash Flow"],
        textposition="outside",
        y=[rev, -cogs_and_opex, None, -fin_cost, -amort, None],
        connector={"line": {"color": "rgba(255,255,255,0.2)"}},
        decreasing={"marker": {"color": COLOR_RECESSION}},
        increasing={"marker": {"color": COLOR_GROWTH}},
        totals={"marker": {"color": ACCENT_GOLD}}
    ))

    fig.update_layout(
        title="Enterprise Cash Conversion Waterfall (Annualized Run-Rate)",
        yaxis=dict(title=f"Amount ({unit.capitalize()})", gridcolor="rgba(255,255,255,0.06)"),
        template="arctus_black_gold",
        height=360,
    )
    return fig


def create_scenario_probability_pie_chart(
    scenarios: List[Scenario]
) -> go.Figure:
    """
    Renders a donut chart displaying scenario probability weights.
    """
    names = [s.name for s in scenarios]
    weights = [s.probability_weight * 100.0 for s in scenarios]
    colors = [s.color for s in scenarios]

    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=weights,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=SURFACE_CARD, width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Probability: %{value:.1f}%<extra></extra>",
    )])

    fig.update_layout(
        title="Scenario Probability Allocation",
        template="arctus_black_gold",
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
    )
    return fig


def create_covenant_trajectory_chart(
    evaluations: List[Any],
    covenant_name: str,
    threshold: float,
    comparison: str = "gte",
    unit_label: str = "x"
) -> go.Figure:
    """
    Plots the quarterly actual/projected ratio trajectory alongside the bank sanction threshold
    and Monte Carlo confidence dispersion.
    """
    quarters = [e.quarter for e in evaluations]
    actual_vals = [e.actual_value for e in evaluations]

    fig = go.Figure()

    # Threshold horizontal reference line
    threshold_vals = [threshold] * len(quarters)
    fig.add_trace(go.Scatter(
        name=f"Bank Sanction Benchmark ({threshold:.2f}{unit_label})",
        x=quarters,
        y=threshold_vals,
        mode="lines",
        line=dict(color=COLOR_RECESSION, width=2, dash="dash"),
        hoverinfo="text",
        hovertext=[f"Bank Limit: {threshold:.2f}{unit_label}"] * len(quarters)
    ))

    # Actual projected line
    fig.add_trace(go.Scatter(
        name=f"Projected {covenant_name}",
        x=quarters,
        y=actual_vals,
        mode="lines+markers",
        line=dict(color=ACCENT_GOLD, width=3),
        marker=dict(size=8, color=ACCENT_GOLD),
        hovertemplate="<b>%{x}</b><br>Level: %{y:.2f}" + unit_label + "<extra></extra>"
    ))

    fig.update_layout(
        title=f"{covenant_name} — 4-Quarter Trajectory vs Sanction Limit",
        xaxis=dict(title="Quarter", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title=f"Multiple ({unit_label})", gridcolor="rgba(255,255,255,0.06)"),
        template="arctus_black_gold",
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_covenant_breach_probability_chart(
    analyses: Dict[str, Any]
) -> go.Figure:
    """
    Bar chart showing Monte Carlo estimated probability of breaching bank sanction threshold
    across Indian consortium covenants.
    """
    names = [a.name for a in analyses.values()]
    probs = [a.max_breach_probability for a in analyses.values()]
    colors = [
        COLOR_RECESSION if p >= 25.0 else (COLOR_BASE if p >= 10.0 else COLOR_GROWTH)
        for p in probs
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names,
        y=probs,
        marker_color=colors,
        marker_line=dict(width=1, color="rgba(255,255,255,0.15)"),
        text=[f"{p:.1f}%" for p in probs],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Breach Probability: %{y:.1f}%<extra></extra>"
    ))

    fig.update_layout(
        title="Probabilistic Covenant Breach Risk Matrix (% Risk of Bank Breach)",
        yaxis=dict(title="Probability (%)", range=[0, max(45.0, max(probs) + 10.0) if probs else 50.0], gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(title=""),
        template="arctus_black_gold",
        height=340,
    )
    return fig


