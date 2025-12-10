/**
 * Swipe Gesture Support for Mobile Navigation
 * Enables swipe left/right to navigate between pages
 * Optimized for fast, responsive swipes
 */

(function() {
    'use strict';
    
    // Configuration - optimized for faster response
    const SWIPE_THRESHOLD = 40; // Reduced from 50 - easier to trigger
    const SWIPE_VELOCITY = 0.15; // Reduced from 0.3 - less strict
    const MAX_VERTICAL_SWIPE = 40; // Increased from 30 - more forgiving
    
    let touchStartX = 0;
    let touchStartY = 0;
    let touchStartTime = 0;
    
    // Cache navigation items for performance
    let cachedNavItems = null;
    let cachedActiveIndex = -1;
    
    // Get navigation items - with caching
    function getNavigationItems() {
        if (cachedNavItems) return cachedNavItems;
        
        const navBar = document.querySelector('.nav-bar');
        if (!navBar) {
            cachedNavItems = [];
            return [];
        }
        
        cachedNavItems = Array.from(navBar.querySelectorAll('.nav-item'));
        return cachedNavItems;
    }
    
    // Get current active page index - with caching
    function getCurrentPageIndex() {
        if (cachedActiveIndex !== -1) return cachedActiveIndex;
        
        const items = getNavigationItems();
        if (items.length === 0) return -1;
        
        const activeItem = items.find(item => item.classList.contains('active'));
        cachedActiveIndex = activeItem ? items.indexOf(activeItem) : -1;
        return cachedActiveIndex;
    }
    
    // Clear cache when needed
    function clearCache() {
        cachedNavItems = null;
        cachedActiveIndex = -1;
    }
    
    // Navigate to next/previous page - optimized for speed
    function navigateToPage(direction) {
        const items = getNavigationItems();
        if (items.length === 0) return;
        
        const currentIndex = getCurrentPageIndex();
        if (currentIndex === -1) return;
        
        let targetIndex;
        if (direction === 'left') {
            // Swipe left = go to next page
            targetIndex = (currentIndex + 1) % items.length;
        } else {
            // Swipe right = go to previous page
            targetIndex = (currentIndex - 1 + items.length) % items.length;
        }
        
        const targetItem = items[targetIndex];
        if (targetItem && targetItem.href) {
            // Navigate immediately - no delay
            window.location.href = targetItem.href;
        }
    }
    
    // Handle touch start - optimized
    function handleTouchStart(e) {
        const target = e.target;
        
        // Only skip if touching active form elements (typing/selecting)
        // Allow swipes everywhere else, including blank spaces
        if (target.tagName === 'INPUT' || 
            target.tagName === 'TEXTAREA' || 
            target.tagName === 'SELECT') {
            // Only block if the element is focused/active
            if (document.activeElement === target) {
                return; // User is typing, don't interfere
            }
        }
        
        // Allow swipes on contenteditable only if not focused
        if (target.isContentEditable && document.activeElement === target) {
            return;
        }
        
        // Record touch for all other cases (including blank spaces)
        // Handle both touches array and changedTouches for better compatibility
        const touch = e.touches && e.touches[0] ? e.touches[0] : (e.changedTouches && e.changedTouches[0] ? e.changedTouches[0] : null);
        
        if (touch) {
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            touchStartTime = performance.now();
        }
    }
    
    // Handle touch end - optimized for speed
    function handleTouchEnd(e) {
        if (!touchStartX || !touchStartY) return;
        
        const touch = e.changedTouches[0];
        const touchEndX = touch.clientX;
        const touchEndY = touch.clientY;
        
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        const deltaTime = performance.now() - touchStartTime;
        
        // Quick validation - exit early if not a swipe
        const absDeltaX = Math.abs(deltaX);
        const absDeltaY = Math.abs(deltaY);
        
        // Reset immediately
        const wasSwipe = absDeltaX > SWIPE_THRESHOLD && 
                        absDeltaY < MAX_VERTICAL_SWIPE &&
                        deltaTime < 500; // Max 500ms for swipe
        
        touchStartX = 0;
        touchStartY = 0;
        
        if (!wasSwipe) return;
        
        // Calculate velocity only if needed
        const velocity = absDeltaX / deltaTime;
        if (velocity < SWIPE_VELOCITY) return;
        
        // Navigate immediately
        if (deltaX > 0) {
            navigateToPage('right');
        } else {
            navigateToPage('left');
        }
    }
    
    // Initialize swipe gestures - optimized
    function initSwipeGestures() {
        // Only enable on mobile devices
        if (!('ontouchstart' in window || navigator.maxTouchPoints > 0)) {
            return;
        }
        
        // Attach to both body and document for maximum coverage
        // This ensures blank spaces and all areas can detect swipes
        const container = document.body;
        const doc = document.documentElement;
        
        // Use capture phase to catch events early, including blank spaces
        container.addEventListener('touchstart', handleTouchStart, { 
            passive: true, 
            capture: true  // Capture phase catches events earlier
        });
        container.addEventListener('touchend', handleTouchEnd, { 
            passive: true, 
            capture: true 
        });
        
        // Also attach to document element for blank space areas
        doc.addEventListener('touchstart', handleTouchStart, { 
            passive: true, 
            capture: true 
        });
        doc.addEventListener('touchend', handleTouchEnd, { 
            passive: true, 
            capture: true 
        });
        
        // Clear cache when page changes (for SPA-like behavior)
        window.addEventListener('pageshow', clearCache);
        
        // Clear cache on navigation
        const originalPushState = history.pushState;
        history.pushState = function() {
            clearCache();
            return originalPushState.apply(history, arguments);
        };
    }
    
    // Initialize immediately if DOM is ready, otherwise wait
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSwipeGestures);
    } else {
        // Use requestAnimationFrame for better performance
        requestAnimationFrame(initSwipeGestures);
    }
})();

