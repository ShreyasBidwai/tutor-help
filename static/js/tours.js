/**
 * Onboarding Tours Configuration
 * Mobile-first tours for tutors and students
 */

// Check if user has completed onboarding
function hasCompletedOnboarding(role) {
    const key = role === 'student' ? 'student_onboarding_completed' : 'tutor_onboarding_completed';
    return localStorage.getItem(key) === 'true';
}

// Mark onboarding as completed
function markOnboardingCompleted(role) {
    const key = role === 'student' ? 'student_onboarding_completed' : 'tutor_onboarding_completed';
    localStorage.setItem(key, 'true');
    // Also update in database via API (only for tutors)
    if (role !== 'student') {
        fetch('/api/onboarding/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).catch(err => console.error('Error marking onboarding complete:', err));
    }
}

// Tutor Dashboard Tour
const tutorTourSteps = [
    {
        element: '[data-intro-step="1"]',
        intro: '<div style="text-align: center; margin-bottom: 1rem;"><div style="font-size: 3rem; margin-bottom: 0.5rem;">👋</div><h3 style="margin: 0 0 0.5rem 0; color: #111827; font-size: 1.25rem;">Welcome to TuitionTrack!</h3></div>Here you can see quick stats about your students, batches, and today\'s attendance at a glance. Tap any card to view details.',
        position: 'bottom'
    },
    {
        element: '[data-intro-step="2"]',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Quick Actions</h3>Use these buttons to quickly add students, create batches, or share homework with your students. Everything you need is just one tap away!',
        position: 'bottom'
    },
    {
        element: '.nav-bar',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Navigation Menu</h3>Navigate easily using the bottom menu:<br><br><strong>🏠 Home</strong> - Your dashboard<br><strong>👥 Students</strong> - Manage all students<br><strong>📊 Attendance</strong> - Mark daily attendance<br><strong>📝 Homework</strong> - Share assignments<br><strong>💳 Payments</strong> - Pro features',
        position: 'top'
    },
    {
        element: '.header',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Your Profile</h3>Your tuition name appears here. Tap the profile icon to edit your details and manage your account settings.',
        position: 'bottom'
    }
];

// Student Dashboard Tour
const studentTourSteps = [
    {
        element: '[data-intro-step="1"]',
        intro: '<div style="text-align: center; margin-bottom: 1rem;"><div style="font-size: 3rem; margin-bottom: 0.5rem;">👋</div><h3 style="margin: 0 0 0.5rem 0; color: #111827; font-size: 1.25rem;">Welcome!</h3></div>Here you can see your attendance percentage, recent homework count, and batch information at a glance.',
        position: 'bottom'
    },
    {
        element: '[data-intro-step="2"]',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Today\'s Attendance</h3>Check your attendance status for today. You\'ll see if you\'re marked as <strong>Present</strong> ✓, <strong>Late</strong> ⏰, or <strong>Absent</strong> ✗.',
        position: 'bottom'
    },
    {
        element: '[data-intro-step="3"]',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Upcoming Classes</h3>View your upcoming classes here. This helps you stay prepared for your next batch and never miss a class!',
        position: 'bottom'
    },
    {
        element: '[data-intro-step="4"]',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Recent Homework</h3>See your recent homework assignments here. Click <strong>"View All"</strong> to see all your homework and track your progress.',
        position: 'bottom'
    },
    {
        element: '.nav-bar',
        intro: '<h3 style="margin: 0 0 0.75rem 0; color: #111827; font-size: 1.125rem;">Navigation Menu</h3>Use the bottom menu to navigate:<br><br><strong>🏠 Home</strong> - Your dashboard<br><strong>📊 Attendance</strong> - View your attendance calendar<br><strong>📝 Homework</strong> - See all assignments',
        position: 'top'
    }
];

// Start Tutor Tour
function startTutorTour() {
    // Wait for DOM to be fully ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            startTutorTourNow();
        });
    } else {
        startTutorTourNow();
    }
}

function startTutorTourNow() {
    // Verify elements exist before starting - with retry logic
    const steps = [];
    
    tutorTourSteps.forEach((step, index) => {
        if (step.element) {
            // Try multiple times to find element
            let element = null;
            for (let i = 0; i < 10; i++) {
                element = document.querySelector(step.element);
                if (element) break;
                // Wait a bit before retrying
                if (i < 9) {
                    const start = Date.now();
                    while (Date.now() - start < 100) {} // Small delay
                }
            }
            
            if (element) {
                // For first two steps, be more lenient with visibility check
                // They might be off-screen initially but should be scrolled into view
                if (index < 2) {
                    // Just check if element exists in DOM, visibility will be handled by scrollToElement
                    steps.push(step);
                } else {
                    // For other steps, check visibility
                    const rect = element.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        steps.push(step);
                    } else {
                        console.warn('Tour step element not visible:', step.element);
                        // Still add it - scrollToElement will handle it
                        steps.push(step);
                    }
                }
            } else {
                console.warn('Tour step element not found after retries:', step.element, 'at index', index);
                // Don't skip first two steps - they're critical
                if (index < 2) {
                    console.error('Critical tour step missing!', step.element);
                }
            }
        } else {
            // Allow steps without elements (floating tooltips)
            steps.push(step);
        }
    });
    
    if (steps.length === 0) {
        console.error('No valid tour steps found. Available elements:', {
            step1: document.querySelector('[data-intro-step="1"]'),
            step2: document.querySelector('[data-intro-step="2"]'),
            navBar: document.querySelector('.nav-bar'),
            header: document.querySelector('.header')
        });
        return;
    }
    
    // Ensure we have at least the first step
    if (steps.length < tutorTourSteps.length) {
        console.warn('Some tour steps were filtered out. Expected', tutorTourSteps.length, 'got', steps.length);
    }
    
    console.log('Starting tutor tour with', steps.length, 'steps. First step element:', steps[0]?.element);
    
    introJs().setOptions({
        steps: steps,
        showProgress: true,
        showBullets: false,
        exitOnOverlayClick: false,
        exitOnEsc: true,
        nextLabel: 'Next',
        prevLabel: 'Previous',
        skipLabel: 'Skip Tour',
        doneLabel: 'Got it!',
        tooltipClass: 'customTooltip',
        highlightClass: 'customHighlight',
        buttonClass: 'customButton',
        disableInteraction: true,
        scrollToElement: true,
        scrollPadding: 20, // Increased padding for better visibility
        tooltipPosition: 'auto',
        highlight: true // Ensure highlighting is enabled
    }).onexit(function() {
        markOnboardingCompleted('tutor');
    }).oncomplete(function() {
        markOnboardingCompleted('tutor');
    }).start();
}

// Start Student Tour
function startStudentTour() {
    // Wait for DOM to be fully ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            startStudentTourNow();
        });
    } else {
        startStudentTourNow();
    }
}

function startStudentTourNow() {
    // Verify elements exist before starting - with retry logic
    const steps = [];
    
    studentTourSteps.forEach((step, index) => {
        if (step.element) {
            // Try multiple times to find element
            let element = null;
            for (let i = 0; i < 5; i++) {
                element = document.querySelector(step.element);
                if (element) break;
                // Wait a bit before retrying
                if (i < 4) {
                    const start = Date.now();
                    while (Date.now() - start < 50) {} // Small delay
                }
            }
            
            if (element) {
                // Ensure element is visible
                const rect = element.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    steps.push(step);
                } else {
                    console.warn('Tour step element not visible:', step.element);
                }
            } else {
                console.warn('Tour step element not found after retries:', step.element);
            }
        } else {
            // Allow steps without elements (floating tooltips)
            steps.push(step);
        }
    });
    
    if (steps.length === 0) {
        console.error('No valid tour steps found. Available elements:', {
            step1: document.querySelector('[data-intro-step="1"]'),
            step2: document.querySelector('[data-intro-step="2"]'),
            step3: document.querySelector('[data-intro-step="3"]'),
            step4: document.querySelector('[data-intro-step="4"]'),
            navBar: document.querySelector('.nav-bar')
        });
        return;
    }
    
    console.log('Starting student tour with', steps.length, 'steps');
    
    introJs().setOptions({
        steps: steps,
        showProgress: true,
        showBullets: false,
        exitOnOverlayClick: false,
        exitOnEsc: true,
        nextLabel: 'Next',
        prevLabel: 'Previous',
        skipLabel: 'Skip Tour',
        doneLabel: 'Got it!',
        tooltipClass: 'customTooltip',
        highlightClass: 'customHighlight',
        buttonClass: 'customButton',
        disableInteraction: true,
        scrollToElement: true,
        scrollPadding: 10,
        tooltipPosition: 'auto',
        highlight: true // Ensure highlighting is enabled
    }).onexit(function() {
        markOnboardingCompleted('student');
    }).oncomplete(function() {
        markOnboardingCompleted('student');
    }).start();
}

// Auto-start tour if onboarding not completed
// DISABLED: Onboarding tours are currently disabled
function checkAndStartTour(role) {
    // Tours are disabled - do nothing
    return;
    
    // Check localStorage first (faster)
    if (hasCompletedOnboarding(role)) {
        return;
    }
    
    // Wait for page to be fully loaded and rendered
    if (document.readyState === 'complete') {
        setTimeout(function() {
            if (role === 'tutor' || role === undefined) {
                startTutorTour();
            } else if (role === 'student') {
                startStudentTour();
            }
        }, 800);
    } else {
        window.addEventListener('load', function() {
            setTimeout(function() {
                if (role === 'tutor' || role === undefined) {
                    startTutorTour();
                } else if (role === 'student') {
                    startStudentTour();
                }
            }, 800);
        });
    }
}

// Restart tour function - clears completion status and starts tour
function restartTour(role) {
    const key = role === 'student' ? 'student_onboarding_completed' : 'tutor_onboarding_completed';
    localStorage.removeItem(key);
    
    // Scroll to top immediately to ensure all elements are in view
    window.scrollTo({ top: 0, behavior: 'instant' });
    
    // Wait a bit for scroll to complete, then verify elements exist
    setTimeout(function() {
        // Force a reflow to ensure DOM is updated
        document.body.offsetHeight;
        
        // Verify first step element exists before starting
        const firstStepElement = role === 'student' 
            ? document.querySelector('[data-intro-step="1"]')
            : document.querySelector('[data-intro-step="1"]');
            
        if (!firstStepElement) {
            console.warn('First step element not found, waiting longer...');
            // Wait a bit more and try again
            setTimeout(function() {
                if (role === 'tutor' || role === undefined) {
                    startTutorTour();
                } else if (role === 'student') {
                    startStudentTour();
                }
            }, 500);
        } else {
            console.log('First step element found, starting tour');
            if (role === 'tutor' || role === undefined) {
                startTutorTour();
            } else if (role === 'student') {
                startStudentTour();
            }
        }
    }, 800);
}
