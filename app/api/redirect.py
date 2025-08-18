from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query, Form, Path, Depends
from typing import Optional, Dict, Any, List
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session

from uuid import UUID
import json
import logging
from pydantic import BaseModel, HttpUrl

from app.db.database import SessionLocal, get_db
from app.models import models
from app.crud import crud_link, crud_event
from app.core.link_utils import LinkEncoder, LinkProcessor  # Support both old and new
from app.core.config import settings
from app.core.exceptions import NotFoundException, ForbiddenException, UnauthorizedException, BadRequestException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Helper functions for raising standard exceptions
def raise_link_not_found(detail: str = "Link not found or inactive"):
    raise NotFoundException(detail)

def raise_password_required(detail: str = "Password required"):
    raise ForbiddenException(detail)

def raise_invalid_password(detail: str = "Invalid password"):
    raise UnauthorizedException(detail)

# Dependency to get form data

class RedirectResponseModel(BaseModel):
    """Response model for link redirection."""
    redirect_url: Optional[HttpUrl] = None
    requires_password: bool = False
    link_data: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
        json_encoders = {
            'HttpUrl': lambda v: str(v) if v else None
        }

class PasswordVerificationRequest(BaseModel):
    """Request model for password verification."""
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "password": "your-password-here"
            }
        }

async def get_link_or_raise(
    db: Session, 
    short_code: str, 
    domain: str
) -> models.Link:
    """Helper function to get a link or raise appropriate exceptions."""
    db_link = crud_link.get_link_by_domain_and_short_code(
        db, short_code=short_code, domain_id=domain
    )
    
    if not db_link:
        logger.warning(f"Link not found: {short_code} (domain: {domain})")
        raise_link_not_found()
        
    if not db_link.is_active:
        logger.warning(f"Link is inactive: {short_code} (domain: {domain})")
        raise_link_not_found("This link is no longer active")
        
    return db_link

@router.get(
    "/go/{short_code}",
    response_model=RedirectResponseModel,
    summary="Redirect to the target URL",
    description="""
    This endpoint handles the redirection of shortened URLs.
    It checks if the link is active and password-protected.
    If password is required but not provided, it returns a flag indicating so.
    Also handles password verification via POST request.
    """
)
async def redirect_link(
    request: Request,
    short_code: str = Path(..., description="The short code of the link"),
    domain: str = Query(
        ..., 
        description="Required domain name for the link"
    ),
    password: Optional[str] = Query(
        None, 
        description="Password if the link is password-protected"
    ),

    db: Session = Depends(get_db)
):
    """
    Handle link redirection and password verification.
    This endpoint is used by the Next.js frontend.
    It returns either a redirect URL or indicates that a password is required.
    """
    try:
        # Get the link from database
        db_link = await get_link_or_raise(db, short_code, domain)
        link_data = db_link.link_data or {}
        
            # Check if the link is password protected
        if LinkEncoder.is_password_protected(link_data):
            if not password or not LinkEncoder.verify_password(link_data, password):
                logger.info(f"Password required for link: {short_code} (domain: {domain})")
                return RedirectResponseModel(
                    requires_password=True,
                    link_data={
                        "short_code": short_code,
                        "domain": domain,
                        "title": link_data.get("title"),
                        "has_password": True
                    }
                )
        
        # Log the click event
        try:
            event_data = {
                "ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "referrer": request.headers.get("referer"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            crud_event.create_event(
                db=db,
                event={
                    "link_id": db_link.id,
                    "type": "CLICK",
                    "event_data": event_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to log click event: {str(e)}", exc_info=True)
        
        # Get the target URL
        target_url = link_data.get("url")
        if not target_url:
            logger.error(f"No target URL found for link: {db_link.id}")
            raise BadRequestException("Invalid link configuration")
        
        # If this is an API request or form submission, return the redirect URL in the response
        if "application/json" in request.headers.get("accept", "") or request.method == "POST":
            # Fetch associated pixels
            pixels = []
            if hasattr(db_link, "pixels") and db_link.pixels:
                for pixel in db_link.pixels:
                    pixels.append({
                        "id": str(pixel.id),
                        "name": pixel.name,
                        "code": pixel.code,
                        "type": pixel.type
                    })
            link_data_response = {
                "id": str(db_link.id),
                "title": link_data.get("title"),
                "short_code": short_code,
                "domain": domain,
                "clicks": link_data.get("clicks", 0)
            }
            if pixels:
                link_data_response["pixels"] = pixels
            return RedirectResponseModel(
                redirect_url=target_url,
                requires_password=False,
                link_data=link_data_response
            )
        
        # Otherwise, perform the redirect
        response = RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
        return response
        
    except (NotFoundException, ForbiddenException, UnauthorizedException, BadRequestException):
        # Re-raise API exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing redirect: {str(e)}", exc_info=True)
        raise BadRequestException("An error occurred while processing your request") from e
