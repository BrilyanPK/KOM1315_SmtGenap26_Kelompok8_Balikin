from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.api import api_router
from app.core.config import settings
from app.core.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from app.core.database import SessionLocal
from app.core.context import client_ip_ctx
from sqlalchemy import text
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IPB Lost & Found API")

@app.middleware("http")
async def add_ip_to_context(request: Request, call_next):
    ip = request.client.host if request.client else None
    token = client_ip_ctx.set(ip)
    try:
        response = await call_next(request)
        return response
    finally:
        client_ip_ctx.reset(token)

# Setup Rate Limiting
app.state.limiter = limiter

async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Terlalu banyak percobaan. Silakan coba beberapa saat lagi."},
    )

app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Setup CORS
allowed_origins = ["*"]
if settings.FRONTEND_URL:
    allowed_origins = [settings.FRONTEND_URL]
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions so CORS headers are still included."""
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


@app.get("/")
def root():
    return {"message": "Welcome to IPB Lost & Found API"}

@app.get("/health")
def health_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"}
        )
