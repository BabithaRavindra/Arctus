"""
Unit tests for SchemaMapper (Stage 2 of Ingestion).
Tests RapidFuzz fuzzy matching on Indian P&L labels, confidence thresholds,
manual overrides, and subtotal derivations.
"""

import pytest
import pandas as pd
import numpy as np
from core.mapper import SchemaMapper


def test_schema_mapper_fuzzy_matching():
    """Verify fuzzy matching for standard Indian accounting terms."""
    mapper = SchemaMapper(confidence_threshold=0.78)

    labels = [
        "Revenue from operations (Gross)",
        "Cost of Materials Consumed",
        "Employee Benefit Expenses",
        "Operating EBITDA",
        "Profit Before Tax (PBT)",
        "Tax Expense",
        "Profit After Tax (PAT)",
    ]

    res = mapper.auto_map_schema(labels)
    mapping = res["mapping"]
    scores = res["confidence_scores"]

    assert mapping["revenue"] == "Revenue from operations (Gross)"
    assert mapping["cogs"] == "Cost of Materials Consumed"
    assert mapping["opex"] == "Employee Benefit Expenses"
    assert mapping["ebitda"] == "Operating EBITDA"
    assert mapping["pbt"] == "Profit Before Tax (PBT)"
    assert mapping["pat"] == "Profit After Tax (PAT)"

    assert scores["revenue"] >= 78.0
    assert scores["cogs"] >= 78.0
    assert scores["ebitda"] >= 78.0


def test_schema_mapper_manual_overrides():
    """Verify that manual overrides take absolute precedence over fuzzy matching."""
    mapper = SchemaMapper()
    labels = ["Total Sales", "Materials", "Other Costs", "EBITDA"]

    overrides = {
        "revenue": "Total Sales",
        "cogs": "Materials",
    }

    res = mapper.auto_map_schema(labels, manual_overrides=overrides)
    assert res["mapping"]["revenue"] == "Total Sales"
    assert res["mapping"]["cogs"] == "Materials"
    assert res["confidence_scores"]["revenue"] == 1.0


def test_subtotal_derivation():
    """Verify derivation of missing Gross Profit and EBITDA rows from components."""
    mapper = SchemaMapper()
    period_cols = ["Q1 FY24", "Q2 FY24"]

    # Raw table missing Gross Profit and EBITDA
    df = pd.DataFrame({
        "Particulars": ["Revenue from Operations", "Cost of Materials Consumed", "Operating Overheads"],
        "Q1 FY24": [100.0, 60.0, 20.0],
        "Q2 FY24": [110.0, 66.0, 22.0],
    })

    mapping = {
        "revenue": "Revenue from Operations",
        "cogs": "Cost of Materials Consumed",
        "opex": "Operating Overheads",
    }

    std_df = mapper.construct_standardized_statement(df, "Particulars", period_cols, mapping)

    # Gross profit should be 100 - 60 = 40 in Q1
    assert std_df.loc["gross_profit", "Q1 FY24"] == 40.0
    assert std_df.loc["gross_profit", "Q2 FY24"] == 44.0

    # EBITDA should be 40 - 20 = 20 in Q1
    assert std_df.loc["ebitda", "Q1 FY24"] == 20.0
    assert std_df.loc["ebitda", "Q2 FY24"] == 22.0
