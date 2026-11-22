import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base, SessionLocal
from .seed import seed_database
from .routers import (
    dashboard,
    analyze,
    reports,
    entities,
    graph,
    chat,
    safety
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & demo seed on startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db, force_reset=False)
    finally:
        db.close()
    yield

app = FastAPI(
    title="OfferGraph Intelligence API",
    description="Backend API for OfferGraph — AI-Powered Recruitment Fraud Intelligence & Network Correlation Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173")
origins = [o.strip() for o in origins_str.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(analyze.router)
app.include_router(reports.router)
app.include_router(entities.router)
app.include_router(graph.router)
app.include_router(chat.router)
app.include_router(safety.router)

@app.get("/")
def root():
    return {
        "name": "OfferGraph Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "tagline": "Don't just detect suspicious offers. Connect the evidence."
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "OfferGraph API"}
