"""
Flask REST API for Arctus FP&A Stress-Testing Engine.
Exposes the core forecasting and Monte Carlo simulation engine programmatically
with input validation, CORS support, and comprehensive JSON responses.
"""

import sys
import os

# Ensure parent directory is in sys.path when running api directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

from core.models import FinancialStatement, Scenario, ForecastResult
from core.engine import ForecastEngine
from core.macro import MacroDataFetcher
from core.validator import ValidationLayer

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for Streamlit or external ERPs


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check heartbeat endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Arctus Forecasting Engine API",
        "version": "1.0.0"
    }), 200


@app.route("/api/macro", methods=["GET"])
def get_macro_indicators():
    """Returns current live/benchmark Indian macroeconomic indicators."""
    fetcher = MacroDataFetcher()
    data = fetcher.fetch_live_macro()
    return jsonify({
        "status": "success",
        "macro_telemetry": data
    }), 200


@app.route("/api/forecast", methods=["POST"])
def run_forecast_api():
    """
    POST /api/forecast
    Executes forward projection and Monte Carlo simulation for provided P&L and scenarios.

    Expected JSON body:
    {
        "statement": {
            "periods": ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"],
            "revenue": [125000000.0, 132000000.0, ...],
            "cogs": [...],
            "gross_profit": [...],
            "opex": [...],
            "ebitda": [...],
            "pbt": [...],
            "pat": [...]
        },
        "scenarios": [
            {
                "name": "Base",
                "rev_growth": 0.08,
                "cogs_inflation": 0.045,
                "opex_inflation": 0.05,
                "macro_shock": 1.0
            }
        ],
        "iterations": 1000,
        "num_quarters": 4
    }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({
            "status": "error",
            "message": "Invalid or missing JSON payload in request body."
        }), 400

    if "statement" not in body or not isinstance(body["statement"], dict):
        return jsonify({
            "status": "error",
            "message": "Missing required 'statement' dictionary in request."
        }), 422

    stmt_dict = body["statement"]
    required_keys = ["periods", "revenue"]
    for k in required_keys:
        if k not in stmt_dict or not stmt_dict[k]:
            return jsonify({
                "status": "error",
                "message": f"Statement missing required field '{k}'."
            }), 422

    periods = list(stmt_dict["periods"])
    n = len(periods)
    if n < 1:
        return jsonify({
            "status": "error",
            "message": "At least one historical period is required in 'periods'."
        }), 422

    try:
        rev = np.array(stmt_dict["revenue"], dtype=np.float64)
        cogs = np.array(stmt_dict.get("cogs", rev * 0.6), dtype=np.float64)
        gp = np.array(stmt_dict.get("gross_profit", rev - cogs), dtype=np.float64)
        opex = np.array(stmt_dict.get("opex", gp * 0.65), dtype=np.float64)
        ebitda = np.array(stmt_dict.get("ebitda", gp - opex), dtype=np.float64)
        pbt = np.array(stmt_dict.get("pbt", ebitda * 0.8), dtype=np.float64)
        pat = np.array(stmt_dict.get("pat", pbt * 0.75), dtype=np.float64)

        stmt = FinancialStatement(
            periods=periods,
            revenue=rev,
            cogs=cogs,
            gross_profit=gp,
            opex=opex,
            ebitda=ebitda,
            pbt=pbt,
            pat=pat
        )
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to construct FinancialStatement: {str(e)}"
        }), 422

    # Parse Scenarios
    scenarios_data = body.get("scenarios", [])
    if not scenarios_data:
        # Default Base scenario if none provided
        scenarios = [Scenario(name="Base", rev_growth=0.08, cogs_inflation=0.048, opex_inflation=0.055, macro_shock=1.0)]
    else:
        scenarios = []
        for s in scenarios_data:
            try:
                scenarios.append(Scenario.from_dict(s))
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid scenario definition for '{s.get('name', 'Unknown')}': {str(e)}"
                }), 422

    iterations = int(body.get("iterations", 1000))
    num_quarters = int(body.get("num_quarters", 4))

    # Execute Engine
    engine = ForecastEngine(random_seed=body.get("seed", 42))
    try:
        forecast_results = engine.run_forecast(
            stmt=stmt,
            scenarios=scenarios,
            iterations=iterations,
            num_quarters=num_quarters
        )
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Simulation engine failed: {str(e)}"
        }), 500

    # Format JSON response
    response_results = {}
    fwd_periods = []
    for sc_name, res in forecast_results.items():
        fwd_periods = res.forecast_periods
        response_results[sc_name] = {
            "annual_revenue": float(np.sum(res.point_forecast["revenue"])),
            "annual_ebitda": float(np.sum(res.point_forecast["ebitda"])),
            "loss_probability": res.loss_probability,
            "p10_ebitda": float(np.sum(res.confidence_bands["ebitda"]["p10"])),
            "p90_ebitda": float(np.sum(res.confidence_bands["ebitda"]["p90"])),
            "quarterly_ebitda_median": res.confidence_bands["ebitda"]["median"].tolist(),
            "quarterly_revenue_median": res.confidence_bands["revenue"]["median"].tolist(),
            "point_forecast": {k: v.tolist() for k, v in res.point_forecast.items()},
            "tornado_sensitivities": res.tornado_sensitivities,
        }

    return jsonify({
        "status": "success",
        "forecast_periods": fwd_periods,
        "iterations_simulated": iterations,
        "results": response_results
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Arctus REST API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
