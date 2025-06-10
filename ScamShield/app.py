import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import pytesseract
from PIL import Image
from scam_detector import ScamDetector
from link_analyzer import LinkAnalyzer
from language_support import LanguageSupport

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cyberrakshak-ai-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
scam_detector = ScamDetector()
link_analyzer = LinkAnalyzer()
language_support = LanguageSupport()

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        # Open and process image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(image, lang='eng+hin')
        
        return extracted_text.strip()
    except Exception as e:
        logging.error(f"OCR extraction failed: {str(e)}")
        return ""

@app.route('/')
def index():
    """Main page with upload and text input forms"""
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    """Chatbot interface page"""
    return render_template('chatbot.html')

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    """Analyze text input for scams"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({
                'success': False,
                'error': language_support.get_text('empty_text_error', language)
            })
        
        # Detect scam
        scam_result = scam_detector.analyze_text(text)
        
        # Analyze links if present
        link_results = link_analyzer.analyze_links_in_text(text)
        
        # Prepare response
        response = {
            'success': True,
            'is_scam': scam_result['is_scam'],
            'scam_type': scam_result['scam_type'],
            'confidence': scam_result['confidence'],
            'explanation': language_support.get_scam_explanation(
                scam_result['scam_type'], language
            ),
            'keywords_found': scam_result['keywords_found'],
            'link_analysis': link_results,
            'warning_message': language_support.get_warning_message(
                scam_result['scam_type'], language
            ) if scam_result['is_scam'] else None
        }
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Text analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': language_support.get_text('analysis_error', language)
        })

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image for scams"""
    try:
        language = request.form.get('language', 'en')
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': language_support.get_text('no_file_error', language)
            })
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': language_support.get_text('no_file_selected_error', language)
            })
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': language_support.get_text('invalid_file_type_error', language)
            })
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from image
            extracted_text = extract_text_from_image(filepath)
            
            if not extracted_text:
                return jsonify({
                    'success': False,
                    'error': language_support.get_text('no_text_found_error', language)
                })
            
            # Analyze extracted text
            scam_result = scam_detector.analyze_text(extracted_text)
            link_results = link_analyzer.analyze_links_in_text(extracted_text)
            
            response = {
                'success': True,
                'extracted_text': extracted_text,
                'is_scam': scam_result['is_scam'],
                'scam_type': scam_result['scam_type'],
                'confidence': scam_result['confidence'],
                'explanation': language_support.get_scam_explanation(
                    scam_result['scam_type'], language
                ),
                'keywords_found': scam_result['keywords_found'],
                'link_analysis': link_results,
                'warning_message': language_support.get_warning_message(
                    scam_result['scam_type'], language
                ) if scam_result['is_scam'] else None
            }
            
            return jsonify(response)
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logging.error(f"Image analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': language_support.get_text('analysis_error', language)
        })

@app.route('/chatbot_query', methods=['POST'])
def chatbot_query():
    """Handle chatbot queries"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        language = data.get('language', 'en')
        
        if not query:
            return jsonify({
                'success': False,
                'error': language_support.get_text('empty_query_error', language)
            })
        
        # Simple chatbot logic
        response_text = process_chatbot_query(query, language)
        
        return jsonify({
            'success': True,
            'response': response_text
        })
        
    except Exception as e:
        logging.error(f"Chatbot query error: {str(e)}")
        return jsonify({
            'success': False,
            'error': language_support.get_text('chatbot_error', language)
        })

def process_chatbot_query(query, language):
    """Process chatbot queries and provide responses"""
    query_lower = query.lower()
    
    # Check if query contains text to analyze
    if any(keyword in query_lower for keyword in ['check', 'analyze', 'scam', 'fraud']):
        # Try to extract potential scam text from query
        scam_result = scam_detector.analyze_text(query)
        
        if scam_result['is_scam']:
            return (
                language_support.get_text('chatbot_scam_detected', language) +
                " " + language_support.get_scam_explanation(scam_result['scam_type'], language)
            )
        else:
            return language_support.get_text('chatbot_no_scam', language)
    
    # General responses
    if any(keyword in query_lower for keyword in ['hello', 'hi', 'help', 'namaste']):
        return language_support.get_text('chatbot_greeting', language)
    
    if any(keyword in query_lower for keyword in ['upi', 'payment', 'money']):
        return language_support.get_text('chatbot_upi_info', language)
    
    if any(keyword in query_lower for keyword in ['phishing', 'link', 'click']):
        return language_support.get_text('chatbot_phishing_info', language)
    
    if any(keyword in query_lower for keyword in ['job', 'work', 'employment']):
        return language_support.get_text('chatbot_job_info', language)
    
    # Default response
    return language_support.get_text('chatbot_default', language)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
