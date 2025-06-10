// Main JavaScript for CyberRakshak AI
class CyberRakshakApp {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.speechSynthesis = window.speechSynthesis;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.loadTranslations();
    }

    setupEventListeners() {
        // Text form submission
        const textForm = document.getElementById('text-form');
        if (textForm) {
            textForm.addEventListener('submit', (e) => this.handleTextSubmission(e));
        }

        // Image form submission
        const imageForm = document.getElementById('image-form');
        if (imageForm) {
            imageForm.addEventListener('submit', (e) => this.handleImageSubmission(e));
        }

        // File input change
        const imageInput = document.getElementById('image-input');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleFileSelection(e));
        }

        // Language change listener
        document.addEventListener('languageChanged', (e) => {
            this.currentLanguage = e.detail.language;
        });

        // Tab switching
        const tabTriggers = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabTriggers.forEach(trigger => {
            trigger.addEventListener('shown.bs.tab', () => {
                feather.replace();
            });
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('upload-area');
        if (!uploadArea) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            }, false);
        });

        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);
        uploadArea.addEventListener('click', () => {
            document.getElementById('image-input').click();
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            document.getElementById('image-input').files = files;
            this.handleFileSelection({ target: { files: files } });
        }
    }

    handleFileSelection(e) {
        const file = e.target.files[0];
        if (file) {
            const fileName = file.name;
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            
            // Update upload area display
            const uploadArea = document.getElementById('upload-area');
            uploadArea.innerHTML = `
                <i data-feather="file-text" size="48" class="text-success mb-3"></i>
                <p class="mb-2 fw-semibold">${fileName}</p>
                <p class="text-muted small mb-3">Size: ${fileSize} MB</p>
                <button type="button" class="btn btn-outline-secondary" onclick="this.closest('form').reset(); location.reload();">
                    <i data-feather="x" class="me-2"></i>
                    Change File
                </button>
            `;
            feather.replace();
        }
    }

    async handleTextSubmission(e) {
        e.preventDefault();
        
        const textInput = document.getElementById('text-input');
        const text = textInput.value.trim();
        
        if (!text) {
            this.showError(this.getTranslation('empty_text_error'));
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/analyze_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    language: this.currentLanguage
                })
            });

            const result = await response.json();
            this.hideLoading();

            if (result.success) {
                this.displayResults(result, text);
                this.playVoiceAlert(result.is_scam);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Network error. Please try again.');
            console.error('Text analysis error:', error);
        }
    }

    async handleImageSubmission(e) {
        e.preventDefault();
        
        const imageInput = document.getElementById('image-input');
        const file = imageInput.files[0];
        
        if (!file) {
            this.showError(this.getTranslation('no_file_selected_error'));
            return;
        }

        this.showLoading();
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('language', this.currentLanguage);

            const response = await fetch('/analyze_image', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            this.hideLoading();

            if (result.success) {
                this.displayResults(result, result.extracted_text);
                this.playVoiceAlert(result.is_scam);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Network error. Please try again.');
            console.error('Image analysis error:', error);
        }
    }

    displayResults(result, originalText) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');
        
        // Determine alert type and styling
        const isScam = result.is_scam;
        const alertClass = isScam ? 'scam-alert' : 'safe-alert';
        const statusIcon = isScam ? '🚨' : '✅';
        const statusText = isScam ? 
            this.getTranslation('scam_detected') : 
            this.getTranslation('no_scam_detected');
        
        // Confidence styling
        let confidenceClass = 'confidence-low';
        if (result.confidence > 0.7) confidenceClass = 'confidence-high';
        else if (result.confidence > 0.4) confidenceClass = 'confidence-medium';

        let html = `
            <div class="alert ${alertClass} border-0 mb-4">
                <div class="d-flex align-items-center mb-3">
                    <span class="display-6 me-3">${statusIcon}</span>
                    <div>
                        <h4 class="alert-heading mb-1">${statusText}</h4>
                        <p class="mb-0">${result.explanation || ''}</p>
                    </div>
                </div>
                
                ${result.warning_message ? `
                    <div class="alert alert-warning border-0 mt-3">
                        <strong>${result.warning_message}</strong>
                    </div>
                ` : ''}
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="card border-0 bg-light mb-3">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i data-feather="bar-chart" class="me-2"></i>
                                ${this.getTranslation('confidence_level')}
                            </h6>
                            <div class="confidence-bar mb-2">
                                <div class="confidence-fill ${confidenceClass}" 
                                     style="width: ${result.confidence * 100}%"></div>
                            </div>
                            <small class="text-muted">${Math.round(result.confidence * 100)}% confidence</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card border-0 bg-light mb-3">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i data-feather="tag" class="me-2"></i>
                                ${this.getTranslation('scam_type')}
                            </h6>
                            <span class="badge bg-secondary fs-6">${result.scam_type || 'none'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Show extracted text for images
        if (result.extracted_text && result.extracted_text !== originalText) {
            html += `
                <div class="card border-0 bg-light mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i data-feather="file-text" class="me-2"></i>
                            ${this.getTranslation('extracted_text')}
                        </h6>
                        <div class="bg-white p-3 rounded border">
                            <code class="text-dark">${this.escapeHtml(result.extracted_text)}</code>
                        </div>
                    </div>
                </div>
            `;
        }

        // Show keywords found
        if (result.keywords_found && result.keywords_found.length > 0) {
            html += `
                <div class="card border-0 bg-light mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i data-feather="search" class="me-2"></i>
                            ${this.getTranslation('keywords_found')}
                        </h6>
                        <div class="keywords-container">
                            ${result.keywords_found.map(keyword => 
                                `<span class="keyword-tag">${this.escapeHtml(keyword)}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        // Show link analysis
        if (result.link_analysis && result.link_analysis.length > 0) {
            html += `
                <div class="card border-0 bg-light mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i data-feather="link" class="me-2"></i>
                            ${this.getTranslation('link_analysis')}
                        </h6>
                        <div class="links-container">
                            ${result.link_analysis.map(link => this.renderLinkAnalysis(link)).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        // Add voice controls
        html += this.renderVoiceControls(result.is_scam);

        resultsContent.innerHTML = html;
        resultsSection.style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Replace feather icons
        feather.replace();
    }

    renderLinkAnalysis(link) {
        const riskClass = link.risk_level === 'high' ? 'high-risk' : 
                         link.risk_level === 'medium' ? 'medium-risk' :
                         link.risk_level === 'low' ? 'low-risk' : 'safe';
        
        const riskIcon = link.risk_level === 'high' ? 'alert-triangle' : 
                        link.risk_level === 'medium' ? 'alert-circle' :
                        link.risk_level === 'low' ? 'info' : 'check-circle';
        
        const riskColor = link.risk_level === 'high' ? 'text-danger' : 
                         link.risk_level === 'medium' ? 'text-warning' :
                         link.risk_level === 'low' ? 'text-info' : 'text-success';

        return `
            <div class="link-item ${riskClass}">
                <div class="d-flex align-items-start">
                    <i data-feather="${riskIcon}" class="${riskColor} me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${this.escapeHtml(link.domain)}</h6>
                        <p class="mb-2 small text-muted">${this.escapeHtml(link.url)}</p>
                        <div class="d-flex align-items-center">
                            <span class="badge bg-secondary me-2">${link.risk_level} risk</span>
                            <small class="text-muted">Score: ${link.risk_score}</small>
                        </div>
                        ${link.risk_factors && link.risk_factors.length > 0 ? `
                            <div class="mt-2">
                                <small class="text-muted">Risk factors:</small>
                                <ul class="small mb-0 mt-1">
                                    ${link.risk_factors.map(factor => 
                                        `<li>${this.escapeHtml(factor)}</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderVoiceControls(isScam) {
        const message = isScam ? 
            this.getTranslation('warning_voice') : 
            this.getTranslation('safe_voice');

        return `
            <div class="voice-controls">
                <i data-feather="volume-2" class="me-2"></i>
                <span class="me-2">Voice Alert:</span>
                <button type="button" onclick="cyberRakshak.speakText('${message.replace(/'/g, '\\'')}')" 
                        class="btn btn-sm" title="Play voice alert">
                    <i data-feather="play"></i>
                </button>
                <button type="button" onclick="cyberRakshak.stopSpeech()" 
                        class="btn btn-sm" title="Stop voice">
                    <i data-feather="stop-circle"></i>
                </button>
            </div>
        `;
    }

    playVoiceAlert(isScam) {
        if (!this.speechSynthesis) return;

        const message = isScam ? 
            this.getTranslation('warning_voice') : 
            this.getTranslation('safe_voice');

        // Play warning sound for scams
        if (isScam) {
            const audio = document.getElementById('warning-sound');
            if (audio) {
                audio.play().catch(e => console.log('Could not play warning sound:', e));
            }
        }

        // Speak the message
        setTimeout(() => {
            this.speakText(message);
        }, isScam ? 1000 : 0);
    }

    speakText(text) {
        if (!this.speechSynthesis) return;

        // Cancel any ongoing speech
        this.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 0.8;

        // Set language
        if (this.currentLanguage === 'hi') {
            utterance.lang = 'hi-IN';
        } else {
            utterance.lang = 'en-US';
        }

        this.speechSynthesis.speak(utterance);
    }

    stopSpeech() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
        }
    }

    showLoading() {
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();
    }

    hideLoading() {
        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (loadingModal) {
            loadingModal.hide();
        }
    }

    showError(message) {
        // Create or update error alert
        let errorAlert = document.getElementById('error-alert');
        
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.id = 'error-alert';
            errorAlert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
            errorAlert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
            document.body.appendChild(errorAlert);
        }

        errorAlert.innerHTML = `
            <i data-feather="alert-circle" class="me-2"></i>
            <strong>Error:</strong> ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        feather.replace();

        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = bootstrap.Alert.getInstance(errorAlert);
            if (alert) alert.close();
        }, 5000);
    }

    getTranslation(key) {
        const translations = window.translations || {};
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

    loadTranslations() {
        // Translations are loaded from the template
        // This method can be extended to load additional translations
    }
}

// Initialize the app
let cyberRakshak;
document.addEventListener('DOMContentLoaded', function() {
    cyberRakshak = new CyberRakshakApp();
});
