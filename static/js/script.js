document.addEventListener('DOMContentLoaded', function() {
    // Sample query buttons functionality
    window.sampleQuery = function(query) {
        document.querySelector('input[name="query"]').value = query;
    };
    
    // Form submission with loading indicator
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Processing...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // AJAX for sample data generation
    const sampleDataForm = document.getElementById('sampleDataForm');
    if (sampleDataForm) {
        sampleDataForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Generating...';
            submitBtn.disabled = true;
            
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Sample data generated successfully!');
                submitBtn.innerHTML = '<i class="fas fa-magic me-1"></i> Generate';
                submitBtn.disabled = false;
            })
            .catch(error => {
                alert('Error generating sample data');
                submitBtn.innerHTML = '<i class="fas fa-magic me-1"></i> Generate';
                submitBtn.disabled = false;
            });
        });
    }
});
