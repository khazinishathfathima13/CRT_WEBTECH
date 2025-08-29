/**
 * PDF Generation Utilities
 * Handles client-side PDF generation and print functionality
 */

/**
 * Generate PDF from current page content
 */
function generatePDF() {
    // Get the result content
    const element = document.querySelector('.result-section');
    if (!element) {
        console.error('Result section not found');
        return;
    }

    // Configure PDF options
    const options = {
        margin: [0.5, 0.5, 0.5, 0.5],
        filename: `academic_result_${new Date().getTime()}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2,
            useCORS: true,
            logging: false
        },
        jsPDF: { 
            unit: 'in', 
            format: 'a4', 
            orientation: 'portrait' 
        }
    };

    // Generate PDF
    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(options).from(element).save();
    } else {
        console.error('html2pdf library not loaded');
        // Fallback to browser print
        window.print();
    }
}

/**
 * Enhanced print functionality
 */
function printResult() {
    // Add print-specific styles
    const printStyles = `
        <style media="print">
            @page {
                margin: 0.5in;
                size: A4;
            }
            
            body * {
                visibility: hidden;
            }
            
            .result-section, .result-section * {
                visibility: visible;
            }
            
            .result-section {
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
            }
            
            .print-hidden {
                display: none !important;
            }
            
            .college-header {
                background: #2d3748 !important;
                color: white !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            .section-title {
                background: #2d3748 !important;
                color: white !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            .grade-badge {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            .chart-container {
                page-break-inside: avoid;
            }
        </style>
    `;
    
    // Add styles to head
    const head = document.head || document.getElementsByTagName('head')[0];
    const style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = printStyles;
    head.appendChild(style);
    
    // Print
    window.print();
    
    // Remove added styles after printing
    setTimeout(() => {
        head.removeChild(style);
    }, 1000);
}

/**
 * Download functionality
 */
function downloadResult() {
    // Check if we're on the result page
    const currentPath = window.location.pathname;
    if (currentPath.includes('/result/')) {
        // Extract student info from URL
        const pathParts = currentPath.split('/');
        const studentId = pathParts[2];
        const year = pathParts[3];
        const semester = pathParts[4];
        
        // Navigate to PDF download endpoint
        window.location.href = `/download_pdf/${studentId}/${year}/${semester}`;
    } else {
        console.error('Not on result page');
    }
}

/**
 * Initialize PDF functionality when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to print and download buttons
    const printButtons = document.querySelectorAll('[onclick="window.print()"]');
    printButtons.forEach(button => {
        button.removeAttribute('onclick');
        button.addEventListener('click', printResult);
    });
    
    // Add download functionality
    const downloadButtons = document.querySelectorAll('a[href*="download_pdf"]');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Let the default behavior handle the download
            console.log('Downloading PDF...');
        });
    });
    
    console.log('PDF generator module loaded successfully');
});

/**
 * Export functions for use in templates
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generatePDF,
        printResult,
        downloadResult
    };
}
