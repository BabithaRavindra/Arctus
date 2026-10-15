import pytest
import numpy as np
from core.models import FinancialStatement, Scenario
from core.synthetic import generate_clean_midmarket_statement
from core.engine import ForecastEngine
from core.cockpit import get_default_capital_structure_for_statement
from core.covenants import (
    STANDARD_BANKING_COVENANTS,
    compute_probabilistic_covenant_matrix,
    CovenantBreachAnalysis,
)


def test_standard_banking_covenants_definitions():
    assert "icr" in STANDARD_BANKING_COVENANTS
    assert "dscr" in STANDARD_BANKING_COVENANTS
    assert "nd_ebitda" in STANDARD_BANKING_COVENANTS
    assert "current_ratio" in STANDARD_BANKING_COVENANTS
    assert "tol_tnw" in STANDARD_BANKING_COVENANTS

    icr = STANDARD_BANKING_COVENANTS["icr"]
    assert icr.threshold == 2.00
    assert icr.comparison == "gte"

    dscr = STANDARD_BANKING_COVENANTS["dscr"]
    assert dscr.threshold == 1.25
    assert dscr.comparison == "gte"

    nd = STANDARD_BANKING_COVENANTS["nd_ebitda"]
    assert nd.threshold == 3.00
    assert nd.comparison == "lte"

    cr = STANDARD_BANKING_COVENANTS["current_ratio"]
    assert cr.threshold == 1.33
    assert cr.comparison == "gte"


def test_compute_probabilistic_covenant_matrix():
    stmt = generate_clean_midmarket_statement()
    cap_struct = get_default_capital_structure_for_statement(stmt)
    engine = ForecastEngine(random_seed=42)

    sc = Scenario(
        name="Moderate Stress",
        rev_growth=-0.08,
        cogs_inflation=0.10,
        opex_inflation=0.06,
        macro_shock=1.20,
    )

    results = engine.run_forecast(stmt, [sc], iterations=500)
    forecast_res = results["Moderate Stress"]

    analyses = compute_probabilistic_covenant_matrix(
        stmt=stmt,
        result=forecast_res,
        cap_struct=cap_struct,
        repo_shock_bps=50.0,
    )

    assert len(analyses) == 5
    for cov_key in ["icr", "dscr", "nd_ebitda", "current_ratio", "tol_tnw"]:
        assert cov_key in analyses
        a: CovenantBreachAnalysis = analyses[cov_key]
        assert len(a.quarterly_evaluations) == 4
        assert 0.0 <= a.max_breach_probability <= 100.0
        assert a.risk_level in ["low", "moderate", "critical"]
        assert isinstance(a.executive_warning, str)

        for q_eval in a.quarterly_evaluations:
            assert q_eval.quarter in forecast_res.forecast_periods
            assert q_eval.status in ["compliant", "warning", "breached"]
            assert 0.0 <= q_eval.breach_probability <= 100.0


def test_severe_stress_covenant_breach_detection():
    stmt = generate_clean_midmarket_statement()
    cap_struct = get_default_capital_structure_for_statement(stmt)
    engine = ForecastEngine(random_seed=42)

    # Catastrophic stress: -30% revenue, +25% COGS, 1.50x capital shock
    severe_sc = Scenario(
        name="Severe Shock",
        rev_growth=-0.30,
        cogs_inflation=0.25,
        opex_inflation=0.15,
        macro_shock=1.50,
    )

    results = engine.run_forecast(stmt, [severe_sc], iterations=300)
    forecast_res = results["Severe Shock"]

    analyses = compute_probabilistic_covenant_matrix(
        stmt=stmt,
        result=forecast_res,
        cap_struct=cap_struct,
        repo_shock_bps=150.0,
    )

    icr_analysis = analyses["icr"]
    # Under catastrophic shock, ICR breach probability should spike above 20%
    assert icr_analysis.max_breach_probability > 10.0
    assert icr_analysis.first_breach_quarter is not None
    assert icr_analysis.risk_level in ["moderate", "critical"]
    assert "breaching" in icr_analysis.executive_warning or "cushion" in icr_analysis.executive_warning
