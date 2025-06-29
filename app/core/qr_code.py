"""
QR Code generation utilities for links.
"""
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def get_qr_url(short_url: str) -> dict:
    """
    Return the URL for QR code generation.
    
    Args:
        short_url: The short URL to be encoded in the QR code
        
    Returns:
        Dictionary containing the URL for QR code generation
    """
    try:
        return {"url": short_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code URL: {str(e)}"
        )
