/**
 * Academic Performance Chart Generator
 * Creates Chart.js visualizations for student performance
 */

function initializePerformanceChart(chartData) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) {
        console.error('Chart canvas not found');
        return;
    }

    // Chart configuration matching the screenshot design
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.subjects,
            datasets: [
                {
                    label: 'Marks',
                    data: chartData.marks,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    yAxisID: 'y',
                    type: 'bar'
                },
                {
                    label: 'Grade Points',
                    data: chartData.grade_points,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 3,
                    fill: false,
                    yAxisID: 'y1',
                    type: 'line',
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            family: 'Poppins',
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                if (context.dataset.label === 'Marks') {
                                    label += context.parsed.y + '/100';
                                } else {
                                    label += context.parsed.y + '/10';
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            family: 'Poppins',
                            size: 10
                        }
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Marks (out of 100)',
                        font: {
                            family: 'Poppins',
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    min: 0,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        font: {
                            family: 'Poppins',
                            size: 10
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Grade Points (out of 10)',
                        font: {
                            family: 'Poppins',
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    min: 0,
                    max: 10,
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        font: {
                            family: 'Poppins',
                            size: 10
                        }
                    }
                },
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            }
        }
    });

    return chart;
}

/**
 * Initialize chart when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Chart will be initialized by the template script
    console.log('Chart.js module loaded successfully');
});

/**
 * Export functions for use in templates
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializePerformanceChart
    };
}
