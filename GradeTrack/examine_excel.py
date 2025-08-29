#!/usr/bin/env python3
"""
Simple script to examine Excel file structure
"""
import pandas as pd
import os

def examine_excel_file(file_path):
    """Examine structure of an Excel file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    try:
        print(f"\n=== Examining: {file_path} ===")
        df = pd.read_excel(file_path)
        print(f"Shape: {df.shape} (rows x columns)")
        
        print("\nColumns:")
        for i, col in enumerate(df.columns):
            print(f"{i:2}: {col}")
        
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        print("\nData types:")
        print(df.dtypes)
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    files = [
        "attached_assets/1-1 SEMESTER RESULTS_1756309550326.xlsx",
        "attached_assets/1-2 SEMESTER RESULTS_1756309569559.xlsx", 
        "attached_assets/2-1 SEMESTER RESULTS_1756309580835.xlsx",
        "attached_assets/2-2 SEMESTER RESULTS_1756309611615.xlsx"
    ]
    
    for file in files:
        examine_excel_file(file)
        print("\n" + "="*80)