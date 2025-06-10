import logging
from typing import Dict, Any, List

class LanguageSupport:
    """Multilingual support for the application"""
    
    def __init__(self):
        """Initialize with supported languages and translations"""
        self.translations = {
            'en': {
                # General messages
                'app_title': 'CyberRakshak AI - Scam Detection',
                'upload_image': 'Upload Screenshot',
                'paste_text': 'Paste Text Message',
                'analyze_button': 'Analyze for Scams',
                'chatbot_title': 'Ask CyberRakshak',
                'language_switch': 'Switch Language',
                
                # Analysis results
                'scam_detected': 'SCAM DETECTED!',
                'no_scam_detected': 'No Scam Detected',
                'analysis_complete': 'Analysis Complete',
                'confidence_level': 'Confidence Level',
                'scam_type': 'Scam Type',
                'keywords_found': 'Suspicious Keywords Found',
                'links_analysis': 'Link Analysis',
                
                # Error messages
                'empty_text_error': 'Please enter some text to analyze',
                'no_file_error': 'No file uploaded',
                'no_file_selected_error': 'Please select a file to upload',
                'invalid_file_type_error': 'Invalid file type. Please upload an image file.',
                'no_text_found_error': 'No text found in the uploaded image',
                'analysis_error': 'An error occurred during analysis. Please try again.',
                'empty_query_error': 'Please enter a question',
                'chatbot_error': 'Sorry, I encountered an error. Please try again.',
                
                # Chatbot responses
                'chatbot_greeting': 'Hello! I\'m CyberRakshak AI. I can help you identify scams. Share any suspicious message or ask me about potential fraud.',
                'chatbot_scam_detected': 'WARNING: This appears to be a scam!',
                'chatbot_no_scam': 'This message appears to be legitimate, but always stay cautious.',
                'chatbot_upi_info': 'UPI scams often ask for OTP, PIN, or personal details. Never share these with anyone. Banks never ask for such information via SMS or calls.',
                'chatbot_phishing_info': 'Phishing scams use fake links to steal your information. Always verify the sender and check URLs carefully before clicking.',
                'chatbot_job_info': 'Job scams often ask for upfront payments or fees. Legitimate employers never ask for money from job applicants.',
                'chatbot_default': 'I can help you identify scams. Please share a suspicious message or ask me about specific types of fraud.',
                
                # Scam explanations
                'upi_fraud_explanation': 'UPI fraud typically involves requests for OTP, UPI PIN, or immediate money transfers. Scammers often impersonate banks or payment services.',
                'phishing_explanation': 'Phishing attempts to steal your personal information through fake websites or messages that appear legitimate.',
                'job_scam_explanation': 'Job scams promise easy money or work-from-home opportunities but require upfront payments or fees.',
                'lottery_scam_explanation': 'Lottery scams claim you\'ve won a prize you never entered for, then ask for fees to claim the prize.',
                
                # Warning messages
                'upi_fraud_warning': '⚠️ Never share your OTP, UPI PIN, or bank details with anyone!',
                'phishing_warning': '⚠️ Do not click suspicious links or provide personal information!',
                'job_scam_warning': '⚠️ Never pay money upfront for job opportunities!',
                'lottery_scam_warning': '⚠️ You cannot win a lottery you never entered!'
            },
            'hi': {
                # General messages
                'app_title': 'साइबर रक्षक एआई - स्कैम डिटेक्शन',
                'upload_image': 'स्क्रीनशॉट अपलोड करें',
                'paste_text': 'टेक्स्ट मैसेज पेस्ट करें',
                'analyze_button': 'स्कैम के लिए विश्लेषण करें',
                'chatbot_title': 'साइबर रक्षक से पूछें',
                'language_switch': 'भाषा बदलें',
                
                # Analysis results
                'scam_detected': 'स्कैम का पता चला!',
                'no_scam_detected': 'कोई स्कैम नहीं मिला',
                'analysis_complete': 'विश्लेषण पूरा',
                'confidence_level': 'विश्वास स्तर',
                'scam_type': 'स्कैम का प्रकार',
                'keywords_found': 'संदिग्ध शब्द मिले',
                'links_analysis': 'लिंक विश्लेषण',
                
                # Error messages
                'empty_text_error': 'कृपया विश्लेषण के लिए कुछ टेक्स्ट दर्ज करें',
                'no_file_error': 'कोई फाइल अपलोड नहीं की गई',
                'no_file_selected_error': 'कृपया अपलोड करने के लिए एक फाइल चुनें',
                'invalid_file_type_error': 'गलत फाइल प्रकार। कृपया एक इमेज फाइल अपलोड करें।',
                'no_text_found_error': 'अपलोड की गई इमेज में कोई टेक्स्ट नहीं मिला',
                'analysis_error': 'विश्लेषण के दौरान एक त्रुटि हुई। कृपया फिर से कोशिश करें।',
                'empty_query_error': 'कृपया एक प्रश्न दर्ज करें',
                'chatbot_error': 'माफ करें, मुझे एक त्रुटि का सामना करना पड़ा। कृपया फिर से कोशिश करें।',
                
                # Chatbot responses
                'chatbot_greeting': 'नमस्ते! मैं साइबर रक्षक एआई हूं। मैं आपको स्कैम की पहचान करने में मदद कर सकता हूं। कोई भी संदिग्ध संदेश साझा करें या मुझसे संभावित धोखाधड़ी के बारे में पूछें।',
                'chatbot_scam_detected': 'चेतावनी: यह एक स्कैम लगता है!',
                'chatbot_no_scam': 'यह संदेश वैध लगता है, लेकिन हमेशा सावधान रहें।',
                'chatbot_upi_info': 'UPI स्कैम अक्सर OTP, PIN, या व्यक्तिगत विवरण मांगते हैं। इन्हें कभी किसी के साथ साझा न करें। बैंक कभी भी SMS या कॉल के माध्यम से ऐसी जानकारी नहीं मांगते।',
                'chatbot_phishing_info': 'फिशिंग स्कैम आपकी जानकारी चुराने के लिए नकली लिंक का उपयोग करते हैं। क्लिक करने से पहले हमेशा भेजने वाले की पुष्टि करें और URL की जांच करें।',
                'chatbot_job_info': 'जॉब स्कैम अक्सर अग्रिम भुगतान या फीस मांगते हैं। वैध नियोक्ता कभी भी नौकरी आवेदकों से पैसे नहीं मांगते।',
                'chatbot_default': 'मैं आपको स्कैम की पहचान करने में मदद कर सकता हूं। कृपया एक संदिग्ध संदेश साझा करें या मुझसे विशिष्ट प्रकार की धोखाधड़ी के बारे में पूछें।',
                
                # Scam explanations
                'upi_fraud_explanation': 'UPI धोखाधड़ी में आमतौर पर OTP, UPI PIN, या तत्काल पैसे ट्रांसफर की मांग शामिल होती है। स्कैमर अक्सर बैंकों या भुगतान सेवाओं का नकल करते हैं।',
                'phishing_explanation': 'फिशिंग आपकी व्यक्तिगत जानकारी चुराने की कोशिश करता है नकली वेबसाइटों या संदेशों के माध्यम से जो वैध लगते हैं।',
                'job_scam_explanation': 'जॉब स्कैम आसान पैसे या घर से काम के अवसरों का वादा करते हैं लेकिन अग्रिम भुगतान या फीस की मांग करते हैं।',
                'lottery_scam_explanation': 'लॉटरी स्कैम दावा करते हैं कि आपने एक ऐसा पुरस्कार जीता है जिसके लिए आपने कभी आवेदन नहीं दिया, फिर पुरस्कार दावा करने के लिए फीस मांगते हैं।',
                
                # Warning messages
                'upi_fraud_warning': '⚠️ अपना OTP, UPI PIN, या बैंक विवरण कभी किसी के साथ साझा न करें!',
                'phishing_warning': '⚠️ संदिग्ध लिंक पर क्लिक न करें या व्यक्तिगत जानकारी न दें!',
                'job_scam_warning': '⚠️ नौकरी के अवसरों के लिए कभी पहले से पैसे न दें!',
                'lottery_scam_warning': '⚠️ आप ऐसी लॉटरी नहीं जीत सकते जिसमें आपने कभी हिस्सा नहीं लिया!'
            }
        }
        
        self.supported_languages = list(self.translations.keys())
        logging.info(f"LanguageSupport initialized with languages: {self.supported_languages}")
    
    def get_text(self, key: str, language: str = 'en') -> str:
        """
        Get translated text for a given key and language
        
        Args:
            key: Translation key
            language: Language code (en, hi)
            
        Returns:
            Translated text or key if not found
        """
        if language not in self.translations:
            language = 'en'  # Fallback to English
        
        return self.translations[language].get(key, key)
    
    def get_scam_explanation(self, scam_type: str, language: str = 'en') -> str:
        """
        Get explanation for a specific scam type
        
        Args:
            scam_type: Type of scam
            language: Language code
            
        Returns:
            Explanation text
        """
        explanation_key = f"{scam_type}_explanation"
        return self.get_text(explanation_key, language)
    
    def get_warning_message(self, scam_type: str, language: str = 'en') -> str:
        """
        Get warning message for a specific scam type
        
        Args:
            scam_type: Type of scam
            language: Language code
            
        Returns:
            Warning message
        """
        warning_key = f"{scam_type}_warning"
        return self.get_text(warning_key, language)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return self.supported_languages
    
    def add_translation(self, language: str, translations: Dict[str, str]):
        """
        Add translations for a new language
        
        Args:
            language: Language code
            translations: Dictionary of key-value translations
        """
        if language not in self.translations:
            self.translations[language] = {}
        
        self.translations[language].update(translations)
        logging.info(f"Added {len(translations)} translations for {language}")
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            'en': 'English',
            'hi': 'हिंदी'
        }
        return language_names.get(language_code, language_code)
