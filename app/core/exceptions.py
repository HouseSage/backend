from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class APIException(HTTPException):
    """Base API exception with standardized error format."""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        error_payload = {
            "error": {
                "code": error_code or f"HTTP_{status_code}",
                "message": message,
            }
        }
        
        if details is not None:
            error_payload["error"]["details"] = details
            
        super().__init__(
            status_code=status_code,
            detail=error_payload,
            headers=headers
        )


class BadRequestException(APIException):
    """400 Bad Request"""
    def __init__(self, message: str = "Bad Request", details: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            error_code="bad_request",
            details=details
        )


class UnauthorizedException(APIException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Unauthorized", details: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="unauthorized",
            details=details
        )


class ForbiddenException(APIException):
    """403 Forbidden"""
    def __init__(self, message: str = "Forbidden", details: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="forbidden",
            details=details
        )


class NotFoundException(APIException):
    """404 Not Found"""
    def __init__(self, resource: str = "Resource", details: Any = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{resource} not found",
            error_code="not_found",
            details=details
        )


class ConflictException(APIException):
    """409 Conflict"""
    def __init__(self, message: str = "Conflict", details: Any = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code="conflict",
            details=details
        )


class ValidationException(APIException):
    """422 Unprocessable Entity"""
    def __init__(self, message: str = "Validation Error", details: Any = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error_code="validation_error",
            details=details
        )


def register_exception_handlers(app):
    """Register exception handlers for the FastAPI app."""
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers=exc.headers
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Validation Error",
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(404)
    async def not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "not_found",
                    "message": "The requested resource was not found"
                }
            }
        )
    
    @app.exception_handler(500)
    async def internal_server_error_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred"
                }
            }
        )
