"""
Integration tests for Arctus Flask REST API.
Tests /api/health, /api/macro, and /api/forecast endpoints using Flask test client.
"""

import pytest
import json
from api.app import app


@pytest.fixture
def client():
    """Creates Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_health(client):
    """Verify health endpoint."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"


def test_api_macro(client):
    """Verify macro telemetry endpoint."""
    res = client.get("/api/macro")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "rbi_repo_rate" in data["macro_telemetry"]


def test_api_forecast_success(client):
    """Verify POST /api/forecast returns structured forecast results."""
    payload = {
        "statement": {
            "periods": ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"],
            "revenue": [100.0, 105.0, 110.0, 115.0],
            "cogs": [60.0, 63.0, 66.0, 69.0],
            "gross_profit": [40.0, 42.0, 44.0, 46.0],
            "opex": [20.0, 21.0, 22.0, 23.0],
            "ebitda": [20.0, 21.0, 22.0, 23.0],
            "pbt": [15.0, 15.5, 16.0, 16.5],
            "pat": [11.25, 11.6, 12.0, 12.4]
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
        "iterations": 100,
        "num_quarters": 4
    }

    res = client.post(
        "/api/forecast",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "forecast_periods" in data
    assert len(data["forecast_periods"]) == 4
    assert "Base" in data["results"]
    assert "annual_ebitda" in data["results"]["Base"]
    assert "tornado_sensitivities" in data["results"]["Base"]


def test_api_forecast_validation_error(client):
    """Verify 422 error on invalid payload."""
    res = client.post(
        "/api/forecast",
        data=json.dumps({"invalid": "data"}),
        content_type="application/json"
    )
    assert res.status_code == 422
