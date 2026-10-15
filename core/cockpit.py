"""
Executive Cockpit & Capital Structure Module for Arctus.
Provides high-level institutional corporate finance metrics:
- Cash & Liquidity Runway (Months of operating cushion)
- Annualized EBITDA Run-Rate & Operating Leverage
- Debt Capital Structure & Amortization Maturity Profile
- Indian Banking Covenant Matrix (ICR, DSCR, Net Debt/EBITDA, Current Ratio, TOL/TNW)
- Real-time What-If sensitivity shock recalculations with zero spreadsheet manipulation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from core.models import FinancialStatement


@dataclass
class DebtInstrument:
    """Represents a specific corporate debt facility."""
    name: str                           # e.g., 'Working Capital CC/OD (SBI)', 'Equipment Term Loan (HDFC)'
    category: str                       # 'working_capital', 'term_loan', 'promoter_debt'
    principal_outstanding: float        # in ₹ Actuals
    interest_rate: float                # Annual interest rate (e.g. 0.0875 for 8.75%)
    is_floating: bool                   # Floating linked to RBI repo rate vs fixed
    spread_over_repo: float             # Spread in bps / pct over repo (e.g. 0.0225 for 225 bps)
    annual_amortization: float          # Scheduled annual principal repayment
    maturity_year: str                  # e.g., 'FY26', 'FY28', 'Revolving'
    lender: str = "Indian Commercial Bank"


@dataclass
class CapitalStructure:
    """Enterprise balance sheet capital structure parameters."""
    cash_and_equivalents: float         # Liquid cash in bank accounts (₹ Actuals)
    undrawn_sanctioned_limits: float    # Available unutilized CC/OD working capital lines
    instruments: List[DebtInstrument] = field(default_factory=list)
    tangible_net_worth: float = 0.0     # TNW for TOL/TNW covenant (₹ Actuals)
    current_assets: float = 0.0         # For Current Ratio (₹ Actuals)
    current_liabilities: float = 0.0    # For Current Ratio (₹ Actuals)
    depreciation_annual: float = 0.0    # Annual non-cash depreciation for DSCR (₹ Actuals)


@dataclass
class CovenantRatio:
    """Individual banking covenant evaluation."""
    name: str                           # e.g., 'Interest Coverage Ratio (ICR)'
    actual_value: float
    threshold: float
    comparison: str                     # 'gte' (>=) or 'lte' (<=)
    unit_label: str                     # 'x' or '%'
    headroom: float                     # Actual - Threshold (positive is good)
    cushion_pct: float                  # Headroom as % of threshold
    status: str                         # 'compliant', 'warning', 'breached'
    bank_standard: str                  # e.g., '≥ 2.00x (Standard Sanction)'
    description: str                    # Explanatory formula / note


@dataclass
class CockpitMetrics:
    """Complete executive summary metrics for C-suite view."""
    company_name: str
    annualized_revenue: float
    annualized_ebitda: float
    ebitda_margin_pct: float
    gross_margin_pct: float
    
    # Liquidity & Runway
    total_liquidity: float              # Cash + Undrawn CC/OD limits
    monthly_operating_burn: float
    cash_runway_months: float
    runway_status: str                  # 'healthy', 'adequate', 'tight'
    
    # Debt & Leverage
    gross_debt: float
    net_debt: float
    net_debt_to_ebitda: float
    annual_finance_cost: float
    annual_principal_repayment: float
    total_annual_debt_service: float
    blended_interest_rate_pct: float
    
    # Banking Covenants
    covenants: Dict[str, CovenantRatio]
    all_covenants_compliant: bool
    covenants_passed_count: int
    covenants_total_count: int
    
    # 12-Month Liquidity Forecast Projection
    monthly_liquidity_trajectory: List[Dict[str, Any]]
    
    # Debt Maturity Schedule
    debt_maturity_schedule: List[Dict[str, Any]]
    
    # Sensitivity Impacts
    applied_repo_shock_bps: float
    applied_cogs_inflation_pct: float
    applied_revenue_shock_pct: float
    ebitda_variance_from_shocks: float


def get_default_capital_structure_for_statement(
    stmt: FinancialStatement,
    company_tier: str = "midmarket_50cr"
) -> CapitalStructure:
    """
    Constructs a realistic, institutional Indian mid-market capital structure
    tailored to the company's financial statement magnitude.
    """
    run_rate = stmt.get_run_rate()
    ann_rev = run_rate["annualized_revenue"]
    ann_ebitda = run_rate["annualized_ebitda"]
    
    # Calibrate realistic ratios based on enterprise size:
    # Working capital limit: ~15-20% of annual turnover
    # Cash balance: ~7-10% of annual turnover
    # Term debt: ~1.2x - 1.8x EBITDA
    
    cash_balance = ann_rev * 0.084          # ~8.4% of turnover in cash/liquid mutual funds
    undrawn_limits = ann_rev * 0.085        # ~8.5% sanctioned undrawn CC/OD buffer
    
    wc_limit_util = ann_rev * 0.17          # ~17% of revenue in utilized CC/OD limit
    term_loan_1 = ann_ebitda * 0.55         # Capex term loan
    term_loan_2 = ann_ebitda * 0.20         # Equipment / automation loan
    promoter_unsecured = ann_ebitda * 0.13  # Subordinated patient debt
    
    instruments = [
        DebtInstrument(
            name="Working Capital Facility (Cash Credit / Overdraft)",
            category="working_capital",
            principal_outstanding=wc_limit_util,
            interest_rate=0.0875,          # Repo (6.50%) + 225 bps spread = 8.75%
            is_floating=True,
            spread_over_repo=0.0225,
            annual_amortization=wc_limit_util * 0.05,  # 5% annual turnover/revolving paydown
            maturity_year="Revolving (Annual Renewal)",
            lender="State Bank of India (Consortium Lead)"
        ),
        DebtInstrument(
            name="Plant & Machinery Term Loan",
            category="term_loan",
            principal_outstanding=term_loan_1,
            interest_rate=0.0925,          # 9.25%
            is_floating=True,
            spread_over_repo=0.0275,
            annual_amortization=term_loan_1 / 4.0,  # 4-year remaining tenure
            maturity_year="FY28",
            lender="HDFC Bank"
        ),
        DebtInstrument(
            name="Green Energy / Solar Capex Facility",
            category="term_loan",
            principal_outstanding=term_loan_2,
            interest_rate=0.0850,          # 8.50% concessional
            is_floating=False,
            spread_over_repo=0.0200,
            annual_amortization=term_loan_2 / 3.0,  # 3-year tenure
            maturity_year="FY27",
            lender="SIDBI"
        ),
        DebtInstrument(
            name="Promoter Subordinated Debt",
            category="promoter_debt",
            principal_outstanding=promoter_unsecured,
            interest_rate=0.0700,          # 7.00% fixed
            is_floating=False,
            spread_over_repo=0.0050,
            annual_amortization=0.0,       # Bullet repayment on maturity
            maturity_year="FY29+",
            lender="Promoter Group"
        ),
    ]
    
    tangible_net_worth = ann_rev * 0.42     # ~42% of turnover in equity + reserves
    current_assets = ann_rev * 0.38         # Inventories + Receivables + Cash
    current_liabilities = ann_rev * 0.275   # Payables + Short-term borrowings
    depreciation_annual = ann_rev * 0.045   # ~4.5% depreciation
    
    return CapitalStructure(
        cash_and_equivalents=cash_balance,
        undrawn_sanctioned_limits=undrawn_limits,
        instruments=instruments,
        tangible_net_worth=tangible_net_worth,
        current_assets=current_assets,
        current_liabilities=current_liabilities,
        depreciation_annual=depreciation_annual
    )


def calculate_cockpit_metrics(
    stmt: FinancialStatement,
    cap_struct: Optional[CapitalStructure] = None,
    repo_rate_shock_bps: float = 0.0,       # in basis points, e.g. +50 or -25
    cogs_inflation_pct: float = 0.0,        # in percent, e.g. +5.0 for 5% cost surge
    revenue_shock_pct: float = 0.0,         # in percent, e.g. -10.0 for 10% demand drop
    company_name: str = "Apex Precision Automotives Ltd."
) -> CockpitMetrics:
    """
    Computes high-level institutional executive metrics, cash runway,
    debt maturity schedule, and banking covenant compliance.
    Supports real-time What-If sensitivity adjustments on repo rate, inflation, and revenue.
    """
    if cap_struct is None:
        cap_struct = get_default_capital_structure_for_statement(stmt)
        
    run_rate = stmt.get_run_rate()
    base_rev = run_rate["annualized_revenue"]
    base_ebitda = run_rate["annualized_ebitda"]
    
    # 1. Apply sensitivity shocks on P&L
    # Revenue shock:
    rev_multiplier = 1.0 + (revenue_shock_pct / 100.0)
    stressed_rev = base_rev * rev_multiplier
    
    # COGS inflation shock:
    # Historical COGS ratio:
    cogs_ratio = float(np.sum(stmt.cogs[-4:]) / np.sum(stmt.revenue[-4:])) if np.sum(stmt.revenue[-4:]) > 0 else 0.60
    base_annual_cogs = base_rev * cogs_ratio
    cogs_inflation_multiplier = 1.0 + (cogs_inflation_pct / 100.0)
    stressed_cogs = base_annual_cogs * rev_multiplier * cogs_inflation_multiplier
    
    # OPEX baseline:
    opex_ratio = float(np.sum(stmt.opex[-4:]) / np.sum(stmt.revenue[-4:])) if np.sum(stmt.revenue[-4:]) > 0 else 0.22
    stressed_opex = base_rev * opex_ratio * (1.0 + 0.5 * (revenue_shock_pct / 100.0)) # partial variable opex
    
    # Stressed EBITDA:
    stressed_ebitda = max(0.01, stressed_rev - stressed_cogs - stressed_opex)
    ebitda_variance = stressed_ebitda - base_ebitda
    
    gross_margin_pct = float((stressed_rev - stressed_cogs) / stressed_rev * 100.0) if stressed_rev > 0 else 0.0
    ebitda_margin_pct = float(stressed_ebitda / stressed_rev * 100.0) if stressed_rev > 0 else 0.0
    
    # 2. Capital Structure & Debt Service with Floating Repo Rate Shock
    repo_shock_decimal = repo_rate_shock_bps / 10000.0  # e.g. 50 bps -> 0.0050
    
    gross_debt = 0.0
    annual_finance_cost = 0.0
    annual_principal_repayment = 0.0
    total_interest_nominal = 0.0
    
    maturity_map: Dict[str, float] = {}
    
    for inst in cap_struct.instruments:
        gross_debt += inst.principal_outstanding
        
        # Effective rate including floating repo shock
        eff_rate = inst.interest_rate
        if inst.is_floating:
            eff_rate = max(0.01, eff_rate + repo_shock_decimal)
            
        interest_charge = inst.principal_outstanding * eff_rate
        annual_finance_cost += interest_charge
        total_interest_nominal += inst.principal_outstanding * inst.interest_rate
        
        annual_principal_repayment += inst.annual_amortization
        
        mat_key = inst.maturity_year
        maturity_map[mat_key] = maturity_map.get(mat_key, 0.0) + inst.principal_outstanding
        
    total_annual_debt_service = annual_finance_cost + annual_principal_repayment
    blended_interest_rate_pct = (annual_finance_cost / gross_debt * 100.0) if gross_debt > 0 else 0.0
    
    # Net Debt
    net_debt = max(0.0, gross_debt - cap_struct.cash_and_equivalents)
    net_debt_to_ebitda = net_debt / stressed_ebitda if stressed_ebitda > 0 else 99.0
    
    # 3. Liquidity & Cash Runway Calculation
    total_liquidity = cap_struct.cash_and_equivalents + cap_struct.undrawn_sanctioned_limits
    
    # Monthly operating burn = (Stressed OPEX + Annual Finance Cost) / 12 months - Operating Cash Inflow
    # For a profitable corporate, net monthly burn is buffer against revenue shocks:
    monthly_fixed_outflows = (stressed_opex + annual_finance_cost + annual_principal_repayment) / 12.0
    monthly_operating_inflows = (stressed_rev - stressed_cogs) / 12.0
    monthly_net_burn = max(monthly_fixed_outflows * 0.35, monthly_fixed_outflows - monthly_operating_inflows)
    
    if monthly_net_burn <= 0:
        monthly_net_burn = monthly_fixed_outflows * 0.25 # standard baseline working capital drain
        
    cash_runway_months = total_liquidity / monthly_net_burn if monthly_net_burn > 0 else 36.0
    
    if cash_runway_months >= 12.0:
        runway_status = "healthy"
    elif cash_runway_months >= 6.0:
        runway_status = "adequate"
    else:
        runway_status = "tight"
        
    # 4. Bank Covenant Health Matrix
    # 4.1 Interest Coverage Ratio (ICR = EBITDA / Finance Cost)
    icr_actual = stressed_ebitda / annual_finance_cost if annual_finance_cost > 0 else 99.0
    icr_threshold = 2.00
    icr_headroom = icr_actual - icr_threshold
    icr_cushion_pct = (icr_headroom / icr_threshold) * 100.0
    icr_status = "compliant" if icr_actual >= icr_threshold else ("warning" if icr_actual >= 1.60 else "breached")
    
    # 4.2 Debt Service Coverage Ratio (DSCR = (PAT + Depr + Int) / Debt Service)
    # Approximate PAT = (EBITDA - Depr - Finance Cost) * (1 - 0.25 tax)
    stressed_pbt = max(0.0, stressed_ebitda - cap_struct.depreciation_annual - annual_finance_cost)
    stressed_pat = stressed_pbt * 0.75
    dscr_numerator = stressed_pat + cap_struct.depreciation_annual + annual_finance_cost
    dscr_actual = dscr_numerator / total_annual_debt_service if total_annual_debt_service > 0 else 99.0
    dscr_threshold = 1.25
    dscr_headroom = dscr_actual - dscr_threshold
    dscr_cushion_pct = (dscr_headroom / dscr_threshold) * 100.0
    dscr_status = "compliant" if dscr_actual >= dscr_threshold else ("warning" if dscr_actual >= 1.10 else "breached")
    
    # 4.3 Net Debt to EBITDA
    nd_ebitda_threshold = 3.00
    nd_ebitda_headroom = nd_ebitda_threshold - net_debt_to_ebitda
    nd_ebitda_cushion_pct = (nd_ebitda_headroom / nd_ebitda_threshold) * 100.0
    nd_ebitda_status = "compliant" if net_debt_to_ebitda <= nd_ebitda_threshold else ("warning" if net_debt_to_ebitda <= 3.50 else "breached")
    
    # 4.4 Current Ratio (Current Assets / Current Liabilities)
    # Stressed current assets adjust with receivables/cash shifts
    ca_stressed = cap_struct.current_assets * (1.0 + 0.5 * (revenue_shock_pct / 100.0))
    cl_stressed = cap_struct.current_liabilities
    cr_actual = ca_stressed / cl_stressed if cl_stressed > 0 else 1.50
    cr_threshold = 1.33
    cr_headroom = cr_actual - cr_threshold
    cr_cushion_pct = (cr_headroom / cr_threshold) * 100.0
    cr_status = "compliant" if cr_actual >= cr_threshold else ("warning" if cr_actual >= 1.20 else "breached")
    
    # 4.5 TOL / TNW (Total Outside Liabilities / Tangible Net Worth)
    tol = gross_debt + cap_struct.current_liabilities
    tnw = max(1.0, cap_struct.tangible_net_worth)
    tol_tnw_actual = tol / tnw
    tol_tnw_threshold = 2.50
    tol_tnw_headroom = tol_tnw_threshold - tol_tnw_actual
    tol_tnw_cushion_pct = (tol_tnw_headroom / tol_tnw_threshold) * 100.0
    tol_tnw_status = "compliant" if tol_tnw_actual <= tol_tnw_threshold else ("warning" if tol_tnw_actual <= 2.80 else "breached")
    
    covenants = {
        "icr": CovenantRatio(
            name="Interest Coverage Ratio (ICR)",
            actual_value=float(icr_actual),
            threshold=icr_threshold,
            comparison="gte",
            unit_label="x",
            headroom=float(icr_headroom),
            cushion_pct=float(icr_cushion_pct),
            status=icr_status,
            bank_standard="≥ 2.00x (Standard Consortium Norm)",
            description="Measures operating earnings buffer against annual loan interest commitments."
        ),
        "dscr": CovenantRatio(
            name="Debt Service Coverage Ratio (DSCR)",
            actual_value=float(dscr_actual),
            threshold=dscr_threshold,
            comparison="gte",
            unit_label="x",
            headroom=float(dscr_headroom),
            cushion_pct=float(dscr_cushion_pct),
            status=dscr_status,
            bank_standard="≥ 1.25x (Term Loan Sanction Norm)",
            description="Evaluates post-tax cash availability to satisfy both interest and principal repayments."
        ),
        "nd_ebitda": CovenantRatio(
            name="Net Debt to EBITDA Multiple",
            actual_value=float(net_debt_to_ebitda),
            threshold=nd_ebitda_threshold,
            comparison="lte",
            unit_label="x",
            headroom=float(nd_ebitda_headroom),
            cushion_pct=float(nd_ebitda_cushion_pct),
            status=nd_ebitda_status,
            bank_standard="≤ 3.00x (Maximum Leverage Cap)",
            description="Total net debt burden scaled against annualized operating cash generation."
        ),
        "current_ratio": CovenantRatio(
            name="Current Ratio (Working Capital)",
            actual_value=float(cr_actual),
            threshold=cr_threshold,
            comparison="gte",
            unit_label="x",
            headroom=float(cr_headroom),
            cushion_pct=float(cr_cushion_pct),
            status=cr_status,
            bank_standard="≥ 1.33x (Tandon Committee Benchmark)",
            description="Short-term liquidity health: current asset coverage against current operating payables."
        ),
        "tol_tnw": CovenantRatio(
            name="Total Outside Liabilities to Net Worth",
            actual_value=float(tol_tnw_actual),
            threshold=tol_tnw_threshold,
            comparison="lte",
            unit_label="x",
            headroom=float(tol_tnw_headroom),
            cushion_pct=float(tol_tnw_cushion_pct),
            status=tol_tnw_status,
            bank_standard="≤ 2.50x (Prudential Gearing Ceiling)",
            description="Total enterprise indebtedness relative to shareholder equity & tangible net worth."
        ),
    }
    
    passed_count = sum(1 for c in covenants.values() if c.status == "compliant")
    all_compliant = (passed_count == len(covenants))
    
    # 5. 12-Month Liquidity Trajectory Schedule
    # Computes forward cash balance month by month
    monthly_trajectory = []
    curr_liquidity = total_liquidity
    monthly_inflow = (stressed_rev - stressed_cogs) / 12.0
    monthly_outflow = (stressed_opex + annual_finance_cost + annual_principal_repayment) / 12.0
    net_monthly = monthly_inflow - monthly_outflow
    
    min_reserve_buffer = base_rev * 0.04 # 4% minimum statutory / payroll reserve
    
    for m in range(1, 13):
        # Apply realistic seasonal working capital variation (+/- 6%)
        seasonal_factor = 1.0 + 0.06 * np.sin(m * np.pi / 6.0)
        m_net = net_monthly * seasonal_factor
        curr_liquidity = max(0.0, curr_liquidity + m_net)
        
        monthly_trajectory.append({
            "month_index": m,
            "month_label": f"M+{m}",
            "liquidity_balance": float(curr_liquidity),
            "net_cash_flow": float(m_net),
            "minimum_buffer": float(min_reserve_buffer),
            "is_above_buffer": bool(curr_liquidity >= min_reserve_buffer)
        })
        
    # 6. Debt Maturity Schedule
    # Sorted breakdown of debt by repayment timeline
    debt_schedule = []
    for inst in cap_struct.instruments:
        debt_schedule.append({
            "facility_name": inst.name,
            "category": inst.category.replace("_", " ").title(),
            "lender": inst.lender,
            "principal": float(inst.principal_outstanding),
            "interest_rate_pct": float(inst.interest_rate * 100.0),
            "is_floating": inst.is_floating,
            "annual_amortization": float(inst.annual_amortization),
            "maturity_year": inst.maturity_year
        })
        
    return CockpitMetrics(
        company_name=company_name,
        annualized_revenue=float(stressed_rev),
        annualized_ebitda=float(stressed_ebitda),
        ebitda_margin_pct=float(ebitda_margin_pct),
        gross_margin_pct=float(gross_margin_pct),
        total_liquidity=float(total_liquidity),
        monthly_operating_burn=float(monthly_net_burn),
        cash_runway_months=float(cash_runway_months),
        runway_status=runway_status,
        gross_debt=float(gross_debt),
        net_debt=float(net_debt),
        net_debt_to_ebitda=float(net_debt_to_ebitda),
        annual_finance_cost=float(annual_finance_cost),
        annual_principal_repayment=float(annual_principal_repayment),
        total_annual_debt_service=float(total_annual_debt_service),
        blended_interest_rate_pct=float(blended_interest_rate_pct),
        covenants=covenants,
        all_covenants_compliant=all_compliant,
        covenants_passed_count=passed_count,
        covenants_total_count=len(covenants),
        monthly_liquidity_trajectory=monthly_trajectory,
        debt_maturity_schedule=debt_schedule,
        applied_repo_shock_bps=repo_rate_shock_bps,
        applied_cogs_inflation_pct=cogs_inflation_pct,
        applied_revenue_shock_pct=revenue_shock_pct,
        ebitda_variance_from_shocks=float(ebitda_variance)
    )


def generate_executive_commentary(metrics: CockpitMetrics) -> str:
    """
    Synthesizes an institutional CFO briefing narrative based on calculated metrics.
    """
    runway_desc = (
        f"abundant liquidity headroom ({metrics.cash_runway_months:.1f} months runway)"
        if metrics.runway_status == "healthy"
        else (
            f"adequate operating liquidity ({metrics.cash_runway_months:.1f} months runway)"
            if metrics.runway_status == "adequate"
            else f"tight liquidity buffer ({metrics.cash_runway_months:.1f} months runway — refinancing watch)"
        )
    )
    
    cov_desc = (
        f"All {metrics.covenants_total_count} Indian banking covenants are fully compliant with healthy cushions."
        if metrics.all_covenants_compliant
        else f"Covenant alert: {metrics.covenants_passed_count} of {metrics.covenants_total_count} covenants satisfied. Vigilance required on debt service headroom."
    )
    
    icr = metrics.covenants["icr"]
    dscr = metrics.covenants["dscr"]
    
    commentary = (
        f"**{metrics.company_name}** maintains an annualized operating EBITDA run-rate of "
        f"**{metrics.ebitda_margin_pct:.1f}%** across prevailing trading conditions. "
        f"Consolidated liquid reserves stand at {runway_desc}. "
        f"With Net Debt/EBITDA at **{metrics.net_debt_to_ebitda:.2f}x**, enterprise leverage remains comfortably positioned. "
        f"The Interest Coverage Ratio (ICR) is **{icr.actual_value:.2f}x** (cushion of +{icr.cushion_pct:.1f}% above the 2.00x consortium covenant), "
        f"while Debt Service Coverage (DSCR) stands at **{dscr.actual_value:.2f}x** against the 1.25x bank benchmark. {cov_desc}"
    )
    
    if metrics.applied_repo_shock_bps != 0 or metrics.applied_cogs_inflation_pct != 0 or metrics.applied_revenue_shock_pct != 0:
        commentary += (
            f"\n\n*Under applied macro sensitivity shocks (Repo: {metrics.applied_repo_shock_bps:+.0f} bps, "
            f"COGS: {metrics.applied_cogs_inflation_pct:+.1f}%, Revenue: {metrics.applied_revenue_shock_pct:+.1f}%), "
            f"EBITDA shifts by {metrics.ebitda_variance_from_shocks:+.2f} relative to baseline.*"
        )
        
    return commentary
