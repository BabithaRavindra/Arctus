"""
Unit and Integration Tests for Executive Cockpit & Capital Structure Module.
Verifies cash runway, debt amortization schedules, Indian banking covenant metrics,
sensitivity shock shifts, and Plotly chart generation.
"""

import pytest
import numpy as np
from core.synthetic import generate_clean_midmarket_statement
from core.cockpit import (
    calculate_cockpit_metrics,
    generate_executive_commentary,
    get_default_capital_structure_for_statement,
    CockpitMetrics,
    CapitalStructure,
    DebtInstrument,
)
from components.charts import (
    create_liquidity_runway_chart,
    create_debt_maturity_chart,
    create_covenant_headroom_chart,
    create_cash_driver_waterfall,
)


@pytest.fixture
def sample_statement():
    """Generates standard clean mid-market statement for tests."""
    return generate_clean_midmarket_statement()


def test_cockpit_baseline_metrics(sample_statement):
    """Verify baseline calculation of liquidity, EBITDA run-rate, and leverage."""
    metrics = calculate_cockpit_metrics(sample_statement, company_name="Apex Precision")
    
    assert metrics.company_name == "Apex Precision"
    assert metrics.annualized_revenue > 0
    assert metrics.annualized_ebitda > 0
    assert metrics.ebitda_margin_pct > 0
    assert metrics.gross_margin_pct > metrics.ebitda_margin_pct
    
    # Liquidity & Runway checks
    assert metrics.total_liquidity > 0
    assert metrics.cash_runway_months > 0
    assert metrics.runway_status in ["healthy", "adequate", "tight"]
    
    # Debt & Leverage
    assert metrics.gross_debt > 0
    assert metrics.net_debt <= metrics.gross_debt
    assert metrics.net_debt_to_ebitda > 0
    assert metrics.annual_finance_cost > 0
    assert metrics.annual_principal_repayment > 0
    assert metrics.blended_interest_rate_pct > 5.0  # realistic Indian commercial borrowing rate


def test_banking_covenant_evaluation(sample_statement):
    """Verify all 5 consortium banking covenants evaluate thresholds and headroom."""
    metrics = calculate_cockpit_metrics(sample_statement)
    covs = metrics.covenants
    
    assert len(covs) == 5
    assert "icr" in covs
    assert "dscr" in covs
    assert "nd_ebitda" in covs
    assert "current_ratio" in covs
    assert "tol_tnw" in covs
    
    # ICR (Interest Coverage Ratio)
    icr = covs["icr"]
    assert icr.threshold == 2.00
    assert icr.actual_value > 0
    assert icr.headroom == pytest.approx(icr.actual_value - 2.00, 0.01)
    assert icr.status in ["compliant", "warning", "breached"]
    
    # DSCR (Debt Service Coverage Ratio)
    dscr = covs["dscr"]
    assert dscr.threshold == 1.25
    assert dscr.actual_value > 0
    assert dscr.status in ["compliant", "warning", "breached"]
    
    # Net Debt / EBITDA (Ceiling covenant)
    nd = covs["nd_ebitda"]
    assert nd.threshold == 3.00
    assert nd.comparison == "lte"
    assert nd.headroom == pytest.approx(3.00 - nd.actual_value, 0.01)


def test_what_if_sensitivity_repo_rate_shock(sample_statement):
    """Verify that a positive repo rate shock increases finance costs and dampens ICR."""
    base_metrics = calculate_cockpit_metrics(sample_statement, repo_rate_shock_bps=0.0)
    shock_metrics = calculate_cockpit_metrics(sample_statement, repo_rate_shock_bps=100.0)  # +100 bps
    
    assert shock_metrics.applied_repo_shock_bps == 100.0
    assert shock_metrics.annual_finance_cost > base_metrics.annual_finance_cost
    assert shock_metrics.covenants["icr"].actual_value < base_metrics.covenants["icr"].actual_value


def test_what_if_sensitivity_inflation_and_demand_shocks(sample_statement):
    """Verify COGS inflation and revenue drop reduce EBITDA and shorten runway."""
    base_metrics = calculate_cockpit_metrics(
        sample_statement,
        cogs_inflation_pct=0.0,
        revenue_shock_pct=0.0
    )
    stress_metrics = calculate_cockpit_metrics(
        sample_statement,
        cogs_inflation_pct=8.0,     # +8% raw material inflation
        revenue_shock_pct=-15.0     # -15% demand drop
    )
    
    assert stress_metrics.annualized_revenue < base_metrics.annualized_revenue
    assert stress_metrics.annualized_ebitda < base_metrics.annualized_ebitda
    assert stress_metrics.ebitda_variance_from_shocks < 0


def test_monthly_liquidity_trajectory(sample_statement):
    """Verify 12-month forward liquidity trajectory structure."""
    metrics = calculate_cockpit_metrics(sample_statement)
    trajectory = metrics.monthly_liquidity_trajectory
    
    assert len(trajectory) == 12
    for m_idx, m_data in enumerate(trajectory):
        assert m_data["month_index"] == m_idx + 1
        assert m_data["month_label"] == f"M+{m_idx + 1}"
        assert m_data["liquidity_balance"] >= 0
        assert m_data["minimum_buffer"] > 0
        assert isinstance(m_data["is_above_buffer"], bool)


def test_cockpit_plotly_chart_builders(sample_statement):
    """Verify all 4 dedicated executive Plotly charts build cleanly."""
    metrics = calculate_cockpit_metrics(sample_statement)
    
    fig_liq = create_liquidity_runway_chart(metrics.monthly_liquidity_trajectory, unit="crores")
    assert fig_liq is not None
    assert len(fig_liq.data) == 2  # Buffer line + Liquidity line
    
    fig_debt = create_debt_maturity_chart(metrics.debt_maturity_schedule, unit="crores")
    assert fig_debt is not None
    assert len(fig_debt.data) == 2  # Principal + Amortization
    
    fig_cov = create_covenant_headroom_chart(metrics.covenants)
    assert fig_cov is not None
    assert len(fig_cov.data) == 2  # Actual Bar + Benchmark Marker
    
    fig_waterfall = create_cash_driver_waterfall(metrics, unit="crores")
    assert fig_waterfall is not None
    assert len(fig_waterfall.data) == 1


def test_executive_commentary_generation(sample_statement):
    """Verify executive commentary synthesis contains key metrics and company name."""
    metrics = calculate_cockpit_metrics(sample_statement, company_name="Apex Precision Automotives")
    commentary = generate_executive_commentary(metrics)
    
    assert "Apex Precision Automotives" in commentary
    assert "EBITDA" in commentary
    assert "Interest Coverage Ratio (ICR)" in commentary
    assert "covenant" in commentary.lower()
