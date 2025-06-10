import re
import requests
import logging
from urllib.parse import urlparse
from typing import List, Dict, Any

class LinkAnalyzer:
    """Analyze links for suspicious content"""
    
    def __init__(self):
        """Initialize link analyzer with suspicious patterns"""
        self.suspicious_domains = {
            # Common suspicious domain patterns
            'bit.ly', 'tinyurl.com', 'short.link', 't.co', 'goo.gl',
            'ow.ly', 'buff.ly', 'is.gd', 'tiny.cc', 'tr.im'
        }
        
        self.suspicious_patterns = [
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
            r'[a-z0-9]+-[a-z0-9]+-[a-z0-9]+\.',  # Randomly generated domains
            r'[0-9]+[a-z]+[0-9]+\.',  # Mixed numbers and letters
            r'\.tk$|\.ml$|\.ga$|\.cf$',  # Free domain extensions
            r'[a-z]{20,}\.',  # Very long domain names
        ]
        
        self.phishing_keywords = [
            'login', 'signin', 'verify', 'secure', 'account', 'bank',
            'paypal', 'amazon', 'google', 'microsoft', 'apple',
            'update', 'confirm', 'suspended', 'expired'
        ]
        
        logging.info("LinkAnalyzer initialized")
    
    def extract_links(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(url_pattern, text, re.IGNORECASE)
        return links
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a single URL for suspicious indicators
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            
            risk_score = 0
            risk_factors = []
            
            # Check domain against suspicious list
            if domain in self.suspicious_domains:
                risk_score += 3
                risk_factors.append("URL shortener service")
            
            # Check for suspicious domain patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, domain):
                    risk_score += 2
                    risk_factors.append(f"Suspicious domain pattern: {pattern}")
            
            # Check for phishing keywords in path
            for keyword in self.phishing_keywords:
                if keyword in path:
                    risk_score += 1
                    risk_factors.append(f"Phishing keyword: {keyword}")
            
            # Check domain length and characteristics
            if len(domain) > 50:
                risk_score += 1
                risk_factors.append("Unusually long domain name")
            
            # Count subdomains
            subdomain_count = domain.count('.') - 1
            if subdomain_count > 3:
                risk_score += 1
                risk_factors.append("Too many subdomains")
            
            # Check for HTTPS
            if parsed_url.scheme != 'https':
                risk_score += 1
                risk_factors.append("Not using HTTPS")
            
            # Determine risk level
            if risk_score >= 5:
                risk_level = "high"
            elif risk_score >= 3:
                risk_level = "medium"
            elif risk_score >= 1:
                risk_level = "low"
            else:
                risk_level = "safe"
            
            return {
                'url': url,
                'domain': domain,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'is_suspicious': risk_score >= 2
            }
            
        except Exception as e:
            logging.error(f"Error analyzing URL {url}: {str(e)}")
            return {
                'url': url,
                'domain': 'unknown',
                'risk_level': 'unknown',
                'risk_score': 0,
                'risk_factors': ['Analysis failed'],
                'is_suspicious': True  # Err on the side of caution
            }
    
    def analyze_links_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze all links found in text
        
        Args:
            text: Text containing potential links
            
        Returns:
            List of analysis results for each link
        """
        links = self.extract_links(text)
        results = []
        
        for link in links:
            analysis = self.analyze_url(link)
            results.append(analysis)
        
        logging.info(f"Analyzed {len(results)} links in text")
        return results
    
    def check_url_reputation(self, url: str) -> Dict[str, Any]:
        """
        Check URL reputation (simplified version - in production would use real services)
        
        Args:
            url: URL to check
            
        Returns:
            Reputation check results
        """
        try:
            # Simple check - try to resolve the domain
            response = requests.head(url, timeout=5, allow_redirects=True)
            
            # Check response characteristics
            suspicious_headers = []
            if 'server' in response.headers:
                server = response.headers['server'].lower()
                if any(sus in server for sus in ['nginx/1.', 'apache/2.2']):
                    suspicious_headers.append("Outdated server version")
            
            # Check for redirects
            redirect_count = len(response.history)
            if redirect_count > 3:
                suspicious_headers.append("Too many redirects")
            
            return {
                'accessible': True,
                'status_code': response.status_code,
                'redirect_count': redirect_count,
                'suspicious_headers': suspicious_headers,
                'final_url': response.url
            }
            
        except requests.RequestException as e:
            logging.error(f"Could not check URL reputation for {url}: {str(e)}")
            return {
                'accessible': False,
                'error': str(e),
                'suspicious_headers': ['Connection failed']
            }
    
    def get_domain_age_estimate(self, domain: str) -> str:
        """
        Estimate domain age (simplified - real implementation would use WHOIS)
        
        Args:
            domain: Domain to check
            
        Returns:
            Age estimate
        """
        # Simplified heuristic based on domain characteristics
        if any(indicator in domain for indicator in ['2023', '2024', 'new', 'temp']):
            return "Very new (suspicious)"
        elif len(domain) < 6:
            return "Likely established"
        else:
            return "Unknown age"
