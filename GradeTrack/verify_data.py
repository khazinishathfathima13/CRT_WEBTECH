#!/usr/bin/env python3
"""
Verify that each semester has different and correct data
"""
from app import app, db
from models import Student, TheorySubject, LabCourse

def verify_semester_data():
    """Check that each semester has different data"""
    with app.app_context():
        student_id = "232G1A3224"  # KHAZI NISHATH FATHIMA
        
        print(f"=== VERIFICATION FOR STUDENT {student_id} ===")
        
        for year in [1, 2]:
            for semester in [1, 2]:
                student = Student.query.filter_by(
                    student_id=student_id, year=year, semester=semester
                ).first()
                
                if student:
                    print(f"\n--- Year {year}, Semester {semester} ---")
                    print(f"Name: {student.name}")
                    print(f"Theory subjects: {len(student.theory_subjects)}")
                    print(f"Lab courses: {len(student.lab_courses)}")
                    
                    # Show theory subject details
                    print("Theory Subjects:")
                    for i, subject in enumerate(student.theory_subjects):
                        print(f"  {i+1}. {subject.subject_name}: {subject.marks} ({subject.grade})")
                    
                    # Show lab details
                    if student.lab_courses:
                        print("Lab Courses:")
                        for i, lab in enumerate(student.lab_courses):
                            print(f"  {i+1}. {lab.lab_name}: Internal={lab.internal_marks}, External={lab.external_marks}, Total={lab.total_marks} ({lab.grade})")
                    
                    print(f"CGPA: {student.calculate_cgpa()}")
                    print(f"Percentage: {student.calculate_percentage()}%")
                    print(f"Result: {student.get_result_status()}")
                else:
                    print(f"\nYear {year}, Semester {semester}: Student not found")

if __name__ == "__main__":
    verify_semester_data()