"""
Excel Data Import Script for Academic Performance Tracker
Imports real student data from Excel files and populates the database
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
        return None  # This will trigger "Result Not Found" display
    
    try:
        return int(float(marks))
    except (ValueError, TypeError):
        return None

def import_semester_data(excel_file, year, semester):
    """Import data from Excel file for specific year and semester"""
    print(f"Importing data from {excel_file} for Year {year}, Semester {semester}")
    
    if not os.path.exists(excel_file):
        print(f"File {excel_file} not found!")
        return
    
    try:
        # Read Excel file, skip first row (it contains NaN values)
        df = pd.read_excel(excel_file, header=1)
        print(f"Found {len(df)} rows in the Excel file")
        
        # Filter out rows where Student ID is NaN or empty
        df = df.dropna(subset=[df.columns[0]])
        df = df[df.iloc[:, 0] != 'STUDENT ID']  # Remove header row if it exists
        print(f"Processing {len(df)} valid student records")
        
        for index, row in df.iterrows():
            try:
                student_id = str(row.iloc[0]).strip()
                student_name = str(row.iloc[1]).strip()
                
                # Skip if invalid data
                if student_id in ['nan', 'NaN', ''] or student_name in ['nan', 'NaN', '']:
                    continue
                
                # Check if student already exists
                existing_student = Student.query.filter_by(
                    student_id=student_id, year=year, semester=semester
                ).first()
                
                if existing_student:
                    print(f"Student {student_id} already exists for Y{year}S{semester}, skipping...")
                    continue
                
                # Create new student
                student = Student(
                    student_id=student_id,
                    name=student_name,
                    year=year,
                    semester=semester
                )
                db.session.add(student)
                
                # Theory subjects - columns 2 to approximately 14 (varies by semester)
                theory_count = 0
                for col_idx in range(2, min(15, len(df.columns))):
                    col_name = df.columns[col_idx]
                    marks_value = row.iloc[col_idx]
                    
                    # Skip if this is a header column or empty
                    if pd.isna(marks_value) or str(col_name).startswith('Unnamed'):
                        continue
                    
                    cleaned_marks = clean_marks_value(marks_value)
                    
                    if cleaned_marks is not None or str(marks_value) == "LONG ABSENT":
                        theory_count += 1
                        # Use actual column name if available, otherwise generate name
                        subject_name = col_name if not str(col_name).startswith('Unnamed') else f"Theory Subject {theory_count} (Y{year}S{semester})"
                        
                        theory_subject = TheorySubject(
                            student_id=student_id,
                            subject_name=subject_name,
                            subject_code=f"TS{year}{semester}{theory_count:02d}",
                            marks=cleaned_marks if cleaned_marks is not None else 0,
                            grade=get_grade_from_marks(marks_value)
                        )
                        db.session.add(theory_subject)
                
                # Lab courses - starting from around column 15
                lab_count = 0
                labs_started = False
                current_lab_internal = None
                current_lab_external = None
                current_lab_total = None
                current_lab_name = None
                
                for col_idx in range(15, len(df.columns)):
                    col_name = str(df.columns[col_idx])
                    value = row.iloc[col_idx]
                    
                    # Detect lab sections
                    if 'LABS' in col_name or labs_started:
                        labs_started = True
                        
                        # Look for patterns: Internal, External, Total, Grade
                        if not pd.isna(value):
                            # Check if this might be total marks (usually higher numbers)
                            try:
                                num_value = float(value)
                                if 70 <= num_value <= 100:  # Likely total marks
                                    lab_count += 1
                                    current_lab_total = clean_marks_value(value)
                                    current_lab_name = f"Lab {lab_count} (Y{year}S{semester})"
                                    
                                    # Look backwards for internal/external
                                    if col_idx >= 2:
                                        prev_val1 = row.iloc[col_idx-1]
                                        prev_val2 = row.iloc[col_idx-2] if col_idx >= 3 else None
                                        
                                        current_lab_external = clean_marks_value(prev_val1)
                                        current_lab_internal = clean_marks_value(prev_val2)
                                    
                                    # Create lab course
                                    if current_lab_total is not None:
                                        lab_course = LabCourse(
                                            student_id=student_id,
                                            lab_name=current_lab_name,
                                            lab_code=f"LAB{year}{semester}{lab_count:02d}",
                                            internal_marks=current_lab_internal or 0,
                                            external_marks=current_lab_external or 0,
                                            total_marks=current_lab_total,
                                            grade=get_grade_from_marks(current_lab_total)
                                        )
                                        db.session.add(lab_course)
                                        
                            except (ValueError, TypeError):
                                continue
                
                print(f"Added: {student_id} - {student_name} (T:{theory_count}, L:{lab_count})")
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully imported data for Year {year}, Semester {semester}")
        
    except Exception as e:
        print(f"Error reading Excel file {excel_file}: {e}")
        db.session.rollback()

def main():
    """Main function to import all semester data"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Define your Excel files (update paths as needed)
        excel_files = [
            ("attached_assets/1-1 SEMESTER RESULTS_1756310639227.xlsx", 1, 1),
            ("attached_assets/1-2 SEMESTER RESULTS_1756310650480.xlsx", 1, 2),
            ("attached_assets/2-1 SEMESTER RESULTS_1756310657928.xlsx", 2, 1),
            ("attached_assets/2-2 SEMESTER RESULTS_1756310665347.xlsx", 2, 2),
        ]
        
        # Import data for each semester
        for excel_file, year, semester in excel_files:
            import_semester_data(excel_file, year, semester)
        
        print("Data import completed!")

if __name__ == '__main__':
    main()