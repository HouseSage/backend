from fastapi import APIRouter

api_router = APIRouter()


from . import spaces, pixels  
from .spaces import router as spaces_router
from .pixels import router as pixels_router

api_router.include_router(spaces_router, prefix="/spaces", tags=["spaces"])
api_router.include_router(pixels_router, prefix="/pixels", tags=["pixels"])
