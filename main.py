from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api import api_router
from app.db.database import SessionLocal, engine
from app.models import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API", description="URL shortener and analytics API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
