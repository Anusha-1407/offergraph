import os
import time
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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

# High-performance in-memory sliding window rate limiter
_RATE_LIMITS = defaultdict(list)
RATE_LIMIT_WINDOW = 60 # seconds
MAX_REQUESTS_PER_WINDOW = 120 # requests per minute per client IP

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

# Security Headers & Rate Limiting Middleware
@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    # Rate limit check for /api endpoints
    if request.url.path.startswith("/api/"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        requests_history = _RATE_LIMITS[client_ip]
        # Purge entries older than window
        _RATE_LIMITS[client_ip] = [t for t in requests_history if now - t < RATE_LIMIT_WINDOW]
        if len(_RATE_LIMITS[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Rate limit exceeded (120 req/min). Please try again later."}
            )
        _RATE_LIMITS[client_ip].append(now)

    response: Response = await call_next(request)

    # Industry-standard HTTP Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

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

# Register API routers
app.include_router(dashboard.router)
app.include_router(analyze.router)
app.include_router(reports.router)
app.include_router(entities.router)
app.include_router(graph.router)
app.include_router(chat.router)
app.include_router(safety.router)

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "OfferGraph API"}

# Unified deployment support: serve frontend static build if available
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if not os.path.exists(frontend_dist):
    frontend_dist = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "name": "OfferGraph Intelligence API",
            "version": "1.0.0",
            "status": "operational",
            "docs_url": "/docs",
            "tagline": "Don't just detect suspicious offers. Connect the evidence."
        }
