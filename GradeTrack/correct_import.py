#!/usr/bin/env python3
"""
CORRECT import script - only import semester-specific data
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

def import_single_semester(excel_file, year, semester):
    """Import ONLY the data for a specific semester - not all semesters"""
    print(f"\nImporting {excel_file} -> Year {year}, Semester {semester}")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file, header=1)
        df = df.dropna(subset=[df.columns[0]])
        df = df[df.iloc[:, 0] != 'STUDENT ID']
        df = df[df.iloc[:, 0].notna()]
        
        # Subject names ONLY for this specific semester
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
        
        # Get subjects for THIS semester ONLY
        semester_subjects = subject_names.get((year, semester), [])
        
        # Theory marks columns: 2, 4, 6, 8, 10
        theory_cols = [2, 4, 6, 8, 10]
        
        print(f"Processing {len(df)} students for semester-specific subjects: {semester_subjects}")
        
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
                    continue
                
                # Create student record
                student = Student(
                    student_id=student_id,
                    name=student_name,
                    year=year,
                    semester=semester
                )
                db.session.add(student)
                
                # Import ONLY the subjects for THIS semester
                subjects_added = 0
                for i, col_idx in enumerate(theory_cols):
                    if i < len(semester_subjects):
                        marks_value = row.iloc[col_idx] if col_idx < len(df.columns) else None
                        
                        if marks_value is not None:
                            cleaned_marks = clean_marks_value(marks_value)
                            
                            theory_subject = TheorySubject(
                                student_id=student_id,
                                subject_name=semester_subjects[i],
                                subject_code=f"TS{year}{semester}{i+1:02d}",
                                marks=cleaned_marks if cleaned_marks is not None else 0,
                                grade=get_grade_from_marks(marks_value),
                                year=year,
                                semester=semester
                            )
                            db.session.add(theory_subject)
                            subjects_added += 1
                
                # Import labs from columns 16+ (ONLY for this semester)
                lab_start = 16
                labs_added = 0
                
                for i in range(0, 12, 4):  # Every 4 columns: Internal, External, Total, Grade
                    if lab_start + i + 2 < len(df.columns) and labs_added < 3:
                        internal = row.iloc[lab_start + i]
                        external = row.iloc[lab_start + i + 1]
                        total = row.iloc[lab_start + i + 2]
                        
                        if pd.notna(total):
                            try:
                                total_num = float(total)
                                if 0 <= total_num <= 100:
                                    labs_added += 1
                                    cleaned_internal = clean_marks_value(internal)
                                    cleaned_external = clean_marks_value(external)
                                    cleaned_total = clean_marks_value(total)
                                    
                                    lab_course = LabCourse(
                                        student_id=student_id,
                                        lab_name=f"Lab {labs_added} (Y{year}S{semester})",
                                        lab_code=f"LAB{year}{semester}{labs_added:02d}",
                                        internal_marks=cleaned_internal or 0,
                                        external_marks=cleaned_external or 0,
                                        total_marks=cleaned_total or 0,
                                        grade=get_grade_from_marks(total),
                                        year=year,
                                        semester=semester
                                    )
                                    db.session.add(lab_course)
                            except (ValueError, TypeError):
                                continue
                
                if subjects_added > 0 or labs_added > 0:
                    print(f"Added: {student_id} - {student_name} ({subjects_added}T, {labs_added}L)")
                
            except Exception as e:
                print(f"Error processing {student_id}: {e}")
                continue
        
        db.session.commit()
        print(f"Successfully imported Year {year}, Semester {semester}")
        
    except Exception as e:
        print(f"Error reading {excel_file}: {e}")
        db.session.rollback()

def main():
    """Main import - each Excel file imports ONLY its semester data"""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Each Excel file contains data for ONLY its specific semester
        files = [
            ("attached_assets/1-1 SEMESTER RESULTS_1756310639227.xlsx", 1, 1),
            ("attached_assets/1-2 SEMESTER RESULTS_1756310650480.xlsx", 1, 2), 
            ("attached_assets/2-1 SEMESTER RESULTS_1756310657928.xlsx", 2, 1),
            ("attached_assets/2-2 SEMESTER RESULTS_1756310665347.xlsx", 2, 2)
        ]
        
        for excel_file, year, semester in files:
            import_single_semester(excel_file, year, semester)
        
        print("\n=== FINAL VERIFICATION ===")
        for year in [1, 2]:
            for semester in [1, 2]:
                students = Student.query.filter_by(year=year, semester=semester).all()
                if students:
                    sample = students[0]
                    theory_count = len(sample.theory_subjects)
                    lab_count = len(sample.lab_courses)
                    print(f"Year {year}, Semester {semester}: {len(students)} students, "
                          f"Theory: {theory_count}, Labs: {lab_count}")

if __name__ == '__main__':
    main()