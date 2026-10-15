"""
SQLite Persistence Layer for Arctus.
Manages user authentication, profile settings, and scenario stress-test history.
Designed for local reliability and straightforward production swap (e.g. Supabase/Postgres).
"""

import sqlite3
import hashlib
import json
import os
import time
from typing import Optional, List, Dict, Any, Tuple
from core.models import UserAccount, FinancialStatement, Scenario, ForecastResult

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "arctus.db")


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hashes password with SHA-256 and constant salt for local build scope."""
    salt = "arctus_fpa_salt_2024"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def init_db():
    """Initializes tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        company_name TEXT NOT NULL,
        default_unit TEXT DEFAULT 'crores',
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenario_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        run_name TEXT NOT NULL,
        company_name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        periods_json TEXT NOT NULL,
        actuals_json TEXT NOT NULL,
        scenarios_json TEXT NOT NULL,
        results_summary_json TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        rev_growth REAL NOT NULL,
        cogs_inflation REAL NOT NULL,
        opex_inflation REAL NOT NULL,
        macro_shock REAL NOT NULL,
        color TEXT NOT NULL,
        description TEXT,
        probability_weight REAL DEFAULT 0.0,
        is_preset INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit()
    conn.close()


# Automatically initialize DB on import
init_db()


def create_user(
    email: str,
    password: str,
    name: str,
    company_name: str,
    default_unit: str = "crores"
) -> Tuple[bool, str, Optional[UserAccount]]:
    """Creates a new user account."""
    clean_email = email.lower().strip()
    if not clean_email or "@" not in clean_email:
        return False, "Please enter a valid business email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters.", None

    conn = get_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(password)
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, name, company_name, default_unit, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (clean_email, pw_hash, name.strip(), company_name.strip(), default_unit, created_at)
        )
        conn.commit()
        user_id = cursor.lastrowid
        user = UserAccount(
            id=user_id,
            email=clean_email,
            name=name.strip(),
            company_name=company_name.strip(),
            default_unit=default_unit,
            created_at=created_at
        )
        return True, "Account created successfully.", user
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists.", None
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[UserAccount]]:
    """Authenticates credentials against the users table."""
    clean_email = email.lower().strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (clean_email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "No account found with this email.", None

    if row["password_hash"] != hash_password(password):
        return False, "Incorrect password. Please try again.", None

    user = UserAccount(
        id=row["id"],
        email=row["email"],
        name=row["name"],
        company_name=row["company_name"],
        default_unit=row["default_unit"] or "crores",
        created_at=row["created_at"]
    )
    return True, "Logged in successfully.", user


def update_user_profile(user_id: int, company_name: str, default_unit: str) -> bool:
    """Updates user company and preferred unit settings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET company_name = ?, default_unit = ? WHERE id = ?",
        (company_name.strip(), default_unit, user_id)
    )
    conn.commit()
    conn.close()
    return True


def save_scenario_run(
    user_id: Optional[int],
    run_name: str,
    company_name: str,
    statement: FinancialStatement,
    scenarios: List[Scenario],
    results: Dict[str, ForecastResult]
) -> int:
    """Persists a full scenario run and its summary metrics."""
    conn = get_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    # Serialize results summary
    summary = {}
    for sc_name, res in results.items():
        summary[sc_name] = {
            "loss_probability": res.loss_probability,
            "annual_revenue": float(sum(res.point_forecast["revenue"])),
            "annual_ebitda": float(sum(res.point_forecast["ebitda"])),
            "p10_ebitda": float(sum(res.confidence_bands["ebitda"]["p10"])),
            "p90_ebitda": float(sum(res.confidence_bands["ebitda"]["p90"])),
            "fwd_periods": res.forecast_periods,
        }

    cursor.execute(
        """
        INSERT INTO scenario_runs (
            user_id, run_name, company_name, timestamp,
            periods_json, actuals_json, scenarios_json, results_summary_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            run_name.strip() or f"Run {ts}",
            company_name.strip(),
            ts,
            json.dumps(statement.periods),
            json.dumps(statement.to_dict()),
            json.dumps([s.to_dict() for s in scenarios]),
            json.dumps(summary),
        )
    )
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id


def get_scenario_runs(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieves list of past scenario runs for user or global."""
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM scenario_runs WHERE user_id = ? ORDER BY id DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM scenario_runs ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    runs = []
    for r in rows:
        runs.append({
            "id": r["id"],
            "run_name": r["run_name"],
            "company_name": r["company_name"],
            "timestamp": r["timestamp"],
            "periods": json.loads(r["periods_json"]),
            "actuals": json.loads(r["actuals_json"]),
            "scenarios": json.loads(r["scenarios_json"]),
            "summary": json.loads(r["results_summary_json"]),
        })
    return runs


def get_scenario_run_by_id(run_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single scenario run by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scenario_runs WHERE id = ?", (run_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r["id"],
        "run_name": r["run_name"],
        "company_name": r["company_name"],
        "timestamp": r["timestamp"],
        "periods": json.loads(r["periods_json"]),
        "actuals": json.loads(r["actuals_json"]),
        "scenarios": json.loads(r["scenarios_json"]),
        "summary": json.loads(r["results_summary_json"]),
    }


def delete_scenario_run(run_id: int) -> bool:
    """Deletes a scenario run by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scenario_runs WHERE id = ?", (run_id,))
    conn.commit()
    conn.close()
    return True


# -----------------------------------------------------------------------------
# Custom Scenarios CRUD
# -----------------------------------------------------------------------------
def save_custom_scenario(
    user_id: Optional[int],
    name: str,
    rev_growth: float,
    cogs_inflation: float,
    opex_inflation: float,
    macro_shock: float,
    color: str,
    description: str = "",
    probability_weight: float = 0.0,
    is_preset: bool = False
) -> int:
    """Saves or updates a custom scenario."""
    conn = get_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO custom_scenarios (
            user_id, name, rev_growth, cogs_inflation, opex_inflation,
            macro_shock, color, description, probability_weight, is_preset, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id, name.strip(), float(rev_growth), float(cogs_inflation),
            float(opex_inflation), float(macro_shock), str(color),
            str(description), float(probability_weight), 1 if is_preset else 0, ts
        )
    )
    conn.commit()
    scenario_id = cursor.lastrowid
    conn.close()
    return scenario_id


def get_custom_scenarios(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieves all custom scenarios for user or global."""
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM custom_scenarios WHERE user_id = ? OR is_preset = 1 ORDER BY id ASC", (user_id,))
    else:
        cursor.execute("SELECT * FROM custom_scenarios ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    scenarios = []
    for r in rows:
        scenarios.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "name": r["name"],
            "rev_growth": r["rev_growth"],
            "cogs_inflation": r["cogs_inflation"],
            "opex_inflation": r["opex_inflation"],
            "macro_shock": r["macro_shock"],
            "color": r["color"],
            "description": r["description"],
            "probability_weight": r["probability_weight"],
            "is_preset": bool(r["is_preset"]),
            "created_at": r["created_at"],
        })
    return scenarios


def delete_custom_scenario(scenario_id: int) -> bool:
    """Deletes a custom scenario by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_scenarios WHERE id = ?", (scenario_id,))
    conn.commit()
    conn.close()
    return True

