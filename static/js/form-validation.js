/**
 * Form Validation Utilities
 * Client-side validation for all forms
 */

// Validate phone number (10 digits)
function validatePhone(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
}

// Validate required fields
function validateRequired(value) {
    return value && value.trim().length > 0;
}

// Validate email (if needed)
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show field error
function showFieldError(field, message) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        // Create error element if it doesn't exist
        const input = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
        if (input) {
            const error = document.createElement('div');
            error.id = `${field}-error`;
            error.className = 'field-error';
            error.style.cssText = 'color: #EF4444; font-size: 0.875rem; margin-top: 0.25rem;';
            error.textContent = message;
            input.parentNode.appendChild(error);
        }
    }
    
    // Add error class to input
    const input = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
    if (input) {
        input.style.borderColor = '#EF4444';
    }
}

// Clear field error
function clearFieldError(field) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
    
    const input = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
    if (input) {
        input.style.borderColor = '';
    }
}

// Validate student form
function validateStudentForm() {
    let isValid = true;
    
    const name = document.getElementById('name')?.value.trim();
    const phone = document.getElementById('phone')?.value.trim();
    const batchId = document.getElementById('batch_id')?.value;
    
    // Validate name
    if (!validateRequired(name)) {
        showFieldError('name', 'Student name is required');
        isValid = false;
    } else {
        clearFieldError('name');
    }
    
    // Validate phone
    if (!validateRequired(phone)) {
        showFieldError('phone', 'Phone number is required');
        isValid = false;
    } else if (!validatePhone(phone)) {
        showFieldError('phone', 'Please enter a valid 10-digit phone number');
        isValid = false;
    } else {
        clearFieldError('phone');
    }
    
    // Validate batch
    if (!batchId || batchId === '') {
        showFieldError('batch_id', 'Please select a batch');
        isValid = false;
    } else {
        clearFieldError('batch_id');
    }
    
    return isValid;
}

// Validate batch form
function validateBatchForm() {
    let isValid = true;
    
    const name = document.getElementById('name')?.value.trim();
    
    if (!validateRequired(name)) {
        showFieldError('name', 'Batch name is required');
        isValid = false;
    } else {
        clearFieldError('name');
    }
    
    return isValid;
}

// Validate homework form
function validateHomeworkForm() {
    let isValid = true;
    
    const title = document.getElementById('title')?.value.trim();
    const batchId = document.getElementById('batch_id')?.value;
    const studentId = document.getElementById('student_id')?.value;
    
    if (!validateRequired(title)) {
        showFieldError('title', 'Homework title is required');
        isValid = false;
    } else {
        clearFieldError('title');
    }
    
    if (!batchId && !studentId) {
        showFieldError('batch_id', 'Please select either a batch or student');
        isValid = false;
    } else {
        clearFieldError('batch_id');
        clearFieldError('student_id');
    }
    
    return isValid;
}

// Prevent duplicate form submission
function preventDuplicateSubmission(formId) {
    const form = document.getElementById(formId) || document.querySelector(`form[action*="${formId}"]`);
    if (form) {
        let isSubmitting = false;
        form.addEventListener('submit', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                return false;
            }
            isSubmitting = true;
            
            // Disable submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('btn-loading');
            }
            
            // Re-enable after 3 seconds (in case of error)
            setTimeout(() => {
                isSubmitting = false;
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('btn-loading');
                }
            }, 3000);
        });
    }
}

// Auto-format phone number input
function formatPhoneInput(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.addEventListener('input', function(e) {
            // Remove non-numeric characters
            this.value = this.value.replace(/[^0-9]/g, '');
            // Limit to 10 digits
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    }
}

// Validate batch form
function validateBatchForm() {
    let isValid = true;
    
    const name = document.getElementById('name')?.value.trim();
    const startTime = document.getElementById('start_time')?.value;
    const endTime = document.getElementById('end_time')?.value;
    const dayCheckboxes = document.querySelectorAll('.day-checkbox');
    const hasDaySelected = Array.from(dayCheckboxes).some(cb => cb.checked);
    
    if (!validateRequired(name)) {
        showFieldError('name', 'Batch name is required');
        isValid = false;
    } else if (name.length < 2) {
        showFieldError('name', 'Batch name must be at least 2 characters long');
        isValid = false;
    } else if (name.length > 100) {
        showFieldError('name', 'Batch name must be 100 characters or less');
        isValid = false;
    } else {
        clearFieldError('name');
    }
    
    // Validate time if provided
    if (startTime && endTime) {
        if (startTime >= endTime) {
            showFieldError('end_time', 'End time must be after start time');
            isValid = false;
        } else {
            clearFieldError('end_time');
        }
    }
    
    return isValid;
}

// Validate homework form
function validateHomeworkForm() {
    let isValid = true;
    
    const title = document.getElementById('title')?.value.trim();
    const batchId = document.getElementById('batch_id')?.value;
    const studentId = document.getElementById('student_id')?.value;
    const submissionDate = document.getElementById('submission_date')?.value;
    const fileInput = document.getElementById('file');
    
    if (!validateRequired(title)) {
        showFieldError('title', 'Homework title is required');
        isValid = false;
    } else {
        clearFieldError('title');
    }
    
    if (!submissionDate) {
        showFieldError('submission_date', 'Submission date is required');
        isValid = false;
    } else {
        clearFieldError('submission_date');
    }
    
    // Validate file size if file is selected
    if (fileInput && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            showFieldError('file', 'File size must be less than 10MB');
            isValid = false;
        } else {
            clearFieldError('file');
        }
    }
    
    return isValid;
}

// Initialize form validation on page load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-format phone inputs
    formatPhoneInput('phone');
    formatPhoneInput('mobile');
    formatPhoneInput('mobile-login');
    formatPhoneInput('mobile-signup');
    
    // Prevent duplicate submissions for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        preventDuplicateSubmission(form.id || form.action);
        
        // Add validation based on form action
        if (form.action.includes('add_student') || form.action.includes('edit_student')) {
            form.addEventListener('submit', function(e) {
                if (!validateStudentForm()) {
                    e.preventDefault();
                    return false;
                }
            });
        } else if (form.action.includes('add_batch') || form.action.includes('edit_batch')) {
            form.addEventListener('submit', function(e) {
                if (!validateBatchForm()) {
                    e.preventDefault();
                    return false;
                }
            });
        } else if (form.action.includes('share_homework') || form.action.includes('edit_homework')) {
            form.addEventListener('submit', function(e) {
                if (!validateHomeworkForm()) {
                    e.preventDefault();
                    return false;
                }
            });
        }
    });
});

