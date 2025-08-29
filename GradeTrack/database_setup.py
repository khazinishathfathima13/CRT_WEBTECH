"""
Database setup script to populate the Academic Performance Tracker with sample data
"""
from app import app, db
from models import Student, TheorySubject, LabCourse, ClassStatistics

def get_grade_from_marks(marks):
    """Convert marks to grade based on standard grading system"""
    if marks >= 90:
        return 'S'
    elif marks >= 80:
        return 'A'
    elif marks >= 70:
        return 'B'
    elif marks >= 60:
        return 'C'
    elif marks >= 50:
        return 'D'
    elif marks >= 40:
        return 'E'
    else:
        return 'F'

def setup_database():
    """Set up the database with sample student data"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Sample student data based on the provided PDF
        sample_student = Student(
            student_id='232G1A3224',
            name='KHAZI NISHATH FATHIMA',
            year=1,
            semester=1
        )
        db.session.add(sample_student)
        
        # Theory subjects for the sample student
        theory_subjects_data = [
            ('Theory Subject 1 (Y1S1)', 'TS101', 76),
            ('Theory Subject 2 (Y1S1)', 'TS102', 68),
            ('Theory Subject 3 (Y1S1)', 'TS103', 80),
            ('Theory Subject 4 (Y1S1)', 'TS104', 84),
            ('Theory Subject 5 (Y1S1)', 'TS105', 64)
        ]
        
        for subject_name, subject_code, marks in theory_subjects_data:
            theory_subject = TheorySubject(
                student_id='232G1A3224',
                subject_name=subject_name,
                subject_code=subject_code,
                marks=marks,
                grade=get_grade_from_marks(marks)
            )
            db.session.add(theory_subject)
        
        # Lab courses for the sample student
        lab_courses_data = [
            ('Lab 1 (Y1S1)', 'LAB101', 26, 69, 95),
            ('Lab 2 (Y1S1)', 'LAB102', 29, 56, 85),
            ('Lab 3 (Y1S1)', 'LAB103', 25, 69, 94)
        ]
        
        for lab_name, lab_code, internal, external, total in lab_courses_data:
            lab_course = LabCourse(
                student_id='232G1A3224',
                lab_name=lab_name,
                lab_code=lab_code,
                internal_marks=internal,
                external_marks=external,
                total_marks=total,
                grade=get_grade_from_marks(total)
            )
            db.session.add(lab_course)
        
        # Add more sample students for class statistics
        additional_students = [
            ('232G1A3225', 'STUDENT TWO', 1, 1),
            ('232G1A3226', 'STUDENT THREE', 1, 1),
            ('232G1A3227', 'STUDENT FOUR', 1, 1),
            ('232G1A3228', 'STUDENT FIVE', 1, 1)
        ]
        
        for student_id, name, year, semester in additional_students:
            student = Student(
                student_id=student_id,
                name=name,
                year=year,
                semester=semester
            )
            db.session.add(student)
            
            # Add random theory subjects
            for i in range(1, 6):
                marks = 65 + (i * 3)  # Varying marks
                theory_subject = TheorySubject(
                    student_id=student_id,
                    subject_name=f'Theory Subject {i} (Y1S1)',
                    subject_code=f'TS10{i}',
                    marks=marks,
                    grade=get_grade_from_marks(marks)
                )
                db.session.add(theory_subject)
            
            # Add random lab courses
            for i in range(1, 4):
                internal = 25 + i
                external = 60 + (i * 2)
                total = internal + external
                lab_course = LabCourse(
                    student_id=student_id,
                    lab_name=f'Lab {i} (Y1S1)',
                    lab_code=f'LAB10{i}',
                    internal_marks=internal,
                    external_marks=external,
                    total_marks=total,
                    grade=get_grade_from_marks(total)
                )
                db.session.add(lab_course)
        
        # Add class statistics
        class_stats = ClassStatistics(
            year=1,
            semester=1,
            total_students=56,
            passed_students=42,
            failed_students=14,
            average_cgpa=5.75,
            topper_student_id='232G1A3224'
        )
        db.session.add(class_stats)
        
        # Commit all changes
        db.session.commit()
        print("Database setup completed successfully!")
        print("Sample student: 232G1A3224 (KHAZI NISHATH FATHIMA)")
        print("Year: 1, Semester: 1")

if __name__ == '__main__':
    setup_database()
