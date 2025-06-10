import re
import logging
from typing import Dict, List, Any

class ScamDetector:
    """Keyword-based scam detection system"""
    
    def __init__(self):
        """Initialize scam detection patterns"""
        self.scam_patterns = {
            'upi_fraud': {
                'keywords': [
                    'send money', 'urgent payment', 'refund', 'verify account',
                    'otp', 'upi pin', 'bank details', 'account blocked',
                    'immediate action', 'suspicious activity', 'verify identity',
                    'paytm', 'phonepe', 'googlepay', 'gpay', 'bhim',
                    'transaction failed', 'payment pending', 'kyd', 'kyc',
                    'reward points', 'cashback', 'scratch card'
                ],
                'hindi_keywords': [
                    'पैसे भेजें', 'तुरंत भुगतान', 'वापसी', 'खाता सत्यापित',
                    'ओटीपी', 'यूपीआई पिन', 'बैंक विवरण', 'खाता बंद',
                    'तत्काल कार्रवाई', 'संदिग्ध गतिविधि'
                ],
                'patterns': [
                    r'\b\d{6}\b',  # 6-digit OTP pattern
                    r'upi.*pin',
                    r'account.*block',
                    r'verify.*otp'
                ]
            },
            'phishing': {
                'keywords': [
                    'click here', 'verify now', 'update details', 'suspend account',
                    'confirm identity', 'security alert', 'unauthorized access',
                    'act now', 'limited time', 'expires today', 'login failed',
                    'security breach', 'account compromised', 'verify email',
                    'reset password', 'billing information', 'payment method'
                ],
                'hindi_keywords': [
                    'यहाँ क्लिक करें', 'अभी सत्यापित करें', 'विवरण अपडेट करें',
                    'खाता स्थगित', 'पहचान की पुष्टि', 'सुरक्षा चेतावनी'
                ],
                'patterns': [
                    r'https?://[^\s]+',  # Suspicious URLs
                    r'bit\.ly|tinyurl|short',
                    r'click.*here',
                    r'verify.*account'
                ]
            },
            'job_scam': {
                'keywords': [
                    'work from home', 'easy money', 'no experience required',
                    'registration fee', 'security deposit', 'processing fee',
                    'guaranteed income', 'part time job', 'copy paste work',
                    'data entry', 'form filling', 'survey work', 'typing work',
                    'advance payment', 'training fee', 'kit charges'
                ],
                'hindi_keywords': [
                    'घर से काम', 'आसान पैसा', 'अनुभव की आवश्यकता नहीं',
                    'पंजीकरण फीस', 'सिक्योरिटी डिपॉजिट', 'प्रसंस्करण शुल्क'
                ],
                'patterns': [
                    r'earn.*\d+.*day',
                    r'registration.*fee',
                    r'work.*home',
                    r'easy.*money'
                ]
            },
            'lottery_scam': {
                'keywords': [
                    'lottery winner', 'congratulations', 'won prize', 'claim reward',
                    'lucky draw', 'selected winner', 'cash prize', 'lottery ticket',
                    'processing charges', 'tax payment', 'courier charges',
                    'delivery fee', 'insurance premium'
                ],
                'hindi_keywords': [
                    'लॉटरी विजेता', 'बधाई', 'पुरस्कार जीता', 'इनाम दावा',
                    'भाग्यशाली ड्रा', 'चुने गए विजेता'
                ],
                'patterns': [
                    r'won.*prize',
                    r'lottery.*winner',
                    r'congratulations.*selected'
                ]
            }
        }
        
        # High-risk indicators
        self.high_risk_indicators = [
            'urgent', 'immediately', 'expire', 'suspend', 'block', 'freeze',
            'unauthorized', 'suspicious', 'security', 'verify', 'confirm',
            'act now', 'limited time', 'don\'t delay', 'final notice'
        ]
        
        logging.info("ScamDetector initialized with keyword patterns")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for scam indicators
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not text or not text.strip():
            return {
                'is_scam': False,
                'scam_type': 'none',
                'confidence': 0.0,
                'keywords_found': []
            }
        
        text_lower = text.lower()
        total_score = 0
        max_category_score = 0
        detected_scam_type = 'none'
        all_keywords_found = []
        
        # Check each scam category
        for scam_type, patterns in self.scam_patterns.items():
            category_score = 0
            category_keywords = []
            
            # Check English keywords
            for keyword in patterns['keywords']:
                if keyword.lower() in text_lower:
                    category_score += 1
                    category_keywords.append(keyword)
            
            # Check Hindi keywords
            for keyword in patterns.get('hindi_keywords', []):
                if keyword in text:
                    category_score += 1
                    category_keywords.append(keyword)
            
            # Check regex patterns
            for pattern in patterns.get('patterns', []):
                if re.search(pattern, text_lower, re.IGNORECASE):
                    category_score += 2  # Patterns get higher weight
                    category_keywords.append(f"Pattern: {pattern}")
            
            # Update maximum category
            if category_score > max_category_score:
                max_category_score = category_score
                detected_scam_type = scam_type
                all_keywords_found = category_keywords
            
            total_score += category_score
        
        # Check high-risk indicators
        risk_bonus = 0
        for indicator in self.high_risk_indicators:
            if indicator.lower() in text_lower:
                risk_bonus += 0.5
                all_keywords_found.append(f"Risk: {indicator}")
        
        # Calculate confidence
        confidence = min((total_score + risk_bonus) / 10.0, 1.0)
        
        # Determine if it's a scam
        is_scam = confidence > 0.3 or max_category_score >= 2
        
        result = {
            'is_scam': is_scam,
            'scam_type': detected_scam_type if is_scam else 'none',
            'confidence': round(confidence, 2),
            'keywords_found': all_keywords_found[:10]  # Limit to top 10
        }
        
        logging.info(f"Scam analysis result: {result}")
        return result
    
    def get_scam_types(self) -> List[str]:
        """Get list of supported scam types"""
        return list(self.scam_patterns.keys())
    
    def add_custom_keywords(self, scam_type: str, keywords: List[str]):
        """Add custom keywords to a scam type"""
        if scam_type in self.scam_patterns:
            self.scam_patterns[scam_type]['keywords'].extend(keywords)
            logging.info(f"Added {len(keywords)} keywords to {scam_type}")
