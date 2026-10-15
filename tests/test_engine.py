"""
Unit tests for ForecastEngine.
Tests 4-quarter forward projections, Monte Carlo simulation shape and statistics,
reproducibility with seed, confidence interval bounds, and tornado sensitivity analysis.
"""

import pytest
import numpy as np
from core.models import FinancialStatement, Scenario
from core.engine import ForecastEngine
from core.synthetic import generate_clean_midmarket_statement


def test_forecast_engine_forward_periods():
    """Verify generation of next 4 chronological quarter labels."""
    fwd = ForecastEngine.generate_forward_periods("Q4 FY24", num_quarters=4)
    assert fwd == ["Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"]

    fwd2 = ForecastEngine.generate_forward_periods("Q2 FY24", num_quarters=3)
    assert fwd2 == ["Q3 FY24", "Q4 FY24", "Q1 FY25"]


def test_monte_carlo_shapes_and_statistics():
    """Verify Monte Carlo produces (1000, 4) iterations and monotonic confidence bounds."""
    stmt = generate_clean_midmarket_statement(num_quarters=4)
    scenarios = [
        Scenario("Base", rev_growth=0.08, cogs_inflation=0.045, opex_inflation=0.05, macro_shock=1.0),
        Scenario("Recession", rev_growth=-0.06, cogs_inflation=0.08, opex_inflation=0.07, macro_shock=1.2),
    ]

    engine = ForecastEngine(random_seed=42)
    results = engine.run_forecast(stmt, scenarios, iterations=1000, num_quarters=4)

    assert "Base" in results
    assert "Recession" in results

    base_res = results["Base"]
    assert base_res.forecast_periods == ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"]

    # Check matrix shape
    mc_ebitda = base_res.monte_carlo_runs["ebitda"]
    assert mc_ebitda.shape == (1000, 4)

    # Check statistical order: p10 <= p25 <= median <= p75 <= p90
    bands = base_res.confidence_bands["ebitda"]
    p10 = bands["p10"]
    p25 = bands["p25"]
    med = bands["median"]
    p75 = bands["p75"]
    p90 = bands["p90"]

    for q in range(4):
        assert p10[q] <= p25[q] <= med[q] <= p75[q] <= p90[q]

    # Recession should have lower median EBITDA than Base
    rec_res = results["Recession"]
    assert np.sum(rec_res.confidence_bands["ebitda"]["median"]) < np.sum(base_res.confidence_bands["ebitda"]["median"])


def test_reproducibility_with_seed():
    """Verify deterministic output when random seed is fixed."""
    stmt = generate_clean_midmarket_statement(num_quarters=4)
    sc = [Scenario("Base", rev_growth=0.08, cogs_inflation=0.045, opex_inflation=0.05)]

    engine1 = ForecastEngine(random_seed=1234)
    res1 = engine1.run_forecast(stmt, sc, iterations=500)

    engine2 = ForecastEngine(random_seed=1234)
    res2 = engine2.run_forecast(stmt, sc, iterations=500)

    np.testing.assert_array_almost_equal(
        res1["Base"].confidence_bands["ebitda"]["median"],
        res2["Base"].confidence_bands["ebitda"]["median"]
    )


def test_tornado_sensitivity_ranking():
    """Verify that tornado sensitivity analysis calculates and sorts parameter impacts."""
    stmt = generate_clean_midmarket_statement(num_quarters=4)
    sc = Scenario("Base", rev_growth=0.10, cogs_inflation=0.05, opex_inflation=0.05, macro_shock=1.0)

    engine = ForecastEngine(random_seed=42)
    tornado = engine.compute_sensitivity_analysis(stmt, sc, delta_pct=0.10)

    assert len(tornado) == 4
    # Should be sorted in descending order of swing
    for i in range(len(tornado) - 1):
        assert tornado[i]["swing"] >= tornado[i + 1]["swing"]
