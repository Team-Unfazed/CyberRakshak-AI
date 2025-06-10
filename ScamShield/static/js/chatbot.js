// Chatbot functionality for CyberRakshak AI
class CyberRakshakChatbot {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.messagesContainer = document.getElementById('chat-messages');
        this.chatForm = document.getElementById('chat-form');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.speechSynthesis = window.speechSynthesis;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupQuickQuestions();
        this.scrollToBottom();
    }

    setupEventListeners() {
        // Form submission
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Enter key handling
        if (this.chatInput) {
            this.chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSubmit(e);
                }
            });

            // Auto-resize textarea
            this.chatInput.addEventListener('input', this.autoResize);
        }

        // Language change listener
        document.addEventListener('languageChanged', (e) => {
            this.currentLanguage = e.detail.language;
        });
    }

    setupQuickQuestions() {
        const quickButtons = document.querySelectorAll('.quick-question');
        quickButtons.forEach(button => {
            button.addEventListener('click', () => {
                const question = button.getAttribute('data-question');
                this.sendMessage(question);
            });
        });
    }

    autoResize(e) {
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to backend
        try {
            const response = await fetch('/chatbot_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: message,
                    language: this.currentLanguage
                })
            });

            const result = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            if (result.success) {
                // Add bot response
                this.addMessage(result.response, 'bot');
                
                // Speak response if it's a warning
                if (result.response.toLowerCase().includes('warning') || 
                    result.response.toLowerCase().includes('scam')) {
                    setTimeout(() => this.speakText(result.response), 500);
                }
            } else {
                this.addMessage(result.error || 'Sorry, I encountered an error.', 'bot');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I\'m having trouble connecting. Please try again.', 'bot');
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });

        const senderName = sender === 'user' ? 
            this.getTranslation('you') : 
            this.getTranslation('bot');

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i data-feather="${sender === 'user' ? 'user' : 'shield'}" 
                   class="${sender === 'user' ? 'text-secondary' : 'text-primary'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <p class="mb-0">${this.formatMessage(text)}</p>
                </div>
                <small class="text-muted message-time">${currentTime}</small>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        feather.replace();
        this.scrollToBottom();
    }

    formatMessage(text) {
        // Format the message text with basic markdown-like formatting
        let formatted = this.escapeHtml(text);
        
        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Highlight warnings
        if (formatted.toLowerCase().includes('warning') || 
            formatted.toLowerCase().includes('scam')) {
            formatted = `<span class="text-danger fw-semibold">${formatted}</span>`;
        }
        
        return formatted;
    }

    showTypingIndicator() {
        const typingTemplate = document.getElementById('typing-template');
        if (typingTemplate) {
            const typingClone = typingTemplate.cloneNode(true);
            typingClone.id = 'typing-indicator';
            typingClone.style.display = 'flex';
            
            this.messagesContainer.appendChild(typingClone);
            feather.replace();
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    sendMessage(message) {
        this.chatInput.value = message;
        this.handleSubmit(new Event('submit'));
    }

    speakText(text) {
        if (!this.speechSynthesis) return;

        // Cancel any ongoing speech
        this.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 0.7;

        // Set language
        if (this.currentLanguage === 'hi') {
            utterance.lang = 'hi-IN';
        } else {
            utterance.lang = 'en-US';
        }

        this.speechSynthesis.speak(utterance);
    }

    setLanguage(language) {
        this.currentLanguage = language;
        
        // Update welcome message if it's the only message
        const messages = this.messagesContainer.querySelectorAll('.message');
        if (messages.length === 1) {
            const welcomeText = this.getTranslation('welcome_message');
            const welcomeBubble = messages[0].querySelector('.message-bubble p');
            if (welcomeBubble) {
                welcomeBubble.textContent = welcomeText;
            }
        }
    }

    getTranslation(key) {
        const translations = window.chatbotTranslations || {};
        const lang = translations[this.currentLanguage] || translations.en || {};
        return lang[key] || key;
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Public methods for external access
    clearChat() {
        const messages = this.messagesContainer.querySelectorAll('.message:not(:first-child)');
        messages.forEach(message => message.remove());
    }

    addQuickResponse(responses) {
        const quickResponsesDiv = document.createElement('div');
        quickResponsesDiv.className = 'quick-responses mt-2 d-flex flex-wrap gap-2';
        
        responses.forEach(response => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-primary btn-sm';
            button.textContent = response;
            button.onclick = () => {
                this.sendMessage(response);
                quickResponsesDiv.remove();
            };
            quickResponsesDiv.appendChild(button);
        });
        
        const lastMessage = this.messagesContainer.lastElementChild;
        if (lastMessage && lastMessage.classList.contains('bot-message')) {
            lastMessage.appendChild(quickResponsesDiv);
        }
    }
}

// Initialize chatbot when DOM is loaded
let chatbot;
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on chatbot page
    if (document.getElementById('chat-messages')) {
        chatbot = new CyberRakshakChatbot();
        
        // Make chatbot globally accessible
        window.chatbot = chatbot;
        
        // Add some example quick responses after welcome message
        setTimeout(() => {
            if (chatbot.messagesContainer.children.length === 1) {
                chatbot.addQuickResponse([
                    'How do I spot a UPI scam?',
                    'What are phishing attacks?',
                    'Help me check this message'
                ]);
            }
        }, 2000);
    }
});

// Export for external access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CyberRakshakChatbot;
}
