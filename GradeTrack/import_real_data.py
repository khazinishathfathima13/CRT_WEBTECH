#!/usr/bin/env python3
"""
Correct Excel Data Import Script for Academic Performance Tracker
Properly imports real student data from Excel files with correct semester mapping
"""
import pandas as pd
from app import app, db
from models import Student, TheorySubject, LabCourse, ClassStatistics
import os

def get_grade_from_marks(marks):
    """Convert marks to grade based on standard grading system"""
    if marks == "LONG ABSENT" or marks == "" or marks is None or str(marks).strip() == "":
        return 'F'
    
    try:
        marks_num = float(marks)
        if marks_num >= 90:
            return 'S'
        elif marks_num >= 80:
            return 'A'
        elif marks_num >= 70:
            return 'B'
        elif marks_num >= 60:
            return 'C'
        elif marks_num >= 50:
            return 'D'
        elif marks_num >= 40:
            return 'E'
        else:
            return 'F'
    except (ValueError, TypeError):
        return 'F'

def clean_marks_value(marks):
    """Clean marks value and handle special cases"""
    if marks == "LONG ABSENT" or str(marks).strip() == "" or marks is None:
        return None
    
    try:
        return int(float(marks))
    except (ValueError, TypeError):
        return None

def examine_excel_structure(excel_file):
    """Examine Excel file to understand its structure"""
    df = pd.read_excel(excel_file, header=1)
    print(f"\n=== Structure of {excel_file} ===")
    print(f"Shape: {df.shape}")
    print("First row (headers):")
    print(df.iloc[0].to_dict())
    return df

def import_semester_data_correctly(excel_file, year, semester):
    """Import data from Excel file correctly for specific year and semester"""
    print(f"\nImporting {excel_file} -> Year {year}, Semester {semester}")
    
    if not os.path.exists(excel_file):
        print(f"File {excel_file} not found!")
        return
    
    try:
        # Read Excel file with proper header handling
        df = pd.read_excel(excel_file, header=1)  # Header row is at row 1
        
        # Filter out empty rows
        df = df.dropna(subset=[df.columns[0]])
        df = df[df.iloc[:, 0] != 'STUDENT ID']
        df = df[df.iloc[:, 0].notna()]
        
        print(f"Processing {len(df)} student records")
        
        for index, row in df.iterrows():
            try:
                student_id = str(row.iloc[0]).strip()
                student_name = str(row.iloc[1]).strip()
                
                # Skip invalid records
                if student_id in ['nan', 'NaN', ''] or student_name in ['nan', 'NaN', '']:
                    continue
                
                # Check if student already exists for this semester
                existing_student = Student.query.filter_by(
                    student_id=student_id, year=year, semester=semester
                ).first()
                
                if existing_student:
                    print(f"Student {student_id} already exists for Y{year}S{semester}, skipping...")
                    continue
                
                # Create new student record
                student = Student(
                    student_id=student_id,
                    name=student_name,
                    year=year,
                    semester=semester
                )
                db.session.add(student)
                
                # Extract theory subject marks (usually columns 2-6 for first 5 subjects)
                theory_count = 0
                subject_names = []
                
                # Look for actual subject marks columns - skip header columns
                for col_idx in range(2, len(df.columns)):
                    col_value = row.iloc[col_idx]
                    
                    # Skip if this is clearly not a marks column
                    if pd.isna(col_value):
                        continue
                    
                    # Check if this looks like marks (number or LONG ABSENT)
                    if str(col_value).strip() in ['', 'nan']:
                        continue
                    
                    # Try to identify if this is marks data
                    try:
                        # Check if it's a number or "LONG ABSENT"
                        if str(col_value) == "LONG ABSENT" or (isinstance(col_value, (int, float)) and 0 <= col_value <= 100):
                            theory_count += 1
                            
                            # Generate subject name based on semester
                            if year == 1 and semester == 1:
                                subject_names = [
                                    "ENGINEERING PHYSICS",
                                    "LINEAR ALGEBRA & CALCULUS", 
                                    "BASIC ELECTRICAL & ELECTRONICS ENGINEERING",
                                    "ENGINEERING CHEMISTRY",
                                    "PROBLEM SOLVING USING C"
                                ]
                            elif year == 1 and semester == 2:
                                subject_names = [
                                    "ENGINEERING MATHEMATICS-II",
                                    "ENGINEERING PHYSICS-II", 
                                    "BASIC MECHANICAL ENGINEERING",
                                    "BASIC CIVIL ENGINEERING",
                                    "ENGINEERING GRAPHICS",
                                    "ENVIRONMENTAL STUDIES"
                                ]
                            elif year == 2 and semester == 1:
                                subject_names = [
                                    "MATHEMATICAL FOUNDATIONS FOR COMPUTER SCIENCE",
                                    "COMPUTER PROGRAMMING", 
                                    "DIGITAL LOGIC DESIGN",
                                    "COMPUTER ORGANIZATION",
                                    "DATA STRUCTURES"
                                ]
                            elif year == 2 and semester == 2:
                                subject_names = [
                                    "DESIGN AND ANALYSIS OF ALGORITHMS",
                                    "DATABASE MANAGEMENT SYSTEMS", 
                                    "FORMAL LANGUAGES AND AUTOMATA THEORY",
                                    "COMPUTER NETWORKS",
                                    "OPERATING SYSTEMS"
                                ]
                            
                            # Use appropriate subject name
                            if theory_count <= len(subject_names):
                                subject_name = subject_names[theory_count - 1]
                            else:
                                subject_name = f"Theory Subject {theory_count} (Y{year}S{semester})"
                            
                            cleaned_marks = clean_marks_value(col_value)
                            
                            theory_subject = TheorySubject(
                                student_id=student_id,
                                subject_name=subject_name,
                                subject_code=f"TS{year}{semester}{theory_count:02d}",
                                marks=cleaned_marks if cleaned_marks is not None else 0,
                                grade=get_grade_from_marks(col_value)
                            )
                            db.session.add(theory_subject)
                            
                            # Stop after 5-6 theory subjects
                            if theory_count >= 6:
                                break
                                
                    except (ValueError, TypeError):
                        continue
                
                print(f"Added: {student_id} - {student_name} ({theory_count} subjects)")
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        # Commit changes for this semester
        db.session.commit()
        print(f"Successfully imported Year {year}, Semester {semester}")
        
    except Exception as e:
        print(f"Error reading Excel file {excel_file}: {e}")
        db.session.rollback()

def main():
    """Main function to import all semester data correctly"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Define Excel files with new timestamps
        excel_files = [
            ("attached_assets/1-1 SEMESTER RESULTS_1756310639227.xlsx", 1, 1),
            ("attached_assets/1-2 SEMESTER RESULTS_1756310650480.xlsx", 1, 2),
            ("attached_assets/2-1 SEMESTER RESULTS_1756310657928.xlsx", 2, 1),
            ("attached_assets/2-2 SEMESTER RESULTS_1756310665347.xlsx", 2, 2),
        ]
        
        # Import each semester's data
        for excel_file, year, semester in excel_files:
            import_semester_data_correctly(excel_file, year, semester)
        
        print("\n=== Data Import Complete ===")
        
        # Verify import
        for year in [1, 2]:
            for semester in [1, 2]:
                count = Student.query.filter_by(year=year, semester=semester).count()
                print(f"Year {year}, Semester {semester}: {count} students")

if __name__ == '__main__':
    main()