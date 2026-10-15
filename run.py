"""
ARCTUS — Unified Single-Command Application Launcher.
Starts the full Arctus stack (Streamlit UI + Flask REST API) with a single command.
Usage:
    python run.py
"""

import sys
import os
import subprocess
import time
import socket
import threading
import logging

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Checks if a TCP port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def start_flask_api():
    """Starts the Flask REST API engine."""
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    from api.app import app as flask_app
    flask_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def main():
    print("=" * 64)
    print("[ARCTUS] Institutional FP&A Stress-Testing Platform")
    print("         Black & Gold Elegance | Indian Mid-Market CFOs")
    print("=" * 64)

    # 1. Initialize SQLite Database
    try:
        from core.database import init_db
        init_db()
        print("[1/3] Database: arctus.db verified & initialized.")
    except Exception as e:
        print(f"[1/3] Warning: Database check encountered: {e}")

    # 2. Start Background Flask REST API
    if not is_port_in_use(5000):
        t = threading.Thread(
            target=start_flask_api,
            daemon=True,
            name="ArctusFlaskAPIThread"
        )
        t.start()
        # Give Flask a brief moment to bind port
        time.sleep(0.5)
        print("[2/3] Backend API: Flask REST API active on http://127.0.0.1:5000")
    else:
        print("[2/3] Backend API: Port 5000 already active, reusing running service.")

    # 3. Launch Streamlit Frontend
    python_exe = sys.executable
    print("[3/3] Launching Unified Services:")
    print("   * Streamlit Web Platform:  http://localhost:8501")
    print("   * Flask REST API Backend:  http://localhost:5000")
    print("   * REST API Health Check:   http://localhost:5000/api/health")
    print("   * Macro Telemetry Feed:    http://localhost:5000/api/macro")
    print("=" * 64)
    print("Press CTRL+C at any time to shut down all Arctus services.")
    print("=" * 64)

    cmd = [
        python_exe,
        "-m", "streamlit", "run", "app.py",
        "--server.port=8501",
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[Arctus] Shutting down all services cleanly. Goodbye!")

if __name__ == "__main__":
    main()
