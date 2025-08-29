# Academic Performance Tracking System

## Overview

The Academic Performance Tracking System is a Flask-based web application designed for B.Tech students, faculty, and parents at Anantha Lakshmi Institute of Technology and Sciences. The system provides instant access to academic results without requiring user authentication - users simply enter their Student ID, Year, and Semester to view comprehensive academic performance data.

The application displays results in a JNTU-style format, including theory subjects, laboratory courses, CGPA calculations, class statistics, and performance visualizations. It supports data for Years 1 & 2 across both semesters, with functionality for PDF generation and printing of results.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM for database operations
- **Database**: SQLite for lightweight, file-based data storage
- **Models**: Three primary entities - Student, TheorySubject, LabCourse, and ClassStatistics
- **Routing**: Simple route structure with homepage search, result display, and PDF generation endpoints
- **Grade Calculation**: Automated CGPA and percentage calculations using standard grading scale (S=10, A=9, B=8, C=7, D=6, E=5, F=FAIL)

### Frontend Architecture
- **Template Engine**: Jinja2 with base template inheritance
- **CSS Framework**: Bootstrap 5 for responsive design and component styling
- **Custom Styling**: CSS variables for consistent theming with professional academic appearance
- **JavaScript Libraries**: Chart.js for performance visualizations, html2pdf for client-side PDF generation
- **Responsive Design**: Mobile-friendly interface with gradient headers and card-based layouts

### Database Schema Design
- **Student Table**: Core student information (ID, name, year, semester)
- **TheorySubject Table**: Individual theory subject records with marks and calculated grades
- **LabCourse Table**: Laboratory course records with internal/external marks
- **Relational Structure**: One-to-many relationships between students and their academic records
- **Cascade Deletion**: Automatic cleanup of related records when students are removed

### Data Processing Logic
- **Grade Conversion**: Automatic conversion from numerical marks to letter grades
- **CGPA Calculation**: Weighted average considering theory subjects (4 credits) and labs (2 credits)
- **Performance Analytics**: Class-wide statistics including averages, pass/fail rates, and toppers
- **Chart Data Generation**: Server-side preparation of visualization data for frontend charts

### PDF and Print Functionality
- **Server-side PDF**: ReportLab integration for generating formatted PDF documents
- **Client-side PDF**: html2pdf.js for browser-based PDF generation as backup
- **Print Optimization**: CSS media queries for print-friendly layouts
- **Document Formatting**: JNTU-compliant result format with proper headers and styling

## External Dependencies

### Python Libraries
- **Flask**: Web framework for routing and request handling
- **SQLAlchemy**: Database ORM for model definitions and queries
- **ReportLab**: PDF generation library for creating formatted academic transcripts

### Frontend Libraries
- **Bootstrap 5**: CSS framework from CDN for responsive UI components
- **Font Awesome 6**: Icon library from CDN for consistent iconography
- **Google Fonts (Poppins)**: Typography from CDN for professional appearance
- **Chart.js**: Visualization library from CDN for performance charts
- **html2pdf.js**: Client-side PDF generation library for browser compatibility

### Database
- **SQLite**: Embedded database engine requiring no external server setup
- **File-based Storage**: Database stored as `academic_tracker.db` file in project directory

### Development Dependencies
- **Python 3.x**: Runtime environment
- **Flask Development Server**: Built-in server for local development and testing