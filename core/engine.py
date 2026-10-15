"""
ForecastEngine - High-Performance Vectorized Financial Forecasting & Monte Carlo Simulation.
Generates 4-quarter forward projections across defined macroeconomic scenarios, simulates
1,000 randomized Monte Carlo iterations per scenario, computes statistical confidence intervals,
and executes tornado sensitivity analysis.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from core.models import FinancialStatement, Scenario, ForecastResult


class ForecastEngine:
    """
    Quantitative FP&A forecasting engine using vectorized NumPy array operations.
    """

    DEFAULT_ITERATIONS = 1000
    TAX_RATE = 0.25  # 25% Indian corporate tax rate for domestic mid-market firms

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.rng = np.random.default_rng(seed=self.random_seed)

    @staticmethod
    def generate_forward_periods(last_period: str, num_quarters: int = 4) -> List[str]:
        """
        Generates subsequent quarter labels starting after last_period.
        E.g. 'Q4 FY24' -> ['Q1 FY25', 'Q2 FY25', 'Q3 FY25', 'Q4 FY25']
        """
        from core.validator import ValidationLayer
        qk = ValidationLayer.parse_quarter_key(last_period)
        if not qk:
            return [f"Q{i+1} Fwd" for i in range(num_quarters)]

        yr, q = qk
        forward_labels = []
        for _ in range(num_quarters):
            q += 1
            if q > 4:
                q = 1
                yr += 1
            forward_labels.append(f"Q{q} FY{yr % 100:02d}")
        return forward_labels

    def _compute_point_forecast(
        self,
        stmt: FinancialStatement,
        scenario: Scenario,
        num_quarters: int = 4
    ) -> Dict[str, np.ndarray]:
        """
        Computes deterministic baseline 4-quarter projection for a scenario.
        """
        # Historical baseline references (last 4 quarters or whatever is available)
        n_hist = min(4, len(stmt.periods))
        hist_rev = stmt.revenue[-n_hist:]
        hist_cogs = stmt.cogs[-n_hist:]
        hist_opex = stmt.opex[-n_hist:]

        base_rev_quarter = float(np.mean(hist_rev))
        cogs_ratio = float(np.sum(hist_cogs) / np.sum(hist_rev)) if np.sum(hist_rev) > 0 else 0.60
        opex_ratio = float(np.sum(hist_opex) / np.sum(hist_rev)) if np.sum(hist_rev) > 0 else 0.25

        q_indices = np.arange(1, num_quarters + 1)

        # Revenue projection: quarterly compounding of revenue growth
        q_growth = scenario.rev_growth / 4.0
        proj_rev = base_rev_quarter * (1.0 + q_growth) ** q_indices

        # COGS projection: adjusted by cost inflation
        q_cogs_inf = scenario.cogs_inflation / 4.0
        proj_cogs = (proj_rev * cogs_ratio) * (1.0 + q_cogs_inf) ** q_indices

        # Gross Profit
        proj_gp = proj_rev - proj_cogs

        # OPEX projection: adjusted by opex inflation and macro shock
        q_opex_inf = scenario.opex_inflation / 4.0
        macro_overhead_multiplier = (scenario.macro_shock ** 0.5)
        base_opex_quarter = base_rev_quarter * opex_ratio
        proj_opex = base_opex_quarter * ((1.0 + q_opex_inf) ** q_indices) * macro_overhead_multiplier

        # EBITDA
        proj_ebitda = proj_gp - proj_opex

        # PBT: EBITDA minus estimated financing costs & depreciation (scaled by macro shock)
        fin_deprec = np.maximum(0.0, proj_ebitda * 0.15 * scenario.macro_shock)
        proj_pbt = proj_ebitda - fin_deprec

        # PAT: PBT after tax
        proj_pat = np.where(proj_pbt > 0, proj_pbt * (1.0 - self.TAX_RATE), proj_pbt)

        return {
            "revenue": proj_rev,
            "cogs": proj_cogs,
            "gross_profit": proj_gp,
            "opex": proj_opex,
            "ebitda": proj_ebitda,
            "pbt": proj_pbt,
            "pat": proj_pat,
        }

    def _run_monte_carlo(
        self,
        stmt: FinancialStatement,
        scenario: Scenario,
        iterations: int = 1000,
        num_quarters: int = 4
    ) -> Dict[str, np.ndarray]:
        """
        Runs vectorized Monte Carlo simulation with random perturbations around assumptions.
        Returns matrices of shape (iterations, num_quarters) for each line item.
        """
        n_hist = min(4, len(stmt.periods))
        hist_rev = stmt.revenue[-n_hist:]
        hist_cogs = stmt.cogs[-n_hist:]
        hist_opex = stmt.opex[-n_hist:]

        base_rev = float(np.mean(hist_rev))
        cogs_ratio = float(np.sum(hist_cogs) / np.sum(hist_rev)) if np.sum(hist_rev) > 0 else 0.60
        opex_ratio = float(np.sum(hist_opex) / np.sum(hist_rev)) if np.sum(hist_rev) > 0 else 0.25

        q_indices = np.arange(1, num_quarters + 1).reshape(1, num_quarters)  # shape (1, 4)

        # Vectorized random perturbation draws (iterations, 1)
        # Revenue growth standard dev ~3.5%
        rev_growth_sim = self.rng.normal(
            loc=scenario.rev_growth,
            scale=0.035,
            size=(iterations, 1)
        )
        # COGS inflation standard dev ~2.5%
        cogs_inf_sim = self.rng.normal(
            loc=scenario.cogs_inflation,
            scale=0.025,
            size=(iterations, 1)
        )
        # OPEX inflation standard dev ~2.0%
        opex_inf_sim = self.rng.normal(
            loc=scenario.opex_inflation,
            scale=0.020,
            size=(iterations, 1)
        )
        # Macro shock multiplier lognormal perturbation
        shock_sim = self.rng.lognormal(
            mean=np.log(max(0.7, scenario.macro_shock)),
            sigma=0.06,
            size=(iterations, 1)
        )

        # Shape (iterations, num_quarters)
        q_growth_mat = rev_growth_sim / 4.0
        sim_rev = base_rev * (1.0 + q_growth_mat) ** q_indices

        q_cogs_mat = cogs_inf_sim / 4.0
        sim_cogs = (sim_rev * cogs_ratio) * (1.0 + q_cogs_mat) ** q_indices
        sim_gp = sim_rev - sim_cogs

        q_opex_mat = opex_inf_sim / 4.0
        base_opex_quarter = base_rev * opex_ratio
        sim_opex = base_opex_quarter * ((1.0 + q_opex_mat) ** q_indices) * (shock_sim ** 0.5)

        sim_ebitda = sim_gp - sim_opex
        fin_deprec = np.maximum(0.0, sim_ebitda * 0.15 * shock_sim)
        sim_pbt = sim_ebitda - fin_deprec
        sim_pat = np.where(sim_pbt > 0, sim_pbt * (1.0 - self.TAX_RATE), sim_pbt)

        return {
            "revenue": sim_rev,
            "cogs": sim_cogs,
            "gross_profit": sim_gp,
            "opex": sim_opex,
            "ebitda": sim_ebitda,
            "pbt": sim_pbt,
            "pat": sim_pat,
        }

    def _calculate_confidence_bands(
        self,
        mc_runs: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Computes percentiles (10%, 25%, 50%, 75%, 90%) and mean/std across simulation runs.
        """
        bands = {}
        for metric, mat in mc_runs.items():
            bands[metric] = {
                "p10": np.percentile(mat, 10, axis=0),
                "p25": np.percentile(mat, 25, axis=0),
                "median": np.percentile(mat, 50, axis=0),
                "mean": np.mean(mat, axis=0),
                "p75": np.percentile(mat, 75, axis=0),
                "p90": np.percentile(mat, 90, axis=0),
                "std": np.std(mat, axis=0),
            }
        return bands

    def compute_sensitivity_analysis(
        self,
        stmt: FinancialStatement,
        scenario: Scenario,
        delta_pct: float = 0.10
    ) -> List[Dict[str, Any]]:
        """
        Calculates tornado chart sensitivity rankings by perturbing each assumption by ±10%.
        Measures swing in cumulative 4-quarter EBITDA.
        """
        base_pts = self._compute_point_forecast(stmt, scenario)
        base_annual_ebitda = float(np.sum(base_pts["ebitda"]))

        parameters = [
            ("Revenue Growth", "rev_growth", scenario.rev_growth, True),
            ("COGS Inflation", "cogs_inflation", scenario.cogs_inflation, False),
            ("OPEX Inflation", "opex_inflation", scenario.opex_inflation, False),
            ("Macro Shock Multiplier", "macro_shock", scenario.macro_shock, False),
        ]

        results = []
        for label, attr_name, val, is_higher_better in parameters:
            # Downside perturbation
            down_val = val * (1.0 - delta_pct) if val != 0 else -0.02
            # Upside perturbation
            up_val = val * (1.0 + delta_pct) if val != 0 else 0.02

            # Downside scenario run
            s_down = Scenario(
                name=f"{scenario.name}_down",
                rev_growth=down_val if attr_name == "rev_growth" else scenario.rev_growth,
                cogs_inflation=down_val if attr_name == "cogs_inflation" else scenario.cogs_inflation,
                opex_inflation=down_val if attr_name == "opex_inflation" else scenario.opex_inflation,
                macro_shock=down_val if attr_name == "macro_shock" else scenario.macro_shock,
            )
            ebitda_down = float(np.sum(self._compute_point_forecast(stmt, s_down)["ebitda"]))

            # Upside scenario run
            s_up = Scenario(
                name=f"{scenario.name}_up",
                rev_growth=up_val if attr_name == "rev_growth" else scenario.rev_growth,
                cogs_inflation=up_val if attr_name == "cogs_inflation" else scenario.cogs_inflation,
                opex_inflation=up_val if attr_name == "opex_inflation" else scenario.opex_inflation,
                macro_shock=up_val if attr_name == "macro_shock" else scenario.macro_shock,
            )
            ebitda_up = float(np.sum(self._compute_point_forecast(stmt, s_up)["ebitda"]))

            # Calculate relative swing
            min_e = min(ebitda_down, ebitda_up)
            max_e = max(ebitda_down, ebitda_up)
            swing = abs(max_e - min_e)
            swing_pct = (swing / abs(base_annual_ebitda) * 100) if base_annual_ebitda != 0 else 0.0

            results.append({
                "parameter": label,
                "base_ebitda": base_annual_ebitda,
                "low_ebitda": min_e,
                "high_ebitda": max_e,
                "swing": swing,
                "swing_pct": round(swing_pct, 1),
                "downside_impact": min_e - base_annual_ebitda,
                "upside_impact": max_e - base_annual_ebitda,
            })

        # Sort descending by impact swing
        results.sort(key=lambda x: x["swing"], reverse=True)
        return results

    def run_forecast(
        self,
        stmt: FinancialStatement,
        scenarios: List[Scenario],
        iterations: int = DEFAULT_ITERATIONS,
        num_quarters: int = 4
    ) -> Dict[str, ForecastResult]:
        """
        Executes forecasting and Monte Carlo simulation for up to 3 scenarios.
        Returns dictionary mapping scenario_name -> ForecastResult.
        """
        last_period = stmt.periods[-1]
        fwd_periods = self.generate_forward_periods(last_period, num_quarters=num_quarters)

        results: Dict[str, ForecastResult] = {}

        for sc in scenarios:
            pts = self._compute_point_forecast(stmt, sc, num_quarters=num_quarters)
            mc = self._run_monte_carlo(stmt, sc, iterations=iterations, num_quarters=num_quarters)
            bands = self._calculate_confidence_bands(mc)

            # Cumulative forward EBITDA across the 4 quarters for each simulation run
            annual_mc_ebitda = np.sum(mc["ebitda"], axis=1)
            loss_prob = float(np.mean(annual_mc_ebitda < 0)) * 100.0

            # Sensitivity tornado analysis
            tornado = self.compute_sensitivity_analysis(stmt, sc)

            results[sc.name] = ForecastResult(
                scenario=sc,
                forecast_periods=fwd_periods,
                point_forecast=pts,
                monte_carlo_runs=mc,
                confidence_bands=bands,
                loss_probability=loss_prob,
                tornado_sensitivities=tornado,
            )

        return results

    def compute_blended_forecast(
        self,
        results: Dict[str, ForecastResult],
        weights: Optional[Dict[str, float]] = None
    ) -> Optional[ForecastResult]:
        """
        Computes a probability-weighted blended forecast across active scenarios.
        If weights is None, extracts probability_weight from scenario models.
        Normalizes weights to sum to 1.0.
        """
        if not results:
            return None

        # Build raw weight map
        raw_weights = {}
        for sc_name, res in results.items():
            if weights and sc_name in weights:
                w = float(weights[sc_name])
            else:
                w = float(getattr(res.scenario, "probability_weight", 0.0))
            if w > 0:
                raw_weights[sc_name] = w

        # Fallback: equal weighting if no positive weights provided
        if not raw_weights:
            eq_w = 1.0 / len(results)
            raw_weights = {name: eq_w for name in results}

        total_weight = sum(raw_weights.values())
        norm_weights = {k: v / total_weight for k, v in raw_weights.items()}

        first_res = next(iter(results.values()))
        fwd_periods = first_res.forecast_periods
        metrics = list(first_res.point_forecast.keys())

        # Blend point forecasts
        blended_pts: Dict[str, np.ndarray] = {
            m: np.zeros_like(first_res.point_forecast[m], dtype=np.float64) for m in metrics
        }
        for sc_name, w in norm_weights.items():
            res = results[sc_name]
            for m in metrics:
                blended_pts[m] += res.point_forecast[m] * w

        # Blend Monte Carlo runs (weighted sample mixture)
        # Sample proportionally to weights from each scenario's iterations
        total_mc_samples = next(iter(results.values())).monte_carlo_runs[metrics[0]].shape[0]
        blended_mc: Dict[str, np.ndarray] = {m: [] for m in metrics}

        for sc_name, w in norm_weights.items():
            num_samples = int(round(w * total_mc_samples))
            if num_samples <= 0:
                continue
            sc_mc = results[sc_name].monte_carlo_runs
            # Subsample random indices
            indices = self.rng.choice(total_mc_samples, size=num_samples, replace=True)
            for m in metrics:
                blended_mc[m].append(sc_mc[m][indices])

        # Stack into final matrix shape (N, quarters)
        final_mc: Dict[str, np.ndarray] = {}
        for m in metrics:
            if blended_mc[m]:
                stacked = np.vstack(blended_mc[m])
                # Ensure exact count matches total_mc_samples
                if stacked.shape[0] < total_mc_samples:
                    diff = total_mc_samples - stacked.shape[0]
                    stacked = np.vstack([stacked, stacked[:diff]])
                elif stacked.shape[0] > total_mc_samples:
                    stacked = stacked[:total_mc_samples]
                final_mc[m] = stacked
            else:
                final_mc[m] = first_res.monte_carlo_runs[m]

        bands = self._calculate_confidence_bands(final_mc)

        # Cumulative forward EBITDA across the 4 quarters for each simulation run
        annual_mc_ebitda = np.sum(final_mc["ebitda"], axis=1)
        loss_prob = float(np.mean(annual_mc_ebitda < 0)) * 100.0

        # Construct synthetic blended Scenario definition
        blended_scenario = Scenario(
            name="Blended Probability Weighted",
            rev_growth=sum(results[sc].scenario.rev_growth * w for sc, w in norm_weights.items()),
            cogs_inflation=sum(results[sc].scenario.cogs_inflation * w for sc, w in norm_weights.items()),
            opex_inflation=sum(results[sc].scenario.opex_inflation * w for sc, w in norm_weights.items()),
            macro_shock=sum(results[sc].scenario.macro_shock * w for sc, w in norm_weights.items()),
            color="#B49A5A",
            description=f"Weighted composite: " + ", ".join(f"{sc} ({w*100:.0f}%)" for sc, w in norm_weights.items()),
            probability_weight=1.0,
        )

        return ForecastResult(
            scenario=blended_scenario,
            forecast_periods=fwd_periods,
            point_forecast=blended_pts,
            monte_carlo_runs=final_mc,
            confidence_bands=bands,
            loss_probability=loss_prob,
            tornado_sensitivities=[],
        )

