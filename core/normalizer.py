"""
RawNormalizer - Stage 1 of the Arctus Data Ingestion Pipeline.
Handles CSV/Excel file detection, multi-sheet P&L identification, merged cell forward-filling,
decorative header stripping, transposed data orientation normalization, Indian currency/accounting
number cleaning, and period standardization.
"""

import io
import re
from typing import Tuple, List, Dict, Any, Optional, Union
import numpy as np
import pandas as pd
import openpyxl


class RawNormalizer:
    """
    Normalizes raw, messy financial spreadsheets into clean, structured DataFrames.
    """

    PL_KEYWORDS = [
        "revenue", "income", "sales", "turnover", "profit & loss", "p&l",
        "statement of profit", "financial results", "operations", "ebitda"
    ]

    QUARTER_PATTERNS = [
        # Q1 FY24, Q1-FY24, Q1FY24, FY24 Q1
        r"(?i)(?:Q([1-4])[\s\-_]*(?:FY)?([0-9]{2,4}))",
        r"(?i)(?:(?:FY)?([0-9]{2,4})[\s\-_]*Q([1-4]))",
        # 2023-Q1, 2023 Q1
        r"(?i)([0-9]{4})[\s\-_]*Q([1-4])",
        # Months: Apr-Jun 2023, April-June 2023
        r"(?i)(?:apr|may|jun|jul|aug|sep|oct|nov|dec|jan|feb|mar)[a-z]*[\s\-_]+(?:to|-)?[\s\-_]*(?:apr|may|jun|jul|aug|sep|oct|nov|dec|jan|feb|mar)[a-z]*[\s\-_]+([0-9]{2,4})"
    ]

    def __init__(self):
        self.audit_log: List[str] = []

    def log(self, message: str):
        """Append to transformation audit trail."""
        self.audit_log.append(message)

    @staticmethod
    def clean_accounting_number(val: Any) -> float:
        """
        Converts messy accounting strings to float:
        - Parentheses negatives: (42,000) -> -42000.0
        - Currency symbols: ₹, Rs, Rs., INR -> stripped
        - Indian commas: 12,34,567 -> 1234567.0
        - Dashes / blanks: '-' or '' -> 0.0
        - Suffixes: 'Cr' / 'Lakh' / 'L' multiplied or normalized
        """
        if pd.isna(val) or val is None:
            return 0.0
        if isinstance(val, (int, float, np.number)):
            return float(val)

        s = str(val).strip()
        if s in ("", "-", "--", "—", "N/A", "NA", "nil", "Nil"):
            return 0.0

        # Check for accounting parentheses negative format: (12,345.67) or (₹ 12,345)
        is_negative = False
        if s.startswith("(") and s.endswith(")"):
            is_negative = True
            s = s[1:-1].strip()
        elif s.startswith("-"):
            is_negative = True
            s = s[1:].strip()

        # Strip currency symbols and whitespace
        s = re.sub(r"(?i)(₹|rs\.?|inr|\$|€|£)", "", s).strip()
        
        # Check for multiplier suffixes
        multiplier = 1.0
        if re.search(r"(?i)\bcr(?:ores?)?\b", s):
            multiplier = 1e7
            s = re.sub(r"(?i)\bcr(?:ores?)?\b", "", s).strip()
        elif re.search(r"(?i)\bl(?:akhs?)?\b", s):
            multiplier = 1e5
            s = re.sub(r"(?i)\bl(?:akhs?)?\b", "", s).strip()

        # Remove all commas
        s = s.replace(",", "").strip()

        try:
            num = float(s) * multiplier
            return -num if is_negative else num
        except ValueError:
            return 0.0

    @classmethod
    def normalize_period_label(cls, period_str: str) -> str:
        """
        Standardizes period labels to canonical format 'Q1 FY24' or 'FY24'.
        """
        s = str(period_str).strip()
        
        # Match 'Q1 FY24' or 'Q1 2024'
        m = re.search(r"(?i)Q([1-4])[\s\-_]*(?:FY)?([0-9]{2,4})", s)
        if m:
            q, yr = m.groups()
            yr_str = yr[-2:] if len(yr) == 4 else yr
            return f"Q{q} FY{yr_str}"

        # Match 'FY24 Q1' or '2024 Q1'
        m = re.search(r"(?i)(?:FY)?([0-9]{2,4})[\s\-_]*Q([1-4])", s)
        if m:
            yr, q = m.groups()
            yr_str = yr[-2:] if len(yr) == 4 else yr
            return f"Q{q} FY{yr_str}"

        # Match '2023-Q1'
        m = re.search(r"(?i)([0-9]{4})[\s\-_]*Q([1-4])", s)
        if m:
            yr, q = m.groups()
            # Indian fiscal year: Apr-Mar (Q1 is Apr-Jun, FY ending next calendar year)
            yr_num = int(yr[-2:]) + 1
            return f"Q{q} FY{yr_num:02d}"

        # Match 'FY24' or 'FY 2024' (Annual)
        m = re.search(r"(?i)FY[\s\-_]*([0-9]{2,4})", s)
        if m:
            yr = m.group(1)
            yr_str = yr[-2:] if len(yr) == 4 else yr
            return f"FY{yr_str}"

        return s

    def identify_pl_sheet(self, file_content: bytes) -> str:
        """
        Inspects multi-sheet Excel file to find the P&L statement sheet.
        Scores sheet names and cell text for financial statement indicators.
        """
        wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True, read_only=True)
        sheet_names = wb.sheetnames

        # 1. Exact or keyword match on sheet names
        scored_sheets = []
        for name in sheet_names:
            score = 0
            lower = name.lower()
            if any(k in lower for k in ["p&l", "profit", "income", "statement of profit"]):
                score += 10
            elif any(k in lower for k in ["revenue", "financial", "operations", "results"]):
                score += 5
            scored_sheets.append((name, score))

        scored_sheets.sort(key=lambda x: x[1], reverse=True)
        if scored_sheets and scored_sheets[0][1] >= 5:
            self.log(f"Auto-selected sheet '{scored_sheets[0][0]}' based on title keyword scoring.")
            return scored_sheets[0][0]

        # 2. Inspect first 20 rows of each sheet if title was ambiguous
        for name in sheet_names:
            ws = wb[name]
            cell_text = ""
            for row in ws.iter_rows(max_row=20, max_col=10, values_only=True):
                for cell in row:
                    if cell:
                        cell_text += " " + str(cell).lower()
            
            if any(k in cell_text for k in ["revenue from operations", "total income", "gross profit", "ebitda"]):
                self.log(f"Selected sheet '{name}' based on content inspection.")
                return name

        # Default to first sheet
        self.log(f"Defaulted to first sheet '{sheet_names[0]}'.")
        return sheet_names[0]

    def read_excel_unmerged(self, file_content: bytes, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Reads Excel file using openpyxl, unmerging cells with forward-fill so no data is dropped.
        """
        wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
        sheet = wb[sheet_name] if sheet_name else wb.active

        # Resolve merged cells by populating all cells in the range with the top-left value
        merged_ranges = list(sheet.merged_cells.ranges)
        for rng in merged_ranges:
            top_val = sheet.cell(rng.min_row, rng.min_col).value
            sheet.unmerge_cells(str(rng))
            for row in range(rng.min_row, rng.max_row + 1):
                for col in range(rng.min_col, rng.max_col + 1):
                    sheet.cell(row, col).value = top_val

        data = []
        for row in sheet.iter_rows(values_only=True):
            data.append(list(row))

        df = pd.DataFrame(data)
        self.log(f"Successfully loaded and unmerged {len(merged_ranges)} cell ranges.")
        return df

    def strip_decorative_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scans DataFrame from top to detect table headers and removes logo, title, and empty rows.
        """
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            return df

        best_row_idx = 0
        max_score = -1

        for idx in range(min(12, len(df))):
            row_vals = df.iloc[idx].tolist()
            non_empty_count = sum(
                1 for v in row_vals 
                if pd.notna(v) and str(v).strip() not in ("", "-", "--", "nan", "None")
            )
            if non_empty_count == 0:
                continue

            # Check how many cells are numeric numbers
            num_numeric = 0
            for v in row_vals:
                if pd.notna(v):
                    s = str(v).strip().replace(",", "").replace("₹", "").replace("%", "").replace("(", "").replace(")", "")
                    try:
                        float(s)
                        num_numeric += 1
                    except ValueError:
                        pass

            # A header row should not be predominantly numeric
            if non_empty_count > 2 and (num_numeric / non_empty_count) > 0.50:
                continue

            # Header score: number of non-empty text cells
            score = non_empty_count
            row_str = " ".join([str(v).lower() for v in row_vals if pd.notna(v)])

            # Boost if row contains standard header keywords
            if any(k in row_str for k in ["particulars", "line item", "quarter", "period", "metric", "description", "q1", "q2", "fy"]):
                score += 5

            if score > max_score:
                max_score = score
                best_row_idx = idx

        if best_row_idx > 0:
            self.log(f"Stripped {best_row_idx} decorative header/title rows.")
            df = df.iloc[best_row_idx:].reset_index(drop=True)

        # Set first row as column header
        df.columns = [str(c).strip() if pd.notna(c) else f"Col_{i}" for i, c in enumerate(df.iloc[0])]
        df = df.iloc[1:].reset_index(drop=True)
        return df

    def detect_and_normalize_orientation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
        """
        Determines whether line items are rows or columns.
        Canonical target orientation:
        - Column 0: 'Particulars' / Line Item Names
        - Columns 1..N: Time Periods ('Q1 FY24', 'Q2 FY24', etc.)
        Returns normalized DataFrame and a boolean indicating whether it was transposed.
        """
        # Check columns vs first column values for period indicators
        cols_text = " ".join([str(c).lower() for c in df.columns])
        first_col_text = " ".join([str(v).lower() for v in df.iloc[:, 0].dropna()])

        # Count quarter indicators in column names vs first column
        col_q_matches = sum(1 for c in df.columns if re.search(r"(?i)(?:Q[1-4]|FY\s*[0-9]{2,4})", str(c)))
        first_col_q_matches = sum(1 for v in df.iloc[:, 0].dropna() if re.search(r"(?i)(?:Q[1-4]|FY\s*[0-9]{2,4})", str(v)))

        # Also check for financial keywords in columns vs first column
        col_pl_matches = sum(1 for c in df.columns if any(k in str(c).lower() for k in ["revenue", "sales", "ebitda", "profit"]))
        first_col_pl_matches = sum(1 for v in df.iloc[:, 0].dropna() if any(k in str(v).lower() for k in ["revenue", "sales", "ebitda", "profit"]))

        was_transposed = False
        # If columns contain line items and first column contains periods -> transpose!
        if first_col_q_matches > col_q_matches or col_pl_matches > first_col_pl_matches:
            self.log("Detected transposed orientation (periods in rows, line items in columns). Transposing to canonical standard.")
            # Set first column as index then transpose
            df = df.set_index(df.columns[0]).T.reset_index()
            df.columns = [str(c).strip() for c in df.columns]
            was_transposed = True

        return df, was_transposed

    def clean_and_standardize_periods(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
        """
        Standardizes period column headers and checks if data is annual or quarterly.
        Returns cleaned DataFrame and boolean is_annual.
        """
        new_cols = [df.columns[0]]
        period_cols = list(df.columns[1:])
        
        annual_count = 0
        quarterly_count = 0

        for col in period_cols:
            norm = self.normalize_period_label(str(col))
            new_cols.append(norm)
            if norm.startswith("FY") and not norm.startswith("FYQ") and "Q" not in norm:
                annual_count += 1
            elif "Q" in norm:
                quarterly_count += 1

        df.columns = new_cols
        is_annual = (annual_count > 0 and quarterly_count == 0)
        if is_annual:
            self.log("Detected annual financial reporting format.")
        else:
            self.log(f"Standardized {len(period_cols)} chronological periods.")

        return df, is_annual

    def process(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Full Stage 1 normalization pipeline:
        File -> Sheet Detection -> Unmerge -> Strip Noise -> Orient -> Number Clean -> Output
        """
        self.audit_log = []
        is_excel = filename.lower().endswith((".xlsx", ".xls"))

        if is_excel:
            sheet_name = self.identify_pl_sheet(file_content)
            df = self.read_excel_unmerged(file_content, sheet_name=sheet_name)
        else:
            self.log("Reading CSV stream.")
            df = pd.read_csv(io.BytesIO(file_content), header=None, dtype=str)

        # 1. Strip decorative headers & isolate table
        df = self.strip_decorative_headers(df)

        # 2. Standardize orientation so Column 0 = Line Items, Columns 1..N = Periods
        df, was_transposed = self.detect_and_normalize_orientation(df)

        # 3. Standardize period names & check periodicity
        df, is_annual = self.clean_and_standardize_periods(df)

        # 4. Clean accounting numbers across all period columns
        line_item_col = df.columns[0]
        period_cols = [c for c in df.columns if c != line_item_col]

        for col in period_cols:
            df[col] = df[col].apply(self.clean_accounting_number)

        # Drop rows where line item name is empty
        df = df[df[line_item_col].astype(str).str.strip().ne("")].reset_index(drop=True)

        return {
            "dataframe": df,
            "line_item_column": line_item_col,
            "period_columns": period_cols,
            "is_annual": is_annual,
            "was_transposed": was_transposed,
            "audit_trail": self.audit_log,
        }
