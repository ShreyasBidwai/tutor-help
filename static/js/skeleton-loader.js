/**
 * Skeleton Loading Utility
 * Shows skeleton placeholders while content loads
 */

// Show skeleton and hide content
function showSkeleton(skeletonId, contentId) {
    const skeleton = document.getElementById(skeletonId);
    const content = document.getElementById(contentId);
    
    if (skeleton) {
        skeleton.classList.add('active');
    }
    if (content) {
        content.classList.add('content-loading');
        content.classList.remove('content-loaded');
    }
}

// Hide skeleton and show content
function hideSkeleton(skeletonId, contentId) {
    const skeleton = document.getElementById(skeletonId);
    const content = document.getElementById(contentId);
    
    if (skeleton) {
        skeleton.classList.remove('active');
    }
    if (content) {
        content.classList.remove('content-loading');
        content.classList.add('content-loaded');
    }
}

// Generate skeleton cards for list
function generateSkeletonCards(count, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const card = document.createElement('div');
        card.className = 'skeleton-card';
        card.innerHTML = `
            <div class="skeleton-header">
                <div class="skeleton skeleton-avatar"></div>
                <div style="flex: 1;">
                    <div class="skeleton skeleton-line skeleton-title"></div>
                    <div class="skeleton skeleton-line skeleton-text"></div>
                </div>
            </div>
            <div class="skeleton skeleton-line skeleton-text"></div>
            <div class="skeleton skeleton-line skeleton-text"></div>
        `;
        container.appendChild(card);
    }
}

// Generate skeleton list items
function generateSkeletonListItems(count, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const item = document.createElement('div');
        item.className = 'skeleton-list-item';
        item.innerHTML = `
            <div class="skeleton skeleton-list-avatar"></div>
            <div class="skeleton-list-content">
                <div class="skeleton skeleton-line skeleton-title"></div>
                <div class="skeleton skeleton-line skeleton-text"></div>
                <div class="skeleton skeleton-line skeleton-text short"></div>
            </div>
        `;
        container.appendChild(item);
    }
}

// Generate skeleton stats
function generateSkeletonStats(count, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const stat = document.createElement('div');
        stat.className = 'skeleton-stat';
        stat.innerHTML = `
            <div class="skeleton skeleton-stat-number"></div>
            <div class="skeleton skeleton-stat-label"></div>
        `;
        container.appendChild(stat);
    }
}

// Auto-hide skeleton after page load
document.addEventListener('DOMContentLoaded', function() {
    // Hide all skeletons after page loads (content is ready)
    setTimeout(() => {
        const skeletons = document.querySelectorAll('.skeleton-container');
        skeletons.forEach(skeleton => {
            skeleton.classList.remove('active');
        });
        
        const contents = document.querySelectorAll('.content-loading');
        contents.forEach(content => {
            content.classList.remove('content-loading');
            content.classList.add('content-loaded');
        });
    }, 300);
});
