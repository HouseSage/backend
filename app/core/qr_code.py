"""
QR Code generation utilities for links.
"""
import io
import qrcode
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional

def generate_qr_code(url: str, box_size: int = 10, border: int = 4) -> bytes:
    """
    Generate a QR code for the given URL.
    
    Args:
        url: The URL to encode in the QR code
        box_size: Size of each box in the QR code (default: 10)
        border: Border size in boxes (default: 4)
        
    Returns:
        Bytes containing the QR code image in PNG format
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )

def get_qr_code_response(url: str, box_size: int = 10, border: int = 4) -> StreamingResponse:
    """
    Generate a QR code and return it as a streaming response.
    
    Args:
        url: The URL to encode in the QR code
        box_size: Size of each box in the QR code (default: 10)
        border: Border size in boxes (default: 4)
        
    Returns:
        StreamingResponse containing the QR code image
    """
    qr_code = generate_qr_code(url, box_size, border)
    return StreamingResponse(
        io.BytesIO(qr_code),
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=qr_code.png"}
    )
