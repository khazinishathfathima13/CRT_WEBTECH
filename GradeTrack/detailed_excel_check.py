#!/usr/bin/env python3
"""
Detailed examination of Excel files to understand exact structure
"""
import pandas as pd
import os

def examine_detailed(file_path, max_rows=5):
    """Examine Excel file in detail"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"\n=== DETAILED EXAMINATION: {file_path} ===")
    
    # Read with different header options
    df = pd.read_excel(file_path, header=1)
    
    print(f"Shape: {df.shape}")
    print(f"Total rows: {len(df)}")
    
    # Show header row
    print("\n--- HEADER ROW ---")
    header_row = df.iloc[0]
    for i, val in enumerate(header_row):
        print(f"Col {i:2}: {val}")
    
    # Show actual data rows
    print(f"\n--- FIRST {max_rows} DATA ROWS ---")
    for row_idx in range(1, min(max_rows + 1, len(df))):
        print(f"\nRow {row_idx} (Student: {df.iloc[row_idx, 0]}):")
        student_row = df.iloc[row_idx]
        for i, val in enumerate(student_row):
            if i < 20:  # Show first 20 columns
                print(f"  Col {i:2}: {val}")
    
    # Look for numeric patterns (likely marks)
    print("\n--- MARKS COLUMNS ANALYSIS ---")
    for col_idx in range(2, min(20, len(df.columns))):
        col_data = df.iloc[1:6, col_idx]  # First 5 students
        numeric_count = 0
        for val in col_data:
            try:
                if pd.notna(val) and (isinstance(val, (int, float)) or str(val) == "LONG ABSENT"):
                    numeric_count += 1
            except:
                pass
        
        if numeric_count >= 3:  # If at least 3 entries look like marks
            print(f"Col {col_idx:2}: Likely MARKS - {col_data.tolist()}")

if __name__ == "__main__":
    files = [
        "attached_assets/1-1 SEMESTER RESULTS_1756310639227.xlsx",
        "attached_assets/1-2 SEMESTER RESULTS_1756310650480.xlsx", 
        "attached_assets/2-1 SEMESTER RESULTS_1756310657928.xlsx",
        "attached_assets/2-2 SEMESTER RESULTS_1756310665347.xlsx"
    ]
    
    for file in files:
        examine_detailed(file, 3)