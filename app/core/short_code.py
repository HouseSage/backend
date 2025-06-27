"""Short code generation and validation utilities for the link shortener."""
import random
import string
from typing import Optional

from app.core.config import settings

ALPHABET = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
AMBIGUOUS_CHARS = "0O1lI"  # Characters that can be confused
SAFE_ALPHABET = ''.join(c for c in ALPHABET if c not in AMBIGUOUS_CHARS)

def generate_short_code(length: Optional[int] = None) -> str:
    """
    Generate a random short code of the specified length.
    
    Args:
        length: Length of the short code. If None, uses the default from settings.
        
    Returns:
        A randomly generated short code.
    """
    if length is None:
        length = settings.SHORT_CODE_LENGTH
    return ''.join(random.choices(SAFE_ALPHABET, k=length))

def is_valid_short_code(code: str) -> bool:
    """
    Check if a short code is valid.
    
    Args:
        code: The short code to validate.
        
    Returns:
        bool: True if the short code is valid, False otherwise.
    """
    if not code:
        return False
    
    if len(code) > settings.MAX_SHORT_CODE_LENGTH:
        return False
    return all(c in SAFE_ALPHABET for c in code)

def generate_unique_short_code(db, max_attempts: int = 10, length: Optional[int] = None) -> Optional[str]:
    """
    Generate a unique short code that doesn't exist in the database.
    
    Args:
        db: Database session
        max_attempts: Maximum number of attempts to generate a unique code
        length: Length of the short code. If None, uses the default from settings.
        
    Returns:
        A unique short code, or None if unable to generate one.
    """
    from app.crud import crud_link
    
    for _ in range(max_attempts):
        code = generate_short_code(length)
        if not crud_link.get_link_by_short_code(db, code):
            return code
    
    return None
