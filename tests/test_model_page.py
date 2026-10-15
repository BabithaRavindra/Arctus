import pytest
import numpy as np
import pandas as pd
from core.synthetic import generate_clean_midmarket_statement
from core.models import FinancialStatement
from pages_ui.model_page import (
    statement_to_modeling_df,
    modeling_df_to_statement,
    STANDARD_P_AND_L_ROWS,
)

def test_statement_to_modeling_df_structure():
    stmt = generate_clean_midmarket_statement()
    df = statement_to_modeling_df(stmt)
    
    assert "Line Item" in df.columns
    assert "Metric Key" in df.columns
    
    # Periods should match statement periods
    for p in stmt.periods:
        assert p in df.columns
        
    # Check that core line items exist
    items = df["Line Item"].tolist()
    assert "Revenue from Operations" in items
    assert "Cost of Goods Sold (COGS)" in items
    assert "Gross Profit" in items
    assert "Operating Expenses (OPEX)" in items
    assert "Operating EBITDA" in items
    assert "Profit Before Tax (PBT)" in items
    assert "Profit After Tax (PAT)" in items

def test_statement_df_roundtrip_fidelity():
    original_stmt = generate_clean_midmarket_statement()
    df = statement_to_modeling_df(original_stmt)
    
    rebuilt_stmt = modeling_df_to_statement(df, original_stmt.periods)
    
    assert rebuilt_stmt.periods == original_stmt.periods
    np.testing.assert_allclose(rebuilt_stmt.revenue, original_stmt.revenue, rtol=1e-5)
    np.testing.assert_allclose(rebuilt_stmt.cogs, original_stmt.cogs, rtol=1e-5)
    np.testing.assert_allclose(rebuilt_stmt.gross_profit, original_stmt.gross_profit, rtol=1e-5)
    np.testing.assert_allclose(rebuilt_stmt.ebitda, original_stmt.ebitda, rtol=1e-5)
    np.testing.assert_allclose(rebuilt_stmt.pat, original_stmt.pat, rtol=1e-5)

def test_modeling_df_custom_quarter_support():
    stmt = generate_clean_midmarket_statement()
    df = statement_to_modeling_df(stmt)
    
    # Add a new quarter Q1 FY26
    new_quarter = "Q1 FY26"
    df[new_quarter] = df[stmt.periods[-1]] * 1.05
    new_periods = stmt.periods + [new_quarter]
    
    rebuilt = modeling_df_to_statement(df, new_periods)
    assert len(rebuilt.periods) == len(stmt.periods) + 1
    assert rebuilt.periods[-1] == "Q1 FY26"
    assert len(rebuilt.revenue) == len(new_periods)

def test_modeling_df_missing_revenue_error():
    stmt = generate_clean_midmarket_statement()
    df = statement_to_modeling_df(stmt)
    # Drop revenue row
    df = df[df["Metric Key"] != "revenue"]
    with pytest.raises(ValueError, match="Revenue row is required"):
        modeling_df_to_statement(df, stmt.periods)
