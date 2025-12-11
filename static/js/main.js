/**
 * Short Media Platform - Main JavaScript
 */

// Auto-dismiss alerts after 5 seconds (only for success/info/warning messages, not errors)
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Only auto-dismiss success, info, and warning messages
        // Keep error messages visible until manually dismissed
        const isError = alert.classList.contains('alert-error') ||
                       alert.classList.contains('alert-danger') ||
                       alert.textContent.toLowerCase().includes('error') ||
                       alert.textContent.toLowerCase().includes('failed');

        if (!isError) {
            setTimeout(() => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 500);
            }, 5000);
        } else {
            // Add manual dismiss button for error messages
            if (!alert.querySelector('.alert-dismiss')) {
                const dismissBtn = document.createElement('button');
                dismissBtn.className = 'alert-dismiss';
                dismissBtn.innerHTML = '×';
                dismissBtn.style.cssText = 'position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; font-size: 1.5rem; cursor: pointer; color: inherit; opacity: 0.7; padding: 0; width: 24px; height: 24px; line-height: 1;';
                dismissBtn.onmouseover = function() { this.style.opacity = '1'; };
                dismissBtn.onmouseout = function() { this.style.opacity = '0.7'; };
                dismissBtn.onclick = function() {
                    alert.style.transition = 'opacity 0.3s ease';
                    alert.style.opacity = '0';
                    setTimeout(() => alert.remove(), 300);
                };
                alert.style.position = 'relative';
                alert.style.paddingRight = '40px';
                alert.appendChild(dismissBtn);
            }
        }
    });
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Remove validation error on input
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('is-invalid')) {
        e.target.classList.remove('is-invalid');
    }
});

// Prevent double form submission
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');

    if (submitButton && !submitButton.disabled) {
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';

        // Re-enable after 3 seconds as fallback
        setTimeout(() => {
            submitButton.disabled = false;
            submitButton.textContent = submitButton.getAttribute('data-original-text') || 'Submit';
        }, 3000);
    }
});
