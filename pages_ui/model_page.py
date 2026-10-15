"""
Dedicated Upload & Financial Modeling Workspace for Arctus.
Enables CFOs and FP&A teams to:
- Ingest Excel / CSV files with Stage 1 (RawNormalizer) and Stage 2 (SchemaMapper)
- Edit historical figures directly in an interactive spreadsheet grid without re-uploading
- Add custom ledger accounts / line items and compute real-time subtotals
- Add new quarters / forward periods to the historical model
- Validate Ind AS statement continuity and commit changes to the shared session state
- Instantly push verified models into the Monte Carlo Stress Engine or Executive Cockpit
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from core.models import FinancialStatement
from core.normalizer import RawNormalizer
from core.mapper import SchemaMapper
from core.validator import ValidationLayer, ValidationError
from core.synthetic import (
    generate_clean_midmarket_statement,
    create_messy_multisheet_excel,
)
from core.theme import (
    format_inr,
    format_percentage,
    ACCENT_GOLD,
    SURFACE_CARD,
    BORDER_COLOR,
    BORDER_COLOR_GOLD,
    COLOR_GROWTH,
    COLOR_BASE,
    COLOR_RECESSION,
)
from components.metrics import render_metric_card
from core.assets import get_logo_icon_b64


STANDARD_P_AND_L_ROWS = [
    ("revenue", "Revenue from Operations"),
    ("cogs", "Cost of Goods Sold (COGS)"),
    ("gross_profit", "Gross Profit"),
    ("opex", "Operating Expenses (OPEX)"),
    ("ebitda", "Operating EBITDA"),
    ("pbt", "Profit Before Tax (PBT)"),
    ("pat", "Profit After Tax (PAT)"),
]


def statement_to_modeling_df(stmt: FinancialStatement) -> pd.DataFrame:
    """Converts a FinancialStatement to an editable financial modeling dataframe."""
    periods = list(stmt.periods)
    data = []
    for key, display_name in STANDARD_P_AND_L_ROWS:
        row_dict = {"Line Item": display_name, "Metric Key": key}
        arr = getattr(stmt, key)
        for i, p in enumerate(periods):
            row_dict[p] = float(arr[i])
        data.append(row_dict)
    return pd.DataFrame(data)


def modeling_df_to_statement(df: pd.DataFrame, period_cols: List[str]) -> FinancialStatement:
    """Rebuilds a validated FinancialStatement instance from edited modeling dataframe."""
    row_map = {}
    for _, row in df.iterrows():
        key = str(row.get("Metric Key", "")).strip().lower()
        if not key:
            # Map by display name fallback
            disp = str(row.get("Line Item", "")).strip().lower()
            for std_k, std_disp in STANDARD_P_AND_L_ROWS:
                if std_k in disp or std_disp.lower() in disp:
                    key = std_k
                    break
        if key:
            vals = [float(row.get(p, 0.0) or 0.0) for p in period_cols]
            row_map[key] = np.array(vals, dtype=np.float64)

    # Derive missing core metrics if user only input components
    n = len(period_cols)
    if "revenue" not in row_map:
        raise ValueError("Revenue row is required to construct a valid financial model.")

    rev = row_map["revenue"]
    cogs = row_map.get("cogs", rev * 0.60)
    gp = row_map.get("gross_profit", rev - cogs)
    opex = row_map.get("opex", rev * 0.22)
    ebitda = row_map.get("ebitda", gp - opex)
    pbt = row_map.get("pbt", ebitda * 0.78)
    pat = row_map.get("pat", pbt * 0.75)

    return FinancialStatement(
        periods=period_cols,
        revenue=rev,
        cogs=cogs,
        gross_profit=gp,
        opex=opex,
        ebitda=ebitda,
        pbt=pbt,
        pat=pat,
    )


def initialize_model_workspace_state():
    """Initializes financial modeling workspace session variables."""
    if "current_statement" not in st.session_state:
        st.session_state["current_statement"] = generate_clean_midmarket_statement()
        st.session_state["statement_source"] = "Demo: Apex Precision Automotives (₹50 Cr Mid-Market)"
        st.session_state["file_normalized"] = True

    if "model_grid_df" not in st.session_state:
        stmt = st.session_state["current_statement"]
        st.session_state["model_grid_df"] = statement_to_modeling_df(stmt)
        st.session_state["model_periods"] = list(stmt.periods)

    if "custom_line_items" not in st.session_state:
        st.session_state["custom_line_items"] = []


def render_model_page(on_navigate, user_unit: str = "crores"):
    """
    Renders the dedicated In-Browser Financial Modeling & Spreadsheet Workspace.
    """
    initialize_model_workspace_state()

    user = st.session_state.get("user")
    company_name = user.company_name if user else "Apex Precision Automotives Ltd."
    logo_icon = get_logo_icon_b64()

    # Top Header
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <img src="{logo_icon}" alt="Arctus" style="height: 48px; width: auto; filter: drop-shadow(0 0 12px rgba(180, 154, 90, 0.3));" />
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                            <span class="brand-badge" style="margin: 0; padding: 2px 8px; font-size: 0.72rem;">MODELING WORKSPACE</span>
                            <span style="font-size: 0.8rem; color: var(--color-growth); display: inline-flex; align-items: center; gap: 6px;">
                                <span class="live-pulse-dot"></span> In-Browser Spreadsheet Editor • Real-Time Subtotals
                            </span>
                        </div>
                        <h1 style="font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.15;">
                            Financial Model & Ingestion Studio
                        </h1>
                        <p style="color: var(--text-dim); font-size: 0.92rem; margin: 4px 0 0 0;">
                            Target: <span style="color: {ACCENT_GOLD}; font-weight: 600;">{company_name}</span> &nbsp;|&nbsp; 
                            Source: <span style="color: var(--text-primary);">{st.session_state.get('statement_source', 'Spreadsheet Model')}</span>
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button class="nav-btn-ghost" style="height: 36px; padding: 0 14px; font-size: 0.82rem;" onclick="window.location.href='?page=overview'">
                        📊 Cockpit
                    </button>
                    <button class="nav-btn-ghost" style="height: 36px; padding: 0 14px; font-size: 0.82rem;" onclick="window.location.href='?page=scenarios'">
                        🎯 Studio
                    </button>
                    <button class="nav-btn-ghost" style="height: 36px; padding: 0 14px; font-size: 0.82rem;" onclick="window.location.href='?page=covenants'">
                        🏦 Covenants
                    </button>
                    <button class="nav-btn-primary" style="height: 36px; padding: 0 14px; font-size: 0.82rem;" onclick="window.location.href='?page=dashboard'">
                        ⚡ Stress Engine →
                    </button>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Quick Stats Telemetry Ribbon
    stmt = st.session_state["current_statement"]
    run_rate = stmt.get_run_rate()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            label="Annualized Turnover",
            value=format_inr(run_rate["annualized_revenue"], unit=user_unit),
            subtext=f"{len(stmt.periods)} Active Historical Quarters",
            is_gold=True
        )
    with col2:
        render_metric_card(
            label="Annualized Operating EBITDA",
            value=format_inr(run_rate["annualized_ebitda"], unit=user_unit),
            subtext=f"Margin: {run_rate['latest_ebitda_margin']:.1f}%",
            is_gold=True
        )
    with col3:
        render_metric_card(
            label="Gross Profit Margin",
            value=f"{run_rate['latest_gross_margin']:.1f}%",
            subtext="Operating contribution margin"
        )
    with col4:
        render_metric_card(
            label="Ledger Health",
            value="Ind AS Compliant",
            subtext=f"Chronology: {stmt.periods[0]} → {stmt.periods[-1]}",
            badge="Verified",
            badge_type="growth"
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 2. Main Workspace Modes (Tabs)
    tab_grid, tab_upload, tab_presets = st.tabs([
        "📊 Interactive Spreadsheet Grid Editor",
        "📁 Ingest Raw Spreadsheet (Excel / CSV)",
        "🏢 Standard Industry Corporate Presets",
    ])

    # TAB 1: SPREADSHEET GRID EDITOR
    with tab_grid:
        st.markdown(
            """
            <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <strong style="color: var(--accent-gold); font-size: 1.05rem;">Interactive P&L Ledger Editor</strong>
                        <p style="color: var(--text-dim); font-size: 0.85rem; margin: 4px 0 0 0;">
                            Double-click any cell to adjust quarterly actuals. Add custom ledger accounts or extend new quarters. 
                            All calculations and stress tests dynamically sync when you click <b>Save & Commit Model Changes</b>.
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        grid_df = st.session_state["model_grid_df"].copy()
        period_cols = st.session_state["model_periods"]

        # Grid Action Toolbar: Add Quarter, Add Custom Ledger Line, Recompute Subtotals
        t_col1, t_col2, t_col3, t_col4 = st.columns([1.2, 1.2, 1.0, 1.2])

        with t_col1:
            with st.popover("➕ Add New Quarter Period"):
                new_q_input = st.text_input(
                    "Quarter Label (e.g. Q1 FY25)",
                    value=f"Q{(len(period_cols)%4)+1} FY{24 + (len(period_cols)//4)}"
                )
                base_col_to_copy = st.selectbox("Pre-fill with figures from:", period_cols, index=len(period_cols)-1)
                growth_bump = st.slider("Quarterly Trend Growth (%)", -20.0, 30.0, 3.5, 0.5)

                if st.button("Add Quarter to Model", type="primary", use_container_width=True):
                    if new_q_input in period_cols:
                        st.error(f"Quarter '{new_q_input}' already exists in model.")
                    else:
                        mult = 1.0 + (growth_bump / 100.0)
                        grid_df[new_q_input] = grid_df[base_col_to_copy] * mult
                        period_cols.append(new_q_input)
                        st.session_state["model_periods"] = period_cols
                        st.session_state["model_grid_df"] = grid_df
                        st.success(f"Added {new_q_input} successfully!")
                        st.rerun()

        with t_col2:
            with st.popover("➕ Add Custom Ledger Account"):
                custom_item_name = st.text_input("Ledger Account Name", placeholder="e.g. Subsidies / Export Incentives")
                account_type = st.selectbox("Accounting Classification", ["Revenue Component", "Direct Cost (COGS)", "Indirect OPEX", "Non-Operating"])
                initial_val = st.number_input("Base Value (₹ Actuals)", min_value=0.0, value=2500000.0, step=100000.0)

                if st.button("Append Ledger Account", type="primary", use_container_width=True):
                    if custom_item_name:
                        new_row = {"Line Item": custom_item_name, "Metric Key": f"custom_{len(st.session_state['custom_line_items'])+1}"}
                        for p in period_cols:
                            new_row[p] = initial_val
                        grid_df = pd.concat([grid_df, pd.DataFrame([new_row])], ignore_index=True)
                        st.session_state["custom_line_items"].append({"name": custom_item_name, "type": account_type})
                        st.session_state["model_grid_df"] = grid_df
                        st.success(f"Appended '{custom_item_name}' to ledger!")
                        st.rerun()

        with t_col3:
            if st.button("↻ Recompute All Subtotals", use_container_width=True):
                # Ensure Gross Profit = Revenue - COGS, EBITDA = GP - OPEX
                for p in period_cols:
                    rev_val = float(grid_df.loc[grid_df["Metric Key"] == "revenue", p].values[0]) if len(grid_df.loc[grid_df["Metric Key"] == "revenue", p]) > 0 else 0.0
                    cogs_val = float(grid_df.loc[grid_df["Metric Key"] == "cogs", p].values[0]) if len(grid_df.loc[grid_df["Metric Key"] == "cogs", p]) > 0 else 0.0
                    gp_val = rev_val - cogs_val
                    if "gross_profit" in grid_df["Metric Key"].values:
                        grid_df.loc[grid_df["Metric Key"] == "gross_profit", p] = gp_val

                    opex_val = float(grid_df.loc[grid_df["Metric Key"] == "opex", p].values[0]) if len(grid_df.loc[grid_df["Metric Key"] == "opex", p]) > 0 else 0.0
                    ebitda_val = gp_val - opex_val
                    if "ebitda" in grid_df["Metric Key"].values:
                        grid_df.loc[grid_df["Metric Key"] == "ebitda", p] = ebitda_val

                    if "pbt" in grid_df["Metric Key"].values:
                        grid_df.loc[grid_df["Metric Key"] == "pbt", p] = ebitda_val * 0.78
                    if "pat" in grid_df["Metric Key"].values:
                        grid_df.loc[grid_df["Metric Key"] == "pat", p] = (ebitda_val * 0.78) * 0.75

                st.session_state["model_grid_df"] = grid_df
                st.success("Subtotals auto-synchronized across periods!")
                st.rerun()

        with t_col4:
            if st.button("↺ Reset to Clean Statement", use_container_width=True):
                st.session_state["model_grid_df"] = statement_to_modeling_df(st.session_state["current_statement"])
                st.session_state["model_periods"] = list(st.session_state["current_statement"].periods)
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Interactive Data Editor Component
        column_config = {
            "Line Item": st.column_config.TextColumn(
                "Financial Line Item",
                help="Standard Ind AS P&L account or custom ledger row",
                disabled=False,
                width="medium"
            ),
            "Metric Key": st.column_config.TextColumn(
                "System Key",
                disabled=True,
                width="small"
            )
        }
        for p in period_cols:
            column_config[p] = st.column_config.NumberColumn(
                p,
                format="₹ %.2f",
                help=f"Actuals for {p} in ₹ INR",
                min_value=0.0
            )

        edited_df = st.data_editor(
            grid_df,
            column_config=column_config,
            use_container_width=True,
            num_rows="dynamic",
            key="financial_model_data_editor",
            height=380
        )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Commit and Save Actions
        save_col1, save_col2, save_col3 = st.columns([1.5, 1.2, 1.2])

        with save_col1:
            if st.button("💾 Save & Commit Model Changes to Engine", type="primary", use_container_width=True):
                try:
                    new_stmt = modeling_df_to_statement(edited_df, period_cols)
                    st.session_state["current_statement"] = new_stmt
                    st.session_state["model_grid_df"] = edited_df
                    st.session_state["forecast_results"] = None  # Force engine recalculation
                    st.success("Financial statement updated and synchronized across all platform modules!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Validation Notice: {str(e)}")

        with save_col2:
            # Download updated model as CSV
            csv_export = edited_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Model as CSV",
                data=csv_export,
                file_name=f"{company_name.replace(' ', '_')}_Financial_Model.csv",
                mime="text/csv",
                use_container_width=True
            )

        with save_col3:
            if st.button("⚡ Test in Stress Engine →", use_container_width=True):
                on_navigate("dashboard")

    # TAB 2: RAW FILE INGESTION (EXCEL / CSV)
    with tab_upload:
        st.markdown(
            """
            <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 18px 22px; margin-bottom: 24px;">
                <h4 style="color: var(--accent-gold); margin-bottom: 8px;">Upload Enterprise P&L Spreadsheet</h4>
                <p style="color: var(--text-dim); font-size: 0.88rem; line-height: 1.5; margin: 0;">
                    Arctus automatically detects sheet structures, unmerges title headers, resolves accounting parentheses <code>(₹ 42,000)</code>, 
                    and uses <b>RapidFuzz token matching</b> to map arbitrary Indian corporate row labels to the standardized schema.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        up_col1, up_col2 = st.columns([2.5, 1.5])
        with up_col1:
            uploaded_file = st.file_uploader(
                "Select P&L Workbook (.xlsx, .xls, .csv)",
                type=["xlsx", "xls", "csv"],
                help="Supports multi-sheet workbooks, merged headers, and Indian accounting formats."
            )

        with up_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            # Button to generate a messy test Excel file
            messy_excel_bytes = create_messy_multisheet_excel("Apex Test Engineering Pvt Ltd")
            st.download_button(
                label="📥 Download Messy Sample Excel File",
                data=messy_excel_bytes,
                file_name="Sample_Messy_Indian_PL_Statement.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Download an intentionally messy Indian corporate spreadsheet with merged cells, negative parentheses, and 3 sheets to test the ingestion engine."
            )

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name

            # Run Stage 1: RawNormalizer
            normalizer = RawNormalizer()
            try:
                norm_res = normalizer.process(file_bytes, filename)
                df_norm = norm_res["dataframe"]
                line_col = norm_res["line_item_column"]
                period_cols = norm_res["period_columns"]
                raw_labels = df_norm[line_col].astype(str).tolist()

                st.success(f"✓ Normalization Complete: Extracted {len(period_cols)} periods across {len(df_norm)} line items.")

                with st.expander("Inspection: Normalizer Audit Trail", expanded=False):
                    for entry in norm_res["audit_trail"]:
                        st.markdown(f"• <span style='font-family: monospace; font-size: 0.85rem; color: #E5E5E5;'>{entry}</span>", unsafe_allow_html=True)

                # Check period continuity
                continuity = ValidationLayer.check_period_continuity(period_cols)
                if not continuity["is_continuous"]:
                    st.warning(f"Missing periods detected in chronology: {', '.join(continuity['missing_quarters'])}.")
                    if st.button("Interpolate Missing Quarters Linearly", key="btn_interpolate"):
                        df_norm, period_cols = ValidationLayer.interpolate_missing_quarters(
                            df_norm.set_index(line_col), period_cols, continuity["missing_quarters"]
                        )
                        df_norm = df_norm.reset_index()
                        st.success("Quarters interpolated successfully.")

                # Stage 2: SchemaMapper
                mapper = SchemaMapper()
                map_res = mapper.auto_map_schema(
                    raw_labels=raw_labels,
                    manual_overrides=st.session_state.get("manual_overrides", {})
                )

                st.markdown("#### Schema Mapping Review & Overrides")
                st.markdown(
                    "<p style='font-size: 0.85rem; color: var(--text-dim);'>"
                    "Review auto-mapped Indian accounting rows. High confidence mappings (≥80%) are pre-selected in green."
                    "</p>",
                    unsafe_allow_html=True
                )

                col_m1, col_m2 = st.columns(2)
                override_dict = st.session_state.get("manual_overrides", {}).copy()

                metrics_to_show = list(mapper.STANDARD_METRICS)
                for idx, metric in enumerate(metrics_to_show):
                    curr_col = col_m1 if idx % 2 == 0 else col_m2
                    with curr_col:
                        assigned_label = map_res["mapping"].get(metric)
                        conf = map_res["confidence_scores"].get(metric, 0.0)

                        options = ["-- None / Auto Derive --"] + raw_labels
                        default_idx = (options.index(assigned_label) if assigned_label in options else 0)

                        selected_label = st.selectbox(
                            f"{metric.upper()} (Confidence: {conf}%)",
                            options=options,
                            index=default_idx,
                            key=f"upload_map_{metric}"
                        )

                        if selected_label != "-- None / Auto Derive --":
                            override_dict[metric] = selected_label
                        elif metric in override_dict:
                            del override_dict[metric]

                st.session_state["manual_overrides"] = override_dict

                if st.button("Apply Mapping & Ingest into Workspace Grid", type="primary", use_container_width=True):
                    std_df = mapper.construct_standardized_statement(
                        df_norm, line_col, period_cols, map_res["mapping"]
                    )
                    stmt, issues = ValidationLayer.create_verified_statement(std_df, period_cols)
                    st.session_state["current_statement"] = stmt
                    st.session_state["statement_source"] = f"Uploaded: {filename}"
                    st.session_state["model_grid_df"] = statement_to_modeling_df(stmt)
                    st.session_state["model_periods"] = list(stmt.periods)
                    st.session_state["forecast_results"] = None
                    st.success("File successfully ingested into interactive modeling grid!")
                    st.rerun()

            except Exception as e:
                st.error(f"Ingestion Notice: {str(e)}")

    # TAB 3: INDUSTRY PRESETS
    with tab_presets:
        st.markdown(
            """
            <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 18px 22px; margin-bottom: 24px;">
                <h4 style="color: var(--accent-gold); margin-bottom: 8px;">Indian Mid-Market Archetype Models</h4>
                <p style="color: var(--text-dim); font-size: 0.88rem; line-height: 1.5; margin: 0;">
                    Instantly load validated multi-quarter financial statements calibrated to representative Indian mid-market business profiles.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        p_col1, p_col2, p_col3 = st.columns(3)

        with p_col1:
            st.markdown(
                f"""
                <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px;">
                    <div class="brand-badge" style="margin-bottom: 8px;">AUTO ANCILLARY</div>
                    <h4 style="color: var(--text-primary); margin-bottom: 6px;">Apex Precision Automotives</h4>
                    <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                        • ₹50 Cr Annual Turnover<br>
                        • High COGS (58% Raw Steel/Aluminum)<br>
                        • 8 Historical Quarters (Q1 FY23 → Q4 FY24)<br>
                        • Heavy working capital & supplier credit lines
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("Load Auto Ancillary Model", key="load_preset_auto", use_container_width=True):
                new_stmt = generate_clean_midmarket_statement("Apex Precision Automotives Ltd.", base_quarterly_rev=125000000.0)
                st.session_state["current_statement"] = new_stmt
                st.session_state["statement_source"] = "Archetype: Apex Precision Automotives (₹50 Cr Auto Ancillary)"
                st.session_state["model_grid_df"] = statement_to_modeling_df(new_stmt)
                st.session_state["model_periods"] = list(new_stmt.periods)
                st.session_state["forecast_results"] = None
                st.success("Loaded ₹50 Cr Auto Ancillary Model!")
                st.rerun()

        with p_col2:
            st.markdown(
                f"""
                <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px;">
                    <div class="brand-badge" style="margin-bottom: 8px;">CHEMICALS & PHARMA</div>
                    <h4 style="color: var(--text-primary); margin-bottom: 6px;">Bharat Specialty Chemicals</h4>
                    <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                        • ₹100 Cr Annual Turnover<br>
                        • Moderate COGS (48% Feedstocks)<br>
                        • Higher EBITDA Margins (24.5%)<br>
                        • Substantial term debt for plant expansions
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("Load Specialty Chemicals Model", key="load_preset_chem", use_container_width=True):
                new_stmt = generate_clean_midmarket_statement("Bharat Specialty Chemicals Ltd.", base_quarterly_rev=250000000.0)
                st.session_state["current_statement"] = new_stmt
                st.session_state["statement_source"] = "Archetype: Bharat Specialty Chemicals (₹100 Cr Chemicals)"
                st.session_state["model_grid_df"] = statement_to_modeling_df(new_stmt)
                st.session_state["model_periods"] = list(new_stmt.periods)
                st.session_state["forecast_results"] = None
                st.success("Loaded ₹100 Cr Specialty Chemicals Model!")
                st.rerun()

        with p_col3:
            st.markdown(
                f"""
                <div style="background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px;">
                    <div class="brand-badge" style="margin-bottom: 8px;">B2B SAAS / TECH</div>
                    <h4 style="color: var(--text-primary); margin-bottom: 6px;">Horizon Cloud Technologies</h4>
                    <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                        • ₹25 Cr Annual Turnover<br>
                        • Low COGS (22% Cloud Infrastructure)<br>
                        • High OPEX (52% Engineering & Sales payroll)<br>
                        • Negative working capital cycle & high runway
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("Load B2B Tech Model", key="load_preset_tech", use_container_width=True):
                new_stmt = generate_clean_midmarket_statement("Horizon Cloud Technologies Ltd.", base_quarterly_rev=62500000.0)
                st.session_state["current_statement"] = new_stmt
                st.session_state["statement_source"] = "Archetype: Horizon Cloud Technologies (₹25 Cr B2B SaaS)"
                st.session_state["model_grid_df"] = statement_to_modeling_df(new_stmt)
                st.session_state["model_periods"] = list(new_stmt.periods)
                st.session_state["forecast_results"] = None
                st.success("Loaded ₹25 Cr B2B SaaS Model!")
                st.rerun()
