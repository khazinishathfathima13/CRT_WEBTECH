#!/usr/bin/env python3
"""
Final correct import script based on exact Excel structure analysis
"""
import pandas as pd
from app import app, db
from models import Student, TheorySubject, LabCourse

def get_grade_from_marks(marks):
    """Convert marks to grade"""
    if marks == "LONG ABSENT" or marks == "" or marks is None or str(marks).strip() == "":
        return 'F'
    try:
        marks_num = float(marks)
        if marks_num >= 90: return 'S'
        elif marks_num >= 80: return 'A'  
        elif marks_num >= 70: return 'B'
        elif marks_num >= 60: return 'C'
        elif marks_num >= 50: return 'D'
        elif marks_num >= 40: return 'E'
        else: return 'F'
    except (ValueError, TypeError):
        return 'F'

def clean_marks_value(marks):
    """Clean marks value"""
    if marks == "LONG ABSENT" or str(marks).strip() == "" or marks is None:
        return None
    try:
        return int(float(marks))
    except (ValueError, TypeError):
        return None

def import_correct_semester_data(excel_file, year, semester):
    """Import semester data correctly based on exact column mapping"""
    print(f"\nImporting {excel_file} -> Year {year}, Semester {semester}")
    
    try:
        # Read with header=1 to get the right structure
        df = pd.read_excel(excel_file, header=1)
        
        # Filter valid students
        df = df.dropna(subset=[df.columns[0]])
        df = df[df.iloc[:, 0] != 'STUDENT ID']
        df = df[df.iloc[:, 0].notna()]
        
        print(f"Processing {len(df)} students")
        
        # Subject names for each semester
        subject_names = {
            (1,1): ["ENGINEERING PHYSICS", "LINEAR ALGEBRA & CALCULUS", 
                   "BASIC ELECTRICAL & ELECTRONICS ENGINEERING", "ENGINEERING CHEMISTRY", 
                   "PROBLEM SOLVING USING C"],
            (1,2): ["ENGINEERING MATHEMATICS-II", "ENGINEERING PHYSICS-II", 
                   "BASIC MECHANICAL ENGINEERING", "BASIC CIVIL ENGINEERING", 
                   "ENGINEERING GRAPHICS", "ENVIRONMENTAL STUDIES"],
            (2,1): ["MATHEMATICAL FOUNDATIONS FOR COMPUTER SCIENCE", "COMPUTER PROGRAMMING", 
                   "DIGITAL LOGIC DESIGN", "COMPUTER ORGANIZATION", "DATA STRUCTURES"],
            (2,2): ["DESIGN AND ANALYSIS OF ALGORITHMS", "DATABASE MANAGEMENT SYSTEMS", 
                   "FORMAL LANGUAGES AND AUTOMATA THEORY", "COMPUTER NETWORKS", 
                   "OPERATING SYSTEMS"]
        }
        
        subjects = subject_names.get((year, semester), [f"Subject {i+1}" for i in range(5)])
        
        # Theory marks are in columns 2, 4, 6, 8, 10 (TOTAL columns)
        theory_cols = [2, 4, 6, 8, 10]
        
        for index, row in df.iterrows():
            try:
                student_id = str(row.iloc[0]).strip()
                student_name = str(row.iloc[1]).strip()
                
                if student_id in ['nan', 'NaN', ''] or student_name in ['nan', 'NaN', '']:
                    continue
                
                # Check if student exists
                existing = Student.query.filter_by(
                    student_id=student_id, year=year, semester=semester).first()
                if existing:
                    print(f"Student {student_id} exists, skipping...")
                    continue
                
                # Create student
                student = Student(
                    student_id=student_id,
                    name=student_name,
                    year=year,
                    semester=semester
                )
                db.session.add(student)
                
                # Import theory subjects from correct columns
                for i, col_idx in enumerate(theory_cols):
                    if i < len(subjects) and col_idx < len(df.columns):
                        marks_value = row.iloc[col_idx]
                        cleaned_marks = clean_marks_value(marks_value)
                        
                        theory_subject = TheorySubject(
                            student_id=student_id,
                            subject_name=subjects[i],
                            subject_code=f"TS{year}{semester}{i+1:02d}",
                            marks=cleaned_marks if cleaned_marks is not None else 0,
                            grade=get_grade_from_marks(marks_value)
                        )
                        db.session.add(theory_subject)
                
                # Import lab data from columns 16+ (Internal, External, Total, Grade pattern)
                lab_start_col = 16
                lab_count = 0
                
                for i in range(0, 15, 4):  # Check every 4 columns for lab data
                    if lab_start_col + i + 2 < len(df.columns):
                        internal = row.iloc[lab_start_col + i]
                        external = row.iloc[lab_start_col + i + 1] 
                        total = row.iloc[lab_start_col + i + 2]
                        
                        # Check if this looks like lab data
                        if pd.notna(total) and str(total) != 'nan':
                            try:
                                total_num = float(total)
                                if 0 <= total_num <= 100:
                                    lab_count += 1
                                    cleaned_internal = clean_marks_value(internal)
                                    cleaned_external = clean_marks_value(external) 
                                    cleaned_total = clean_marks_value(total)
                                    
                                    lab_course = LabCourse(
                                        student_id=student_id,
                                        lab_name=f"Lab {lab_count} (Y{year}S{semester})",
                                        lab_code=f"LAB{year}{semester}{lab_count:02d}",
                                        internal_marks=cleaned_internal or 0,
                                        external_marks=cleaned_external or 0,
                                        total_marks=cleaned_total or 0,
                                        grade=get_grade_from_marks(total)
                                    )
                                    db.session.add(lab_course)
                                    
                                    if lab_count >= 3:  # Limit to 3 labs
                                        break
                            except (ValueError, TypeError):
                                continue
                
                print(f"Added: {student_id} - {student_name}")
                
            except Exception as e:
                print(f"Error processing {student_id}: {e}")
                continue
        
        db.session.commit()
        print(f"Successfully imported Year {year}, Semester {semester}")
        
    except Exception as e:
        print(f"Error reading {excel_file}: {e}")
        db.session.rollback()

def main():
    """Main import function"""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Import each semester
        files = [
            ("attached_assets/1-1 SEMESTER RESULTS_1756310639227.xlsx", 1, 1),
            ("attached_assets/1-2 SEMESTER RESULTS_1756310650480.xlsx", 1, 2), 
            ("attached_assets/2-1 SEMESTER RESULTS_1756310657928.xlsx", 2, 1),
            ("attached_assets/2-2 SEMESTER RESULTS_1756310665347.xlsx", 2, 2)
        ]
        
        for excel_file, year, semester in files:
            import_correct_semester_data(excel_file, year, semester)
        
        # Verify import
        print("\n=== IMPORT VERIFICATION ===")
        for year in [1, 2]:
            for semester in [1, 2]:
                count = Student.query.filter_by(year=year, semester=semester).count()
                print(f"Year {year}, Semester {semester}: {count} students")

if __name__ == '__main__':
    main()