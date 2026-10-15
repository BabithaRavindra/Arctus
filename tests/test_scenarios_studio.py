import pytest
import numpy as np
from core.models import FinancialStatement, Scenario, ForecastResult
from core.synthetic import generate_clean_midmarket_statement
from core.engine import ForecastEngine
from core.database import (
    save_custom_scenario,
    get_custom_scenarios,
    delete_custom_scenario,
)

def test_custom_scenario_creation_and_database_crud():
    stmt = generate_clean_midmarket_statement()
    
    # Save a custom scenario
    sc_id = save_custom_scenario(
        user_id=1,
        name="Test Red Sea Freight Shock",
        rev_growth=-0.08,
        cogs_inflation=0.18,
        opex_inflation=0.07,
        macro_shock=1.20,
        color="#E67E22",
        description="Container shipping rate escalation test",
        probability_weight=0.35,
        is_preset=False
    )
    assert sc_id > 0
    
    # Retrieve and verify
    scenarios = get_custom_scenarios(user_id=1)
    found = [s for s in scenarios if s["id"] == sc_id]
    assert len(found) == 1
    assert found[0]["name"] == "Test Red Sea Freight Shock"
    assert found[0]["rev_growth"] == -0.08
    assert found[0]["probability_weight"] == 0.35
    
    # Delete and verify
    assert delete_custom_scenario(sc_id) is True
    scenarios_after = get_custom_scenarios(user_id=1)
    assert not any(s["id"] == sc_id for s in scenarios_after)

def test_engine_probability_weighted_blended_forecast():
    stmt = generate_clean_midmarket_statement()
    engine = ForecastEngine(random_seed=42)
    
    scenarios = [
        Scenario("Stress Case", rev_growth=-0.10, cogs_inflation=0.15, opex_inflation=0.08, macro_shock=1.25, color="#B5545A", probability_weight=0.25),
        Scenario("Base Case", rev_growth=0.08, cogs_inflation=0.05, opex_inflation=0.05, macro_shock=1.00, color="#B49A5A", probability_weight=0.50),
        Scenario("Bull Case", rev_growth=0.20, cogs_inflation=0.03, opex_inflation=0.04, macro_shock=0.90, color="#7A9B76", probability_weight=0.25),
    ]
    
    # Run multi-scenario forecasts
    results = engine.run_forecast(stmt, scenarios, iterations=500)
    assert len(results) == 3
    
    # Compute blended expectation
    blended = engine.compute_blended_forecast(results)
    assert blended is not None
    assert blended.scenario.name == "Blended Probability Weighted"
    assert len(blended.forecast_periods) == 4
    
    # Blended point forecast EBITDA should lie strictly between the Stress and Bull cases
    stress_ebitda = float(np.sum(results["Stress Case"].point_forecast["ebitda"]))
    bull_ebitda = float(np.sum(results["Bull Case"].point_forecast["ebitda"]))
    blended_ebitda = float(np.sum(blended.point_forecast["ebitda"]))
    
    assert stress_ebitda < blended_ebitda < bull_ebitda
    assert 0.0 <= blended.loss_probability <= 100.0
    assert "ebitda" in blended.confidence_bands
    assert "p10" in blended.confidence_bands["ebitda"]
    assert "p90" in blended.confidence_bands["ebitda"]

def test_engine_blended_forecast_normalized_weights():
    stmt = generate_clean_midmarket_statement()
    engine = ForecastEngine(random_seed=42)
    
    sc1 = Scenario("S1", rev_growth=0.05, cogs_inflation=0.05, opex_inflation=0.05, probability_weight=50.0)
    sc2 = Scenario("S2", rev_growth=0.15, cogs_inflation=0.05, opex_inflation=0.05, probability_weight=50.0)
    
    results = engine.run_forecast(stmt, [sc1, sc2], iterations=100)
    # Custom non-normalized weights (e.g. 10 and 30 -> 25% and 75%)
    blended = engine.compute_blended_forecast(results, weights={"S1": 10.0, "S2": 30.0})
    
    assert blended is not None
    s1_rev = float(np.sum(results["S1"].point_forecast["revenue"]))
    s2_rev = float(np.sum(results["S2"].point_forecast["revenue"]))
    blended_rev = float(np.sum(blended.point_forecast["revenue"]))
    
    expected_rev = 0.25 * s1_rev + 0.75 * s2_rev
    assert pytest.approx(blended_rev, rel=1e-4) == expected_rev
