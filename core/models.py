"""
Domain models for Arctus FP&A Stress-Testing Platform.
Defines strongly typed, testable data structures for financial statements,
scenarios, forecast results, and user accounts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


@dataclass
class FinancialStatement:
    """
    Standardized quarterly or annual P&L statement data model.
    Encapsulates verified historical line items across chronological periods.
    """
    periods: List[str]
    revenue: np.ndarray
    cogs: np.ndarray
    gross_profit: np.ndarray
    opex: np.ndarray
    ebitda: np.ndarray
    pbt: np.ndarray
    pat: np.ndarray

    def __post_init__(self):
        # Convert any sequences to float64 numpy arrays
        self.revenue = np.asarray(self.revenue, dtype=np.float64)
        self.cogs = np.asarray(self.cogs, dtype=np.float64)
        self.gross_profit = np.asarray(self.gross_profit, dtype=np.float64)
        self.opex = np.asarray(self.opex, dtype=np.float64)
        self.ebitda = np.asarray(self.ebitda, dtype=np.float64)
        self.pbt = np.asarray(self.pbt, dtype=np.float64)
        self.pat = np.asarray(self.pat, dtype=np.float64)

        n = len(self.periods)
        for key, arr in [
            ("revenue", self.revenue),
            ("cogs", self.cogs),
            ("gross_profit", self.gross_profit),
            ("opex", self.opex),
            ("ebitda", self.ebitda),
            ("pbt", self.pbt),
            ("pat", self.pat),
        ]:
            if len(arr) != n:
                raise ValueError(
                    f"Length mismatch: {key} has {len(arr)} elements, expected {n} periods."
                )

    def to_dataframe(self) -> pd.DataFrame:
        """Convert statement to a clean pandas DataFrame."""
        return pd.DataFrame({
            "Period": self.periods,
            "Revenue": self.revenue,
            "COGS": self.cogs,
            "Gross Profit": self.gross_profit,
            "OPEX": self.opex,
            "EBITDA": self.ebitda,
            "PBT": self.pbt,
            "PAT": self.pat,
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert statement to serializable dictionary."""
        return {
            "periods": self.periods,
            "revenue": self.revenue.tolist(),
            "cogs": self.cogs.tolist(),
            "gross_profit": self.gross_profit.tolist(),
            "opex": self.opex.tolist(),
            "ebitda": self.ebitda.tolist(),
            "pbt": self.pbt.tolist(),
            "pat": self.pat.tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialStatement":
        """Instantiate statement from a dictionary."""
        return cls(
            periods=list(data["periods"]),
            revenue=np.array(data["revenue"], dtype=np.float64),
            cogs=np.array(data["cogs"], dtype=np.float64),
            gross_profit=np.array(data["gross_profit"], dtype=np.float64),
            opex=np.array(data["opex"], dtype=np.float64),
            ebitda=np.array(data["ebitda"], dtype=np.float64),
            pbt=np.array(data["pbt"], dtype=np.float64),
            pat=np.array(data["pat"], dtype=np.float64),
        )

    def get_run_rate(self) -> Dict[str, float]:
        """Calculate TTM (Trailing Twelve Months) or annualized figures."""
        weights = min(4, len(self.periods))
        factor = 4.0 / weights
        return {
            "annualized_revenue": float(np.sum(self.revenue[-weights:]) * factor),
            "annualized_ebitda": float(np.sum(self.ebitda[-weights:]) * factor),
            "latest_ebitda_margin": float(
                (self.ebitda[-1] / self.revenue[-1] * 100) if self.revenue[-1] != 0 else 0.0
            ),
            "latest_gross_margin": float(
                (self.gross_profit[-1] / self.revenue[-1] * 100) if self.revenue[-1] != 0 else 0.0
            ),
        }


@dataclass
class Scenario:
    """
    Macroeconomic and operational assumptions for forward stress-testing.
    """
    name: str                           # e.g., 'Recession', 'Base', 'Growth'
    rev_growth: float                   # Annualized / quarterly revenue growth (e.g. 0.08 for +8%)
    cogs_inflation: float               # COGS inflation rate (e.g. 0.05 for +5%)
    opex_inflation: float               # OPEX inflation rate (e.g. 0.06 for +6%)
    macro_shock: float = 1.0            # Shock multiplier on cost of capital & overheads (e.g. 1.15)
    color: str = "#FCA311"              # Visual theme color for this scenario
    description: str = ""
    probability_weight: float = 0.0     # Relative weight for blended scenario forecasting (e.g. 0.20 for 20%)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize scenario parameters to dictionary."""
        return {
            "name": self.name,
            "rev_growth": self.rev_growth,
            "cogs_inflation": self.cogs_inflation,
            "opex_inflation": self.opex_inflation,
            "macro_shock": self.macro_shock,
            "color": self.color,
            "description": self.description,
            "probability_weight": self.probability_weight,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scenario":
        """Instantiate scenario from dictionary."""
        return cls(
            name=str(data["name"]),
            rev_growth=float(data["rev_growth"]),
            cogs_inflation=float(data["cogs_inflation"]),
            opex_inflation=float(data["opex_inflation"]),
            macro_shock=float(data.get("macro_shock", 1.0)),
            color=str(data.get("color", "#FCA311")),
            description=str(data.get("description", "")),
            probability_weight=float(data.get("probability_weight", 0.0)),
        )


@dataclass
class ForecastResult:
    """
    Encapsulates results from a forward projection and Monte Carlo stress test.
    """
    scenario: Scenario
    forecast_periods: List[str]
    point_forecast: Dict[str, np.ndarray]          # Metric -> 4-element array
    # Monte Carlo simulation distribution: (1000 iterations x 4 quarters) per metric
    monte_carlo_runs: Dict[str, np.ndarray]
    # Summary statistical percentiles: { metric: { 'p10': [], 'p25': [], 'mean': [], 'median': [], 'p75': [], 'p90': [], 'std': [] } }
    confidence_bands: Dict[str, Dict[str, np.ndarray]]
    # Probability that cumulative forward EBITDA is negative (Value-at-Risk signal)
    loss_probability: float
    # Tornado sensitivity metrics: list of dicts with assumption name, downside, upside, swing
    tornado_sensitivities: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize forecast result for API and SQLite storage."""
        return {
            "scenario": self.scenario.to_dict(),
            "forecast_periods": self.forecast_periods,
            "point_forecast": {k: v.tolist() for k, v in self.point_forecast.items()},
            "confidence_bands": {
                metric: {stat: arr.tolist() for stat, arr in stats.items()}
                for metric, stats in self.confidence_bands.items()
            },
            "loss_probability": self.loss_probability,
            "tornado_sensitivities": self.tornado_sensitivities,
        }


@dataclass
class UserAccount:
    """
    Represents an authenticated user and company profile.
    """
    id: int
    email: str
    name: str
    company_name: str
    default_unit: str = "crores"        # 'crores', 'lakhs', or 'raw'
    created_at: str = ""
