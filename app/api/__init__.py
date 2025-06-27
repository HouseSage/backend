from fastapi import APIRouter

# Main API router for versioned API endpoints
api_router = APIRouter()
# Public router for non-versioned endpoints like redirects
public_router = APIRouter()

# Register all resource routers with the main API router
from . import spaces, pixels, users, domains, links, events, redirect
from .spaces import router as spaces_router
from .pixels import router as pixels_router
from .users import router as users_router
from .domains import router as domains_router
from .links import router as links_router
from .events import router as events_router
from .redirect import router as redirect_router

# Include versioned API routes
api_router.include_router(spaces_router, prefix="/spaces", tags=["spaces"])
api_router.include_router(pixels_router, prefix="/pixels", tags=["pixels"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(domains_router, prefix="/domains", tags=["domains"])
api_router.include_router(links_router, prefix="/links", tags=["links"])
api_router.include_router(events_router, prefix="/events", tags=["events"])

# Include public routes (non-versioned)
public_router.include_router(redirect_router, prefix="", tags=["redirects"])
