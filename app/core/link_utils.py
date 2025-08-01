from typing import Optional, Dict, Any
import base64
import json
from datetime import datetime

class LinkProcessor:
    """
    Generic link processor for different link types.
    Handles type-based link processing without diverging from the data schema.
    """
    
    @staticmethod
    def process_link_redirect(link_data: Dict[str, Any], request_info: Dict[str, Any] = None) -> str:
        """
        Process a link based on its type and return the appropriate redirect URL.
        
        Args:
            link_data: Link data containing type and redirect logic
            request_info: Optional request information (user agent, IP, etc.)
            
        Returns:
            str: The URL to redirect to
        """
        link_type = link_data.get('type', 'simple')
        
        if link_type == 'simple':
            return LinkProcessor._process_simple_link(link_data)
        elif link_type == 'round_robin':
            return LinkProcessor._process_round_robin_link(link_data)
        elif link_type == 'complex':
            return LinkProcessor._process_complex_link(link_data, request_info)
        else:
            raise ValueError(f"Unknown link type: {link_type}")
    
    @staticmethod
    def _process_simple_link(link_data: Dict[str, Any]) -> str:
        """Process a simple redirect link."""
        return link_data.get('url', '')
    
    @staticmethod
    def _process_round_robin_link(link_data: Dict[str, Any]) -> str:
        """Process a round-robin link by rotating through URLs."""
        urls = link_data.get('urls', [])
        if not urls:
            raise ValueError("Round robin link must have at least one URL")
        
        # Simple round-robin: use current timestamp to pick URL
        # In production, you might want to store state in Redis or database
        import time
        index = int(time.time()) % len(urls)
        return urls[index]
    
    @staticmethod
    def _process_complex_link(link_data: Dict[str, Any], request_info: Dict[str, Any] = None) -> str:
        """Process a complex link with rules."""
        rules = link_data.get('rules', {})
        
        if not request_info:
            # No request info, use default
            return rules.get('else', '')
        
        user_agent = request_info.get('user_agent', '').lower()
        
        # Simple device detection
        if 'android' in user_agent and 'android' in rules:
            return rules['android']
        elif ('iphone' in user_agent or 'ipad' in user_agent) and 'iphone' in rules:
            return rules['iphone']
        else:
            return rules.get('else', '')
    
    @staticmethod
    def is_password_protected(link_data: Dict[str, Any]) -> bool:
        """Check if a link is password protected."""
        return bool(link_data.get('password'))
    
    @staticmethod
    def verify_password(link_data: Dict[str, Any], password: str) -> bool:
        """Verify if the provided password matches the link's password."""
        return link_data.get('password') == password
    
    @staticmethod
    def is_expired(link_data: Dict[str, Any]) -> bool:
        """Check if a link has expired."""
        expires_at = link_data.get('expires_at')
        if not expires_at:
            return False
        
        try:
            if isinstance(expires_at, str):
                expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            else:
                expiry_date = expires_at
            return datetime.utcnow() > expiry_date.replace(tzinfo=None)
        except:
            return False
    
    @staticmethod
    def should_track(link_data: Dict[str, Any]) -> bool:
        """Check if events should be tracked for this link."""
        return link_data.get('track', True)  # Default to tracking enabled

# Legacy alias for backward compatibility
class LinkEncoder:
    """Legacy class - use LinkProcessor instead."""
    
    @staticmethod
    def encode_link_data(link_data: Dict[str, Any]) -> str:
        """Legacy method - keeping for backward compatibility."""
        json_str = json.dumps(link_data, separators=(',', ':'))
        return base64.urlsafe_b64encode(json_str.encode()).decode().rstrip('=')
    
    @staticmethod
    def decode_link_data(encoded_data: str) -> Dict[str, Any]:
        """Legacy method - keeping for backward compatibility."""
        padding = '=' * (4 - (len(encoded_data) % 4) if len(encoded_data) % 4 != 0 else 0)
        decoded_bytes = base64.urlsafe_b64decode(encoded_data + padding)
        return json.loads(decoded_bytes.decode())
    
    @staticmethod
    def is_password_protected(link_data: Dict[str, Any]) -> bool:
        """Legacy method - use LinkProcessor instead."""
        return LinkProcessor.is_password_protected(link_data)
    
    @staticmethod
    def verify_password(link_data: Dict[str, Any], password: str) -> bool:
        """Legacy method - use LinkProcessor instead."""
        return LinkProcessor.verify_password(link_data, password)
