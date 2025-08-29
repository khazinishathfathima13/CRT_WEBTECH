from app import db
from sqlalchemy import func

class Student(db.Model):
    """Student model for storing basic student information"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 1 or 2
    semester = db.Column(db.Integer, nullable=False)  # 1 or 2
    
    @property
    def theory_subjects(self):
        """Get theory subjects for this specific semester"""
        return TheorySubject.query.filter_by(
            student_id=self.student_id, year=self.year, semester=self.semester
        ).all()
    
    @property
    def lab_courses(self):
        """Get lab courses for this specific semester"""
        return LabCourse.query.filter_by(
            student_id=self.student_id, year=self.year, semester=self.semester
        ).all()
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'year', 'semester', name='_student_year_semester_uc'),
    )
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'
    
    def calculate_cgpa(self):
        """Calculate CGPA based on all subjects and labs"""
        total_credits = 0
        total_grade_points = 0
        
        # Calculate from theory subjects
        for subject in self.theory_subjects:
            if subject.marks is None or subject.marks == 0:  # Handle LONG ABSENT cases
                continue
            grade_point = self.get_grade_point(subject.grade)
            if grade_point > 0:  # Exclude F grades
                total_credits += 4  # Assuming 4 credits per theory subject
                total_grade_points += grade_point * 4
        
        # Calculate from lab courses
        for lab in self.lab_courses:
            if lab.total_marks is None or lab.total_marks == 0:  # Handle LONG ABSENT cases
                continue
            grade_point = self.get_grade_point(lab.grade)
            if grade_point > 0:  # Exclude F grades
                total_credits += 2  # Assuming 2 credits per lab
                total_grade_points += grade_point * 2
        
        if total_credits == 0:
            return 0.0
        
        return round(total_grade_points / total_credits, 2)
    
    def calculate_percentage(self):
        """Calculate overall percentage"""
        total_marks = 0
        total_possible = 0
        
        # Theory subjects (out of 100 each)
        for subject in self.theory_subjects:
            total_marks += subject.marks
            total_possible += 100
        
        # Lab courses (out of 100 each)
        for lab in self.lab_courses:
            total_marks += lab.total_marks
            total_possible += 100
        
        if total_possible == 0:
            return 0.0
        
        return round((total_marks / total_possible) * 100, 2)
    
    def get_result_status(self):
        """Determine if student passed or failed"""
        # Check if any subject has F grade
        for subject in self.theory_subjects:
            if subject.grade == 'F':
                return 'FAIL'
        
        for lab in self.lab_courses:
            if lab.grade == 'F':
                return 'FAIL'
        
        return 'PASS'
    
    @staticmethod
    def get_grade_point(grade):
        """Convert grade to grade point"""
        grade_mapping = {
            'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0
        }
        return grade_mapping.get(grade, 0)

class TheorySubject(db.Model):
    """Theory subject model for storing subject marks and grades"""
    __tablename__ = 'theory_subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<TheorySubject {self.subject_name}: {self.marks} ({self.grade})>'

class LabCourse(db.Model):
    """Lab course model for storing lab marks and grades"""
    __tablename__ = 'lab_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    lab_name = db.Column(db.String(100), nullable=False)
    lab_code = db.Column(db.String(20), nullable=False)
    internal_marks = db.Column(db.Integer, nullable=False)
    external_marks = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<LabCourse {self.lab_name}: {self.total_marks} ({self.grade})>'

class ClassStatistics(db.Model):
    """Class statistics model for storing semester-wise statistics"""
    __tablename__ = 'class_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    total_students = db.Column(db.Integer, nullable=False)
    passed_students = db.Column(db.Integer, nullable=False)
    failed_students = db.Column(db.Integer, nullable=False)
    average_cgpa = db.Column(db.Float, nullable=False)
    topper_student_id = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<ClassStatistics Y{self.year}S{self.semester}: {self.total_students} students>'
