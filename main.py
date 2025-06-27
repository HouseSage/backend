from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_router, public_router
from app.core.exceptions import register_exception_handlers, APIException
from app.db.database import SessionLocal, engine
from app.models import models

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
