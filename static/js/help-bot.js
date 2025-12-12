/**
 * Niya - TuitionTrack Help Bot
 * RAG-powered AI assistant using FAISS and Gemini
 */

const NiyaHelpBot = {
    // User role (tutor or student)
    userRole: 'tutor',
    
    // Current action/context
    currentAction: 'main',
    
    // Initialize the bot
    init: function() {
        console.log('Niya: Initializing AI help bot...');
        
        // Determine user role
        const isStudent = window.location.pathname.includes('/student/') ||
                         (typeof window.userRole !== 'undefined' && window.userRole === 'student') ||
                         document.querySelector('.student-header');
        
        this.userRole = isStudent ? 'student' : 'tutor';
        console.log('Niya: User role:', this.userRole);
        
        // Create floating button
        this.createFloatingButton();
        
        // Create bot panel
        this.createPanel();
        
        // Attach event listeners
        this.attachEventListeners();
    },
    
    // Create floating button
    createFloatingButton: function() {
        // Remove existing button if any
        const existingBtn = document.getElementById('niya-help-button');
        if (existingBtn) {
            existingBtn.remove();
        }
        
        const button = document.createElement('div');
        button.id = 'niya-help-button';
        button.innerHTML = `
            <img src="/static/niya_avatar_60x60.png" alt="Niya" class="niya-avatar">
        `;
        button.setAttribute('role', 'button');
        button.setAttribute('aria-label', 'Open Niya help bot');
        button.style.cssText = `
            position: fixed !important;
            bottom: 100px !important;
            right: 20px !important;
            width: 60px !important;
            height: 60px !important;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4) !important;
            z-index: 99999 !important;
            transition: all 0.3s ease !important;
            visibility: visible !important;
            opacity: 1 !important;
        `;
        
        document.body.appendChild(button);
        console.log('Niya: Floating button created');
    },
    
    // Create bot panel
    createPanel: function() {
        // Remove existing panel if any
        const existingPanel = document.getElementById('niya-help-panel');
        if (existingPanel) {
            existingPanel.remove();
        }
        
        const panel = document.createElement('div');
        panel.id = 'niya-help-panel';
        panel.innerHTML = `
            <div class="niya-header">
                <div class="niya-header-content">
                    <div class="niya-avatar-container">
                        <img src="/static/niya_avatar_80x80.png" alt="Niya" class="niya-avatar-large">
                        <span class="niya-status-dot"></span>
                    </div>
                    <div>
                        <div class="niya-name">Niya</div>
                        <div class="niya-status">AI Assistant</div>
                    </div>
                </div>
                <button class="niya-close" aria-label="Close help bot">✕</button>
            </div>
            <div class="niya-messages" id="niya-messages"></div>
            <div class="niya-input-container">
                <input type="text" id="niya-query-input" class="niya-query-input" placeholder="Ask me anything about TuitionTrack..." autocomplete="off">
                <button id="niya-send-btn" class="niya-send-btn" aria-label="Send message">➤</button>
            </div>
        `;
        document.body.appendChild(panel);
        
        // Force input container visibility and proper sizing (browser compatibility)
        setTimeout(() => {
            const inputContainer = panel.querySelector('.niya-input-container');
            if (inputContainer) {
                inputContainer.style.cssText = `
                    display: flex !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    width: 100% !important;
                    max-width: 100% !important;
                    box-sizing: border-box !important;
                    padding: 0.75rem 1rem !important;
                `;
            }
            
            const queryInput = panel.querySelector('.niya-query-input');
            if (queryInput) {
                queryInput.style.cssText = `
                    flex: 1 1 auto !important;
                    min-width: 0 !important;
                    max-width: 100% !important;
                    box-sizing: border-box !important;
                `;
            }
        }, 100);
        
        // Show welcome message
        setTimeout(() => {
            this.showWelcomeMessage();
        }, 400);
    },
    
    // Show welcome message
    showWelcomeMessage: function() {
        const messagesDiv = document.getElementById('niya-messages');
        if (!messagesDiv) return;
        
        const welcomeEl = document.createElement('div');
        welcomeEl.className = 'niya-message niya-message-left';
        welcomeEl.innerHTML = `
            <div class="niya-message-avatar">
                <img src="/static/niya_avatar_50x50.png" alt="Niya">
            </div>
            <div class="niya-message-content">
                Hi! I'm Niya 👋<br><br>
                I'm your AI assistant for TuitionTrack! Ask me anything about attendance, students, homework, batches, or reports. 😊
            </div>
        `;
        messagesDiv.appendChild(welcomeEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    },
    
    // Attach event listeners
    attachEventListeners: function() {
        const button = document.getElementById('niya-help-button');
        const panel = document.getElementById('niya-help-panel');
        const closeBtn = panel.querySelector('.niya-close');
        const queryInput = document.getElementById('niya-query-input');
        const sendBtn = document.getElementById('niya-send-btn');

        button.addEventListener('click', () => this.togglePanel());
        closeBtn.addEventListener('click', () => this.closePanel());
        
        // Close on outside click
        panel.addEventListener('click', (e) => {
            if (e.target === panel) {
                this.closePanel();
            }
        });
        
        // Text input handling
        if (queryInput && sendBtn) {
            // Send on button click
            sendBtn.addEventListener('click', () => this.handleQuery());
            
            // Send on Enter key
            queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleQuery();
                }
            });
            
            // Focus input when panel opens
            const panelObserver = new MutationObserver(() => {
                if (panel.classList.contains('niya-open')) {
                    setTimeout(() => queryInput.focus(), 500);
                }
            });
            panelObserver.observe(panel, { attributes: true, attributeFilter: ['class'] });
        }
    },
    
    // Toggle panel
    togglePanel: function() {
        const panel = document.getElementById('niya-help-panel');
        const button = document.getElementById('niya-help-button');
        const isOpen = panel && panel.classList.contains('niya-open');
        
        if (!isOpen) {
            if (panel) {
                panel.classList.add('niya-open');
                panel.classList.add('niya-fullscreen');
                
                // Force panel width to 100% (not 100vw to avoid scrollbar issues)
                panel.style.width = '100%';
                panel.style.maxWidth = '100%';
                panel.style.boxSizing = 'border-box';
            }
            
            // Hide floating button when panel is open
            document.body.classList.add('niya-chat-open');
            if (button) {
                button.style.display = 'none';
                button.style.visibility = 'hidden';
                button.style.opacity = '0';
            }
            
            // Force input container styles after panel opens
            setTimeout(() => {
                const inputContainer = panel.querySelector('.niya-input-container');
                if (inputContainer) {
                    inputContainer.style.cssText = `
                        display: flex !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        width: 100% !important;
                        max-width: 100% !important;
                        box-sizing: border-box !important;
                        padding: 0.75rem 1rem !important;
                    `;
                }
                
                const queryInput = document.getElementById('niya-query-input');
                if (queryInput) {
                    queryInput.style.cssText = `
                        flex: 1 1 auto !important;
                        min-width: 0 !important;
                        max-width: 100% !important;
                        box-sizing: border-box !important;
                    `;
                    queryInput.focus();
                }
            }, 450);
        } else {
            this.closePanel();
        }
    },
    
    // Close panel
    closePanel: function() {
        const panel = document.getElementById('niya-help-panel');
        const button = document.getElementById('niya-help-button');
        
        if (panel) {
            panel.classList.remove('niya-open');
            panel.classList.remove('niya-fullscreen');
        }
        
        // Show floating button when panel is closed
        document.body.classList.remove('niya-chat-open');
        if (button) {
            button.style.display = 'flex';
            button.style.visibility = 'visible';
            button.style.opacity = '1';
        }
    },
    
    // Handle user query
    handleQuery: async function() {
        const queryInput = document.getElementById('niya-query-input');
        const sendBtn = document.getElementById('niya-send-btn');
        const messagesDiv = document.getElementById('niya-messages');
        
        const query = queryInput.value.trim();
        if (!query) return;
        
        // Clear input
        queryInput.value = '';
        queryInput.disabled = true;
        sendBtn.disabled = true;
        
        // Show user message
        const userMessageEl = document.createElement('div');
        userMessageEl.className = 'niya-message niya-message-right';
        userMessageEl.innerHTML = `
            <div class="niya-message-content">
                ${this.escapeHtml(query)}
            </div>
            <div class="niya-message-avatar">
                <div class="niya-user-avatar">👤</div>
            </div>
        `;
        messagesDiv.appendChild(userMessageEl);
        
            // Show typing indicator
        const typingEl = document.createElement('div');
        typingEl.className = 'niya-message niya-message-left niya-typing';
        typingEl.id = 'niya-typing-indicator';
        typingEl.innerHTML = `
            <div class="niya-message-avatar">
                <img src="/static/niya_avatar_50x50.png" alt="Niya">
            </div>
            <div class="niya-message-content">
                <div class="niya-typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesDiv.appendChild(typingEl);
        
        // Scroll to show typing indicator
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        try {
            // Call AI API
            const response = await fetch('/api/help-bot/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    context: this.currentAction || 'main'
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            const typingIndicator = document.getElementById('niya-typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Get response text
            const responseText = data.success ? data.response : (data.error || "I'm here to help! Could you please rephrase your question? 😊");
            
            // Show response
            const responseEl = document.createElement('div');
            responseEl.className = 'niya-message niya-message-left';
            responseEl.innerHTML = `
                <div class="niya-message-avatar">
                    <img src="/static/niya_avatar_50x50.png" alt="Niya">
                </div>
                <div class="niya-message-content">
                    ${responseText.replace(/\n/g, '<br>')}
                </div>
            `;
            messagesDiv.appendChild(responseEl);
            
        } catch (error) {
            console.error('Error querying AI API:', error);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById('niya-typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Show error message
            const errorEl = document.createElement('div');
            errorEl.className = 'niya-message niya-message-left';
            errorEl.innerHTML = `
                <div class="niya-message-avatar">
                    <img src="/static/niya_avatar_50x50.png" alt="Niya">
                </div>
                <div class="niya-message-content">
                    Oops! Something went wrong. Please try again or check your internet connection. 😊
                </div>
            `;
            messagesDiv.appendChild(errorEl);
        } finally {
            // Re-enable input
            queryInput.disabled = false;
            sendBtn.disabled = false;
            queryInput.focus();
            
            // Scroll to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    },
    
    // Escape HTML to prevent XSS
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize when DOM is ready - only if user is logged in
document.addEventListener('DOMContentLoaded', () => {
    console.log('Niya: DOMContentLoaded fired');
    
    // Check if user is logged in
    if (typeof window.userLoggedIn === 'undefined' || !window.userLoggedIn) {
        console.log('Niya: User not logged in, skipping initialization');
        return;
    }
    
    // Small delay to ensure body is ready
    setTimeout(() => {
        try {
            NiyaHelpBot.init();
        } catch (error) {
            console.error('Niya: Error during initialization:', error);
        }
    }, 100);
});
