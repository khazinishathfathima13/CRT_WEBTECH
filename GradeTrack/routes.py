from flask import render_template, request, redirect, url_for, jsonify, make_response
from app import app, db
from models import Student, TheorySubject, LabCourse, ClassStatistics
from sqlalchemy import func
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import logging

@app.route('/')
def index():
    """Homepage with search form"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_student():
    """Search for student and redirect to result page"""
    student_id = request.form.get('student_id', '').strip()
    year = request.form.get('year', type=int)
    semester = request.form.get('semester', type=int)
    
    if not all([student_id, year, semester]):
        return redirect(url_for('index'))
    
    # Check if student exists
    student = Student.query.filter_by(
        student_id=student_id, 
        year=year, 
        semester=semester
    ).first()
    
    if not student:
        return render_template('index.html', error="Student not found for the specified year and semester.")
    
    return redirect(url_for('result', student_id=student_id, year=year, semester=semester))

@app.route('/result/<student_id>/<int:year>/<int:semester>')
def result(student_id, year, semester):
    """Display student result page"""
    # Get student data
    student = Student.query.filter_by(
        student_id=student_id, 
        year=year, 
        semester=semester
    ).first()
    
    if not student:
        return redirect(url_for('index'))
    
    # Get class statistics
    stats = get_class_statistics(year, semester)
    
    # Get chart data
    chart_data = get_chart_data(student)
    
    return render_template('result.html', 
                         student=student, 
                         stats=stats, 
                         chart_data=chart_data)

@app.route('/download_pdf/<student_id>/<int:year>/<int:semester>')
def download_pdf(student_id, year, semester):
    """Generate and download PDF report"""
    student = Student.query.filter_by(
        student_id=student_id, 
        year=year, 
        semester=semester
    ).first()
    
    if not student:
        return redirect(url_for('index'))
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    # Add college header
    college_header = Paragraph("ANANTHA LAKSHMI INSTITUTE OF TECHNOLOGY AND<br/>SCIENCES", title_style)
    elements.append(college_header)
    elements.append(Spacer(1, 20))
    
    # Add report title
    report_title = Paragraph("ACADEMIC PERFORMANCE REPORT", header_style)
    elements.append(report_title)
    elements.append(Spacer(1, 30))
    
    # Student information
    student_info_data = [
        ['Student Name:', student.name],
        ['Student ID:', student.student_id],
        ['Year:', f'{student.year} Year'],
        ['Semester:', f'{student.semester} Semester'],
        ['CGPA:', str(student.calculate_cgpa())],
        ['Percentage:', f'{student.calculate_percentage()}%'],
        ['Result:', student.get_result_status()]
    ]
    
    student_info_table = Table(student_info_data, colWidths=[2*inch, 3*inch])
    student_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(student_info_table)
    elements.append(Spacer(1, 30))
    
    # Theory subjects header
    subjects_header = Paragraph("SUBJECTS", styles['Heading3'])
    elements.append(subjects_header)
    elements.append(Spacer(1, 10))
    
    # Theory subjects table
    theory_data = [['Subject Name', 'Marks', 'Grade']]
    for subject in student.theory_subjects:
        theory_data.append([subject.subject_name, str(subject.marks), subject.grade])
    
    theory_table = Table(theory_data, colWidths=[3*inch, 1*inch, 1*inch])
    theory_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(theory_table)
    elements.append(Spacer(1, 30))
    
    # Laboratory courses header
    lab_header = Paragraph("LABORATORY COURSES", styles['Heading3'])
    elements.append(lab_header)
    elements.append(Spacer(1, 10))
    
    # Lab courses table
    lab_data = [['Lab Name', 'Internal', 'External', 'Total', 'Grade']]
    for lab in student.lab_courses:
        lab_data.append([
            lab.lab_name, 
            str(lab.internal_marks), 
            str(lab.external_marks), 
            str(lab.total_marks), 
            lab.grade
        ])
    
    lab_table = Table(lab_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    lab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(lab_table)
    
    # Build PDF
    doc.build(elements)
    
    # FileResponse
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{student_id}_result.pdf"'
    
    return response

def get_class_statistics(year, semester):
    """Get class statistics for the given year and semester"""
    # Get all students for this year and semester
    students = Student.query.filter_by(year=year, semester=semester).all()
    
    if not students:
        return {
            'total_students': 0,
            'passed': 0,
            'failed': 0,
            'average_cgpa': 0.0
        }
    
    total_students = len(students)
    passed = sum(1 for s in students if s.get_result_status() == 'PASS')
    failed = total_students - passed
    
    # Calculate average CGPA
    cgpas = [s.calculate_cgpa() for s in students if s.calculate_cgpa() > 0]
    average_cgpa = round(sum(cgpas) / len(cgpas), 2) if cgpas else 0.0
    
    return {
        'total_students': total_students,
        'passed': passed,
        'failed': failed,
        'average_cgpa': average_cgpa
    }

def get_chart_data(student):
    """Get chart data for student performance visualization"""
    subjects_data = []
    grades_data = []
    
    # Theory subjects
    for subject in student.theory_subjects:
        subjects_data.append({
            'name': subject.subject_name,
            'marks': subject.marks,
            'grade_point': Student.get_grade_point(subject.grade)
        })
    
    # Lab courses
    for lab in student.lab_courses:
        subjects_data.append({
            'name': lab.lab_name,
            'marks': lab.total_marks,
            'grade_point': Student.get_grade_point(lab.grade)
        })
    
    return {
        'subjects': [item['name'] for item in subjects_data],
        'marks': [item['marks'] for item in subjects_data],
        'grade_points': [item['grade_point'] for item in subjects_data]
    }
