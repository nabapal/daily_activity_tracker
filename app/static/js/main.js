document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm before deleting
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Dashboard-Specific JavaScript
    if (document.querySelector('.dashboard-container')) {
        // Initialize Status Chart
        const ctx = document.getElementById('statusChart');
        if (ctx) {
            const statusData = {
                completed: document.querySelector('.metric-card.completed-card .metric-value').textContent.trim(),
                inProgress: document.querySelector('.metric-card.progress-card .metric-value').textContent.trim(),
                onHold: document.querySelector('.metric-card.hold-card .metric-value').textContent.trim(),
                pending: document.querySelector('.metric-card.pending-card .metric-value').textContent.trim()
            };

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress', 'On Hold', 'Yet To Start'],
                    datasets: [{
                        data: [
                            statusData.completed,
                            statusData.inProgress,
                            statusData.onHold,
                            statusData.pending
                        ],
                        backgroundColor: [
                            '#2ecc71',
                            '#3498db',
                            '#e74c3c',
                            '#f39c12'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    cutout: '70%',
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
        }

        // Initialize Date Range Picker
        const dateRangeInput = document.querySelector('.flatpickr');
        if (dateRangeInput) {
            flatpickr(dateRangeInput, {
                mode: "range",
                dateFormat: "Y-m-d",
                defaultDate: [new Date(), new Date(new Date().setDate(new Date().getDate() + 7))],
                onChange: function(selectedDates) {
                    if (selectedDates.length === 2) {
                        const start = selectedDates[0].toLocaleDateString();
                        const end = selectedDates[1].toLocaleDateString();
                        document.getElementById('current-date-range').textContent = `${start} - ${end}`;
                        // Here you would typically reload data or filter the timeline
                    }
                }
            });
        }

        // Timeline Item Interactions
        document.querySelectorAll('.timeline-item').forEach(item => {
            item.addEventListener('click', function(e) {
                if (!e.target.closest('.btn-action')) {
                    this.querySelector('.timeline-content').classList.toggle('expanded');
                }
            });
        });

        // Update status buttons
        document.querySelectorAll('.btn-action.update-status').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const activityId = this.closest('.timeline-item').querySelector('.activity-id').textContent;
                // Implement your status update modal here
                console.log(`Update status for ${activityId}`);
            });
        });
    }

    // Responsive adjustments
    function handleResponsive() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        if (window.innerWidth < 768) {
            timelineItems.forEach(item => {
                item.querySelector('.timeline-actions').classList.add('flex-column');
            });
        } else {
            timelineItems.forEach(item => {
                item.querySelector('.timeline-actions').classList.remove('flex-column');
            });
        }
    }

    window.addEventListener('resize', handleResponsive);
    handleResponsive();
});