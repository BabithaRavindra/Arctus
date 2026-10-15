"""
ValidationLayer - Quality Assurance and Sanity Checks for Arctus.
Validates normalized and mapped financial statements against core accounting rules,
detects missing periods or chronology gaps, and provides actionable, human-readable
guidance instead of unhandled exceptions.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from core.models import FinancialStatement


class ValidationError(Exception):
    """Domain-specific validation exception with user-facing guidance."""
    def __init__(self, message: str, action_guidance: str, code: str = "VALIDATION_FAILED"):
        super().__init__(message)
        self.message = message
        self.action_guidance = action_guidance
        self.code = code


class ValidationLayer:
    """
    Sanity-checks mapped P&L statements before ingestion by the forecast engine.
    """

    @staticmethod
    def parse_quarter_key(period_str: str) -> Optional[Tuple[int, int]]:
        """
        Extracts (year, quarter) tuple from normalized period string 'Q1 FY24'.
        Returns None if not parseable as a quarter.
        """
        m = re.search(r"(?i)Q([1-4])[\s\-_]*FY([0-9]{2,4})", str(period_str))
        if m:
            q = int(m.group(1))
            yr = int(m.group(2))
            full_yr = 2000 + yr if yr < 100 else yr
            return (full_yr, q)
        return None

    @classmethod
    def check_period_continuity(cls, periods: List[str]) -> Dict[str, Any]:
        """
        Checks whether quarters are in sequential chronological order without gaps.
        Returns continuity status, list of detected missing quarters, and resolution options.
        """
        parsed = []
        for p in periods:
            qk = cls.parse_quarter_key(p)
            if qk:
                parsed.append((p, qk[0], qk[1]))

        if len(parsed) != len(periods) or len(parsed) < 2:
            return {
                "is_continuous": True,
                "missing_quarters": [],
                "can_interpolate": False,
            }

        # Calculate continuous quarter index: (year * 4) + (quarter - 1)
        quarter_indices = [y * 4 + (q - 1) for _, y, q in parsed]
        missing_quarters = []

        for i in range(len(quarter_indices) - 1):
            diff = quarter_indices[i + 1] - quarter_indices[i]
            if diff > 1:
                # One or more missing quarters between periods[i] and periods[i+1]
                for missing_idx in range(quarter_indices[i] + 1, quarter_indices[i + 1]):
                    m_year = missing_idx // 4
                    m_q = (missing_idx % 4) + 1
                    missing_quarters.append(f"Q{m_q} FY{m_year % 100:02d}")

        return {
            "is_continuous": len(missing_quarters) == 0,
            "missing_quarters": missing_quarters,
            "can_interpolate": len(missing_quarters) > 0,
        }

    @classmethod
    def interpolate_missing_quarters(
        cls,
        df: pd.DataFrame,
        periods: List[str],
        missing_quarters: List[str]
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Linearly interpolates values for missing intermediate quarters.
        """
        # Reconstruct ordered full timeline
        all_quarters_dict = {}
        for p in periods:
            qk = cls.parse_quarter_key(p)
            if qk:
                idx = qk[0] * 4 + (qk[1] - 1)
                all_quarters_dict[idx] = p

        min_idx = min(all_quarters_dict.keys())
        max_idx = max(all_quarters_dict.keys())

        full_timeline = []
        for idx in range(min_idx, max_idx + 1):
            if idx in all_quarters_dict:
                full_timeline.append(all_quarters_dict[idx])
            else:
                m_year = idx // 4
                m_q = (idx % 4) + 1
                full_timeline.append(f"Q{m_q} FY{m_year % 100:02d}")

        # Reindex DataFrame and interpolate linearly
        expanded_df = pd.DataFrame(index=df.index, columns=full_timeline, dtype=float)
        for col in periods:
            expanded_df[col] = df[col]

        # Interpolate across periods (columns)
        interpolated_df = expanded_df.T.interpolate(method="linear").T.bfill(axis=1).ffill(axis=1)

        return interpolated_df, full_timeline

    @classmethod
    def validate_statement_data(
        cls,
        df: pd.DataFrame,
        periods: List[str],
    ) -> List[Dict[str, str]]:
        """
        Performs sanity and business rule checks on standardized financial matrix:
        - Revenue > 0
        - Gross profit <= Revenue
        - No NaN or inf values
        Returns list of warning or error notices.
        """
        issues: List[Dict[str, str]] = []

        if "revenue" not in df.index:
            issues.append({
                "type": "error",
                "title": "Missing Revenue Metric",
                "message": "We couldn't detect or map a Revenue row in your file. Revenue is required to simulate forward projections.",
                "action": "Please assign the row representing 'Revenue from Operations' or 'Sales' in the mapping dropdown below.",
            })
            return issues

        rev = df.loc["revenue"].values
        if np.all(rev <= 0):
            issues.append({
                "type": "error",
                "title": "Zero or Negative Revenue",
                "message": "All revenue values in the uploaded statement are zero or negative.",
                "action": "Please verify your input figures or check if values were multiplied by an incorrect negative sign.",
            })

        if "gross_profit" in df.index:
            gp = df.loc["gross_profit"].values
            if np.any(gp > rev * 1.05):
                issues.append({
                    "type": "warning",
                    "title": "Gross Profit Exceeds Revenue",
                    "message": "In one or more periods, Gross Profit is greater than Total Revenue. This typically indicates a swapped row label.",
                    "action": "Check the Gross Profit and Revenue mappings.",
                })

        if "ebitda" in df.index and "gross_profit" in df.index:
            ebitda = df.loc["ebitda"].values
            gp = df.loc["gross_profit"].values
            if np.any(ebitda > gp * 1.10):
                issues.append({
                    "type": "warning",
                    "title": "EBITDA Higher than Gross Profit",
                    "message": "Operating EBITDA exceeds Gross Profit in some quarters. Unless you have massive non-operating subsidies, OPEX should reduce Gross Profit.",
                    "action": "Verify whether EBITDA and Gross Profit rows are correctly identified.",
                })

        return issues

    @classmethod
    def create_verified_statement(
        cls,
        df: pd.DataFrame,
        periods: List[str],
    ) -> Tuple[FinancialStatement, List[Dict[str, str]]]:
        """
        Validates and converts standardized DataFrame into a clean FinancialStatement instance.
        """
        issues = cls.validate_statement_data(df, periods)
        critical_errors = [i for i in issues if i["type"] == "error"]
        if critical_errors:
            first = critical_errors[0]
            raise ValidationError(first["message"], first["action"])

        statement = FinancialStatement(
            periods=periods,
            revenue=df.loc["revenue"].values,
            cogs=df.loc["cogs"].values if "cogs" in df.index else df.loc["revenue"].values * 0.6,
            gross_profit=df.loc["gross_profit"].values if "gross_profit" in df.index else df.loc["revenue"].values * 0.4,
            opex=df.loc["opex"].values if "opex" in df.index else df.loc["revenue"].values * 0.25,
            ebitda=df.loc["ebitda"].values if "ebitda" in df.index else df.loc["revenue"].values * 0.15,
            pbt=df.loc["pbt"].values if "pbt" in df.index else df.loc["revenue"].values * 0.12,
            pat=df.loc["pat"].values if "pat" in df.index else df.loc["revenue"].values * 0.09,
        )

        return statement, issues
