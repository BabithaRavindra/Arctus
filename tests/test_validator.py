"""
Unit tests for ValidationLayer.
Tests period continuity detection, linear missing-quarter interpolation,
and financial statement sanity rules.
"""

import pytest
import pandas as pd
import numpy as np
from core.validator import ValidationLayer, ValidationError


def test_period_continuity_detection():
    """Verify detection of missing quarters in timeline."""
    # Continuous sequence
    c1 = ValidationLayer.check_period_continuity(["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"])
    assert c1["is_continuous"] is True
    assert len(c1["missing_quarters"]) == 0

    # Sequence with missing Q3
    c2 = ValidationLayer.check_period_continuity(["Q1 FY24", "Q2 FY24", "Q4 FY24"])
    assert c2["is_continuous"] is False
    assert "Q3 FY24" in c2["missing_quarters"]

    # Multi-year continuous sequence
    c3 = ValidationLayer.check_period_continuity(["Q3 FY23", "Q4 FY23", "Q1 FY24", "Q2 FY24"])
    assert c3["is_continuous"] is True


def test_interpolate_missing_quarters():
    """Verify linear interpolation populates missing quarter values."""
    periods = ["Q1 FY24", "Q2 FY24", "Q4 FY24"]
    df = pd.DataFrame({
        "Q1 FY24": [100.0, 20.0],
        "Q2 FY24": [110.0, 22.0],
        "Q4 FY24": [130.0, 26.0],
    }, index=["revenue", "ebitda"])

    interpolated_df, new_periods = ValidationLayer.interpolate_missing_quarters(
        df, periods, ["Q3 FY24"]
    )

    assert "Q3 FY24" in new_periods
    assert new_periods == ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"]
    # Q3 revenue should be midpoint between Q2 (110) and Q4 (130) -> 120.0
    assert interpolated_df.loc["revenue", "Q3 FY24"] == 120.0
    # Q3 ebitda should be midpoint between Q2 (22) and Q4 (26) -> 24.0
    assert interpolated_df.loc["ebitda", "Q3 FY24"] == 24.0


def test_validation_layer_sanity_rules():
    """Verify sanity checks detect zero or negative revenue."""
    df_zero_rev = pd.DataFrame({
        "Q1 FY24": [0.0, 10.0],
        "Q2 FY24": [0.0, 12.0],
    }, index=["revenue", "ebitda"])

    issues = ValidationLayer.validate_statement_data(df_zero_rev, ["Q1 FY24", "Q2 FY24"])
    assert any(i["type"] == "error" for i in issues)

    with pytest.raises(ValidationError):
        ValidationLayer.create_verified_statement(df_zero_rev, ["Q1 FY24", "Q2 FY24"])
