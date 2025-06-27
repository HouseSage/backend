from typing import Optional, Dict, Any
import base64
import json

class LinkEncoder:
    """
    Utility class for encoding and decoding link data.
    Handles serialization/deserialization of link data including passwords and metadata.
    """
    
    @staticmethod
    def encode_link_data(link_data: Dict[str, Any]) -> str:
        """
        Encode link data to a URL-safe base64 string.
        
        Args:
            link_data: Dictionary containing link data including URL, password, etc.
            
        Returns:
            str: URL-safe base64 encoded string
        """
        json_str = json.dumps(link_data, separators=(',', ':'))
        return base64.urlsafe_b64encode(json_str.encode()).decode().rstrip('=')
    
    @staticmethod
    def decode_link_data(encoded_data: str) -> Dict[str, Any]:
        """
        Decode URL-safe base64 string back to link data.
        
        Args:
            encoded_data: URL-safe base64 encoded string
            
        Returns:
            Dict containing the decoded link data
        """
        # Add padding back if needed
        padding = '=' * (4 - (len(encoded_data) % 4) if len(encoded_data) % 4 != 0 else 0)
        decoded_bytes = base64.urlsafe_b64decode(encoded_data + padding)
        return json.loads(decoded_bytes.decode())
    
    @staticmethod
    def is_password_protected(link_data: Dict[str, Any]) -> bool:
        """Check if a link is password protected."""
        return bool(link_data.get('password'))
    
    @staticmethod
    def verify_password(link_data: Dict[str, Any], password: str) -> bool:
        """Verify if the provided password matches the link's password."""
        return link_data.get('password') == password
