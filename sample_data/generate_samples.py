"""
Generate sample Excel and CSV files for testing and evaluation of Arctus.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.synthetic import create_messy_multisheet_excel, create_transposed_csv, generate_clean_midmarket_statement

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Messy multi-sheet Excel
    messy_bytes = create_messy_multisheet_excel("Apex Precision Automotives Ltd.")
    messy_path = os.path.join(out_dir, "messy_multisheet_pl.xlsx")
    with open(messy_path, "wb") as f:
        f.write(messy_bytes)
    print(f"Generated: {messy_path}")

    # 2. Transposed CSV
    transposed_bytes = create_transposed_csv()
    transposed_path = os.path.join(out_dir, "transposed_pl.csv")
    with open(transposed_path, "wb") as f:
        f.write(transposed_bytes)
    print(f"Generated: {transposed_path}")

    # 3. Clean mid-market Excel
    clean_stmt = generate_clean_midmarket_statement()
    clean_df = clean_stmt.to_dataframe()
    clean_path = os.path.join(out_dir, "clean_midmarket_pl.xlsx")
    clean_df.to_excel(clean_path, index=False)
    print(f"Generated: {clean_path}")

if __name__ == "__main__":
    main()
