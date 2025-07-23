from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.core.config import settings

from app.api import api_router, public_router
from app.core.exceptions import register_exception_handlers, APIException
from app.db.database import SessionLocal, engine
from app.models import models
from slowapi.middleware import SlowAPIMiddleware

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A powerful URL shortener with analytics and link management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
# Include public routes (like redirects) without API versioning
app.include_router(public_router)

# Register exception handlers
register_exception_handlers(app)

# Set up rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

app.add_middleware(SlowAPIMiddleware)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Dependency that provides a database session and ensures it is closed after use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
