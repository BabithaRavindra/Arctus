"""
Unit tests for RawNormalizer (Stage 1 of Ingestion).
Tests messy Excel edge cases: merged cells, transposed layouts,
accounting negatives in parentheses '(42,000)', Indian currency symbols,
and multi-sheet P&L identification.
"""

import pytest
import io
import pandas as pd
from core.normalizer import RawNormalizer
from core.synthetic import create_messy_multisheet_excel, create_transposed_csv


def test_clean_accounting_number_variants():
    """Verify conversion of accounting and Indian currency strings."""
    normalizer = RawNormalizer()

    # Accounting parentheses negatives
    assert normalizer.clean_accounting_number("(42,000)") == -42000.0
    assert normalizer.clean_accounting_number("(₹ 1,50,000.50)") == -150000.50
    assert normalizer.clean_accounting_number("-12,345") == -12345.0

    # Currency strings & commas
    assert normalizer.clean_accounting_number("₹ 12,34,567.89") == 1234567.89
    assert normalizer.clean_accounting_number("Rs. 50,000") == 50000.0
    assert normalizer.clean_accounting_number("INR 10,00,000") == 1000000.0

    # Suffix multipliers
    assert normalizer.clean_accounting_number("12.5 Cr") == 125000000.0
    assert normalizer.clean_accounting_number("45.2 Lakhs") == 4520000.0
    assert normalizer.clean_accounting_number("10 L") == 1000000.0

    # Blanks, dashes, and invalid
    assert normalizer.clean_accounting_number("-") == 0.0
    assert normalizer.clean_accounting_number("--") == 0.0
    assert normalizer.clean_accounting_number("N/A") == 0.0
    assert normalizer.clean_accounting_number("") == 0.0
    assert normalizer.clean_accounting_number(None) == 0.0


def test_period_normalization():
    """Verify period format normalization to 'Q1 FY24'."""
    assert RawNormalizer.normalize_period_label("Q1 FY24") == "Q1 FY24"
    assert RawNormalizer.normalize_period_label("Q1-FY24") == "Q1 FY24"
    assert RawNormalizer.normalize_period_label("Q1 2024") == "Q1 FY24"
    assert RawNormalizer.normalize_period_label("FY24 Q1") == "Q1 FY24"
    assert RawNormalizer.normalize_period_label("2023-Q1") == "Q1 FY23"
    assert RawNormalizer.normalize_period_label("FY 2024") == "FY24"


def test_process_messy_multisheet_excel():
    """Verify full ingestion of a 3-sheet Excel with merged cells and decorative banners."""
    excel_bytes = create_messy_multisheet_excel("Test Engineering Ltd")
    normalizer = RawNormalizer()
    res = normalizer.process(excel_bytes, "financials.xlsx")

    df = res["dataframe"]
    line_col = res["line_item_column"]
    periods = res["period_columns"]

    # Must have extracted the P&L sheet, not the Cover or Balance Sheet
    assert len(periods) == 8
    assert "Q1 FY23" in periods
    assert "Q4 FY24" in periods

    # Verify line items were preserved
    labels = df[line_col].astype(str).tolist()
    assert any("Revenue from Operations" in l for l in labels)
    assert any("Operating EBITDA" in l for l in labels)

    # Verify negative interest '(42.00)' was parsed to numeric float
    pbt_row = df[df[line_col].str.contains("PBT", case=False, na=False)]
    assert len(pbt_row) > 0
    assert isinstance(pbt_row.iloc[0][periods[0]], (int, float))


def test_process_transposed_csv():
    """Verify automatic orientation detection and pivoting for transposed CSV."""
    csv_bytes = create_transposed_csv()
    normalizer = RawNormalizer()
    res = normalizer.process(csv_bytes, "transposed_pl.csv")

    assert res["was_transposed"] is True
    periods = res["period_columns"]
    assert len(periods) == 4
    assert "Q1 FY24" in periods
    assert "Q4 FY24" in periods
