#!/usr/bin/env python3
"""
Check what data is currently in the database
"""
from app import app, db
from models import Student, TheorySubject, LabCourse
import pandas as pd

def check_database():
    """Check what's in the database"""
    with app.app_context():
        print("=== DATABASE CONTENTS ===")
        
        students = Student.query.all()
        print(f"Total students: {len(students)}")
        
        # Group by year and semester
        for year in [1, 2]:
            for semester in [1, 2]:
                students_in_semester = Student.query.filter_by(year=year, semester=semester).all()
                print(f"\nYear {year}, Semester {semester}: {len(students_in_semester)} students")
                
                if students_in_semester:
                    # Show first few students
                    for i, student in enumerate(students_in_semester[:3]):
                        print(f"  {student.student_id}: {student.name}")
                        theory_subjects = student.theory_subjects
                        print(f"    Theory subjects: {len(theory_subjects)}")
                        for j, subject in enumerate(theory_subjects[:3]):
                            print(f"      {j+1}. {subject.subject_name}: {subject.marks} ({subject.grade})")
                        if len(theory_subjects) > 3:
                            print(f"      ... and {len(theory_subjects)-3} more")
                        
                        lab_courses = student.lab_courses
                        print(f"    Lab courses: {len(lab_courses)}")
                        for j, lab in enumerate(lab_courses[:2]):
                            print(f"      {j+1}. {lab.lab_name}: {lab.total_marks} ({lab.grade})")

def check_specific_student():
    """Check specific student data"""
    with app.app_context():
        print("\n=== CHECKING KHAZI NISHATH FATHIMA ===")
        student_id = "232G1A3224"
        
        for year in [1, 2]:
            for semester in [1, 2]:
                student = Student.query.filter_by(
                    student_id=student_id, 
                    year=year, 
                    semester=semester
                ).first()
                
                if student:
                    print(f"\n{student.name} - Year {year}, Semester {semester}")
                    print(f"Theory subjects: {len(student.theory_subjects)}")
                    print(f"Lab courses: {len(student.lab_courses)}")
                    print(f"CGPA: {student.calculate_cgpa()}")
                    print(f"Percentage: {student.calculate_percentage()}")
                else:
                    print(f"\n{student_id} not found in Year {year}, Semester {semester}")

if __name__ == "__main__":
    check_database()
    check_specific_student()