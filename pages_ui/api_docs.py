"""
API Documentation View for Arctus.
Developer- and CFO-grade in-app API documentation styled like modern developer portals (Stripe/Redoc).
Documents the Flask REST API endpoint POST /api/forecast with parameters, cURL, Python, and JS snippets.
"""

import json
import streamlit as st
from core.theme import ACCENT_GOLD, SURFACE_CARD, BORDER_COLOR, BORDER_COLOR_GOLD


def render_api_docs_page():
    """
    Renders interactive in-app API documentation.
    """
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: inline-block; background: rgba(252, 163, 17, 0.12); color: {ACCENT_GOLD}; border: 1px solid {BORDER_COLOR_GOLD}; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;">
                Developer Hub
            </div>
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; margin-bottom: 4px;">
                Arctus REST API Reference
            </h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">
                Programmatically call the Arctus Monte Carlo forecasting engine from external ERPs (SAP, Tally, Zoho Books) or internal FP&A scripts.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check live background API status
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_api_online = sock.connect_ex(("127.0.0.1", 5000)) == 0
    sock.close()

    status_badge = (
        '<span style="background: rgba(122,155,118,0.18); color: #7A9B76; border: 1px solid #7A9B76; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 700;">● ONLINE (PORT 5000)</span>'
        if is_api_online else
        '<span style="background: rgba(252,163,17,0.18); color: #FCA311; border: 1px solid #FCA311; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 700;">● INITIALIZING</span>'
    )

    # Overview endpoint badge
    st.markdown(
        f"""
        <div style="
            background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 12px;
            padding: 16px 20px; margin-bottom: 24px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
        ">
            <span style="
                background: {ACCENT_GOLD}; color: #000000; font-weight: 800; font-size: 0.85rem;
                padding: 4px 10px; border-radius: 4px; font-family: monospace;
            ">POST</span>
            <span style="font-family: monospace; font-size: 1.05rem; color: #FFFFFF; font-weight: 600;">
                /api/forecast
            </span>
            <div style="margin-left: auto; display: flex; align-items: center; gap: 14px;">
                {status_badge}
                <span style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">
                    Base URL: <code>http://localhost:5000</code>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_overview, tab_curl, tab_python, tab_js, tab_live = st.tabs([
        "📖 Request & Response Schema",
        "💻 cURL",
        "🐍 Python Requests",
        "⚡ JavaScript / Fetch",
        "🚀 Live Test Console",
    ])

    sample_request = {
        "statement": {
            "periods": ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24"],
            "revenue": [125000000.0, 132000000.0, 139000000.0, 148000000.0],
            "cogs": [75000000.0, 79200000.0, 83400000.0, 88800000.0],
            "gross_profit": [50000000.0, 52800000.0, 55600000.0, 59200000.0],
            "opex": [29000000.0, 30500000.0, 32000000.0, 34000000.0],
            "ebitda": [21000000.0, 22300000.0, 23600000.0, 25200000.0],
            "pbt": [15000000.0, 16000000.0, 17000000.0, 18200000.0],
            "pat": [11250000.0, 12000000.0, 12750000.0, 13650000.0]
        },
        "scenarios": [
            {
                "name": "Recession",
                "rev_growth": -0.05,
                "cogs_inflation": 0.08,
                "opex_inflation": 0.06,
                "macro_shock": 1.20
            },
            {
                "name": "Base",
                "rev_growth": 0.08,
                "cogs_inflation": 0.048,
                "opex_inflation": 0.055,
                "macro_shock": 1.00
            }
        ],
        "iterations": 1000,
        "num_quarters": 4
    }

    sample_response = {
        "status": "success",
        "forecast_periods": ["Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25"],
        "results": {
            "Base": {
                "annual_revenue": 605200000.0,
                "annual_ebitda": 102400000.0,
                "loss_probability": 0.0,
                "p10_ebitda": 89500000.0,
                "p90_ebitda": 115200000.0,
                "quarterly_ebitda_median": [24500000.0, 25200000.0, 26000000.0, 26700000.0]
            }
        },
        "macro_benchmarks": {
            "rbi_repo_rate": 6.50,
            "cpi_inflation": 4.85
        }
    }

    with tab_overview:
        col_req, col_res = st.columns(2)
        with col_req:
            st.markdown("#### Sample Request Body (JSON)")
            st.code(json.dumps(sample_request, indent=2), language="json")
        with col_res:
            st.markdown("#### Sample Response Body (JSON, HTTP 200)")
            st.code(json.dumps(sample_response, indent=2), language="json")

    with tab_curl:
        curl_cmd = f"""curl -X POST "http://localhost:5000/api/forecast" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(sample_request)}'"""
        st.code(curl_cmd, language="bash")

    with tab_python:
        python_code = f"""import requests

url = "http://localhost:5000/api/forecast"
payload = {json.dumps(sample_request, indent=4)}

response = requests.post(url, json=payload)
data = response.json()

print(f"Status: {{response.status_code}}")
print(f"Base FY EBITDA: ₹{{data['results']['Base']['annual_ebitda']:,.2f}}")
print(f"Recession Loss Probability: {{data['results']['Base']['loss_probability']}}%")"""
        st.code(python_code, language="python")

    with tab_js:
        js_code = f"""const response = await fetch('http://localhost:5000/api/forecast', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/json' }},
  body: JSON.stringify({json.dumps(sample_request, indent=2)})
}});

const result = await response.json();
console.log('Arctus Forecast:', result);"""
        st.code(js_code, language="javascript")

    with tab_live:
        st.markdown("#### ⚡ Live API Test Runner")
        st.markdown(
            "Execute a real, live HTTP request against the embedded Arctus REST API on `http://localhost:5000` to verify latency and payload structure."
        )

        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🚀 Send POST /api/forecast", use_container_width=True):
                import requests
                try:
                    res = requests.post("http://127.0.0.1:5000/api/forecast", json=sample_request, timeout=8)
                    st.success(f"HTTP {res.status_code} OK (Response received in background)")
                    st.json(res.json())
                except Exception as e:
                    st.error(f"Failed to reach API server: {e}")

        with col_act2:
            if st.button("📡 Send GET /api/macro", use_container_width=True):
                import requests
                try:
                    res = requests.get("http://127.0.0.1:5000/api/macro", timeout=5)
                    st.success(f"HTTP {res.status_code} OK (Macro Telemetry Live)")
                    st.json(res.json())
                except Exception as e:
                    st.error(f"Failed to reach API server: {e}")

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("### Additional Endpoints")
    st.markdown(
        f"""
        <div style="background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
            <code style="color: {ACCENT_GOLD}; font-weight: 700;">GET /api/macro</code> — Returns live Indian macroeconomic benchmark indicators (RBI repo, CPI, crude).
        </div>
        <div style="background: {SURFACE_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 12px 16px;">
            <code style="color: {ACCENT_GOLD}; font-weight: 700;">GET /api/health</code> — Health check and uptime heartbeat.
        </div>
        """,
        unsafe_allow_html=True
    )
