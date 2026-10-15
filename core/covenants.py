"""
Banking Covenants & Probabilistic Breach Analytics Module for Arctus.
Calculates deterministic and Monte Carlo simulated probabilistic breach distributions
for Indian banking consortium covenants:
- Interest Coverage Ratio (ICR >= 2.0x)
- Debt Service Coverage Ratio (DSCR >= 1.25x)
- Net Debt to EBITDA (<= 3.0x)
- Current Ratio (>= 1.33x)
- Total Outside Liabilities to Tangible Net Worth (TOL/TNW <= 2.50x)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

from core.models import FinancialStatement, Scenario, ForecastResult
from core.cockpit import CapitalStructure, DebtInstrument, get_default_capital_structure_for_statement


@dataclass
class CovenantBenchmark:
    """Benchmark threshold definitions for Indian Banking Consortium sanctions."""
    key: str
    name: str
    threshold: float
    comparison: str                     # 'gte' (>=) or 'lte' (<=)
    unit_label: str                     # 'x'
    warning_cushion_pct: float          # e.g., 15% buffer
    bank_standard: str
    formula_str: str
    description: str


STANDARD_BANKING_COVENANTS: Dict[str, CovenantBenchmark] = {
    "icr": CovenantBenchmark(
        key="icr",
        name="Interest Coverage Ratio (ICR)",
        threshold=2.00,
        comparison="gte",
        unit_label="x",
        warning_cushion_pct=15.0,
        bank_standard="≥ 2.00x (Consortium Sanction Norm)",
        formula_str="Operating EBITDA / Annual Finance Cost",
        description="Assesses operating cash earnings cushion to absorb floating borrowing costs without loan restructuring."
    ),
    "dscr": CovenantBenchmark(
        key="dscr",
        name="Debt Service Coverage Ratio (DSCR)",
        threshold=1.25,
        comparison="gte",
        unit_label="x",
        warning_cushion_pct=10.0,
        bank_standard="≥ 1.25x (Term Loan Sanction Norm)",
        formula_str="(PAT + Depreciation + Interest) / (Interest + Scheduled Principal Repayment)",
        description="Measures post-tax cash availability to satisfy both interest expenses and mandatory term loan amortizations."
    ),
    "nd_ebitda": CovenantBenchmark(
        key="nd_ebitda",
        name="Total / Net Debt to EBITDA",
        threshold=3.00,
        comparison="lte",
        unit_label="x",
        warning_cushion_pct=15.0,
        bank_standard="≤ 3.00x (Maximum Total Leverage Cap)",
        formula_str="(Gross Debt - Cash & Liquid Mutual Funds) / Annualized Operating EBITDA",
        description="Scales net debt payback requirements against operational profitability. Ratios exceeding 3.0x trigger bank oversight."
    ),
    "current_ratio": CovenantBenchmark(
        key="current_ratio",
        name="Current Ratio (Working Capital)",
        threshold=1.33,
        comparison="gte",
        unit_label="x",
        warning_cushion_pct=10.0,
        bank_standard="≥ 1.33x (RBI Tandon / Nayak Committee Norm)",
        formula_str="Current Assets / Current Liabilities",
        description="Short-term liquidity health standard required by Indian state and private banks for CC/OD renewals."
    ),
    "tol_tnw": CovenantBenchmark(
        key="tol_tnw",
        name="TOL / TNW (Solvency Ratio)",
        threshold=2.50,
        comparison="lte",
        unit_label="x",
        warning_cushion_pct=15.0,
        bank_standard="≤ 2.50x (Long-term Solvency Cap)",
        formula_str="(Gross Debt + Current Liabilities) / Tangible Net Worth",
        description="Enterprise gearing and outside liability exposure against promoter equity capital and retained earnings."
    ),
}


@dataclass
class QuarterCovenantEvaluation:
    """Evaluation of a single covenant in a specific quarter."""
    quarter: str
    actual_value: float
    threshold: float
    comparison: str
    unit_label: str
    headroom: float
    cushion_pct: float
    status: str                         # 'compliant', 'warning', 'breached'
    breach_probability: float           # 0.0 to 100.0% from Monte Carlo
    simulated_distribution: Optional[np.ndarray] = None


@dataclass
class CovenantBreachAnalysis:
    """Comprehensive covenant analytics across all forward quarters and scenarios."""
    covenant_key: str
    name: str
    bank_standard: str
    formula_str: str
    quarterly_evaluations: List[QuarterCovenantEvaluation]
    max_breach_probability: float
    first_breach_quarter: Optional[str]
    cushion_trend: str                  # 'expanding', 'deteriorating', 'stable'
    risk_level: str                     # 'low', 'moderate', 'critical'
    executive_warning: str


def compute_probabilistic_covenant_matrix(
    stmt: FinancialStatement,
    result: ForecastResult,
    cap_struct: Optional[CapitalStructure] = None,
    repo_shock_bps: float = 0.0
) -> Dict[str, CovenantBreachAnalysis]:
    """
    Computes quarter-by-quarter covenant compliance values along with Monte Carlo simulated
    breach probabilities across all 4 forward quarters.
    """
    if cap_struct is None:
        cap_struct = get_default_capital_structure_for_statement(stmt)

    fwd_periods = result.forecast_periods
    num_quarters = len(fwd_periods)
    iterations = result.monte_carlo_runs["ebitda"].shape[0]

    # 1. Capital structure base parameters
    repo_adj = repo_shock_bps / 10000.0
    gross_debt = sum(inst.principal_outstanding for inst in cap_struct.instruments)

    # Compute floating interest and quarterly debt service
    q_interest = 0.0
    q_principal = 0.0
    for inst in cap_struct.instruments:
        rate = inst.interest_rate
        if inst.is_floating:
            rate = max(0.01, rate + repo_adj)
        q_interest += (inst.principal_outstanding * rate) / 4.0
        q_principal += inst.annual_amortization / 4.0

    q_debt_service = q_interest + q_principal
    q_deprec = cap_struct.depreciation_annual / 4.0
    cash_bal = cap_struct.cash_and_equivalents
    curr_assets = cap_struct.current_assets
    curr_liabs = max(1.0, cap_struct.current_liabilities)
    tnw = max(1.0, cap_struct.tangible_net_worth)

    analyses: Dict[str, CovenantBreachAnalysis] = {}

    for cov_key, benchmark in STANDARD_BANKING_COVENANTS.items():
        q_evals: List[QuarterCovenantEvaluation] = []
        max_prob = 0.0
        first_breach_q = None

        for q_idx, period_label in enumerate(fwd_periods):
            # Point forecast items for this quarter
            pt_ebitda = float(result.point_forecast["ebitda"][q_idx])
            pt_rev = float(result.point_forecast["revenue"][q_idx])

            # Monte Carlo simulated matrix for this quarter (shape: (iterations,))
            mc_ebitda = result.monte_carlo_runs["ebitda"][:, q_idx]
            mc_rev = result.monte_carlo_runs["revenue"][:, q_idx]

            if cov_key == "icr":
                # ICR = Quarter EBITDA / Quarter Interest
                actual_val = pt_ebitda / q_interest if q_interest > 0 else 99.0
                sim_vals = mc_ebitda / q_interest if q_interest > 0 else np.full(iterations, 99.0)
                breach_mask = sim_vals < benchmark.threshold

            elif cov_key == "dscr":
                # DSCR = (PAT + Deprec + Interest) / Debt Service
                pt_pbt = max(0.0, pt_ebitda - q_deprec - q_interest)
                pt_pat = pt_pbt * (1.0 - 0.25)
                actual_val = (pt_pat + q_deprec + q_interest) / q_debt_service if q_debt_service > 0 else 99.0

                mc_pbt = np.maximum(0.0, mc_ebitda - q_deprec - q_interest)
                mc_pat = mc_pbt * 0.75
                sim_vals = (mc_pat + q_deprec + q_interest) / q_debt_service if q_debt_service > 0 else np.full(iterations, 99.0)
                breach_mask = sim_vals < benchmark.threshold

            elif cov_key == "nd_ebitda":
                # Annualized EBITDA = Quarter EBITDA * 4
                ann_pt_ebitda = max(0.01, pt_ebitda * 4.0)
                actual_val = max(0.0, gross_debt - cash_bal) / ann_pt_ebitda

                ann_mc_ebitda = np.maximum(0.01, mc_ebitda * 4.0)
                sim_vals = np.maximum(0.0, gross_debt - cash_bal) / ann_mc_ebitda
                breach_mask = sim_vals > benchmark.threshold

            elif cov_key == "current_ratio":
                # Current ratio adjusts with revenue shifts affecting working capital
                rev_ratio = pt_rev / (stmt.revenue[-1] if stmt.revenue[-1] > 0 else 1.0)
                adj_ca = curr_assets * (0.5 + 0.5 * rev_ratio)
                actual_val = adj_ca / curr_liabs

                mc_rev_ratio = mc_rev / (stmt.revenue[-1] if stmt.revenue[-1] > 0 else 1.0)
                sim_adj_ca = curr_assets * (0.5 + 0.5 * mc_rev_ratio)
                sim_vals = sim_adj_ca / curr_liabs
                breach_mask = sim_vals < benchmark.threshold

            elif cov_key == "tol_tnw":
                # TOL / TNW = (Gross Debt + Current Liabs) / Tangible Net Worth
                actual_val = (gross_debt + curr_liabs) / tnw
                sim_vals = np.full(iterations, actual_val)
                breach_mask = sim_vals > benchmark.threshold

            else:
                actual_val = 0.0
                sim_vals = np.zeros(iterations)
                breach_mask = np.zeros(iterations, dtype=bool)

            breach_prob = float(np.mean(breach_mask) * 100.0)
            if breach_prob > max_prob:
                max_prob = breach_prob
            if breach_prob >= 10.0 and first_breach_q is None:
                first_breach_q = period_label

            # Compute headroom and cushion
            if benchmark.comparison == "gte":
                headroom = actual_val - benchmark.threshold
                cushion_pct = (headroom / benchmark.threshold) * 100.0
                if actual_val < benchmark.threshold or breach_prob >= 40.0:
                    status = "breached"
                elif cushion_pct < benchmark.warning_cushion_pct or breach_prob >= 15.0:
                    status = "warning"
                else:
                    status = "compliant"
            else:
                headroom = benchmark.threshold - actual_val
                cushion_pct = (headroom / benchmark.threshold) * 100.0
                if actual_val > benchmark.threshold or breach_prob >= 40.0:
                    status = "breached"
                elif cushion_pct < benchmark.warning_cushion_pct or breach_prob >= 15.0:
                    status = "warning"
                else:
                    status = "compliant"

            q_evals.append(QuarterCovenantEvaluation(
                quarter=period_label,
                actual_value=float(actual_val),
                threshold=benchmark.threshold,
                comparison=benchmark.comparison,
                unit_label=benchmark.unit_label,
                headroom=float(headroom),
                cushion_pct=float(cushion_pct),
                status=status,
                breach_probability=float(breach_prob),
                simulated_distribution=sim_vals
            ))

        # Overall trend
        first_cushion = q_evals[0].cushion_pct
        last_cushion = q_evals[-1].cushion_pct
        if last_cushion > first_cushion + 3.0:
            trend = "expanding"
        elif last_cushion < first_cushion - 3.0:
            trend = "deteriorating"
        else:
            trend = "stable"

        # Risk classification
        if max_prob >= 35.0 or any(e.status == "breached" for e in q_evals):
            risk_level = "critical"
        elif max_prob >= 12.0 or any(e.status == "warning" for e in q_evals):
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Executive warning message
        if max_prob >= 10.0 and first_breach_q:
            exec_warning = f"{max_prob:.1f}% risk of breaching the {benchmark.threshold:.2f}{benchmark.unit_label} bank sanction threshold in {first_breach_q}."
        elif any(e.status == "warning" for e in q_evals):
            exec_warning = f"Headroom cushion narrows to {min(e.cushion_pct for e in q_evals):.1f}% under stress. Consortium surveillance recommended."
        else:
            exec_warning = f"Strong compliance cushion maintained across all quarters (minimum cushion: {min(e.cushion_pct for e in q_evals):.1f}%)."

        analyses[cov_key] = CovenantBreachAnalysis(
            covenant_key=cov_key,
            name=benchmark.name,
            bank_standard=benchmark.bank_standard,
            formula_str=benchmark.formula_str,
            quarterly_evaluations=q_evals,
            max_breach_probability=float(max_prob),
            first_breach_quarter=first_breach_q,
            cushion_trend=trend,
            risk_level=risk_level,
            executive_warning=exec_warning
        )

    return analyses
