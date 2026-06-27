from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import os
from app.core.logging import logger
from app.core.events import init_redis, close_redis
from app.api import booking, search
from app.api import websocket
from app.middleware.rate_limit import setup_rate_limiting, limiter
import uvicorn
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup: initialize the shared Redis connection for Pub/Sub
    await init_redis()
    logger.info("Redis Pub/Sub connection initialized.")
    yield
    # Shutdown: close the Redis connection cleanly
    await close_redis()
    logger.info("Redis Pub/Sub connection closed.")


app = FastAPI(
    title="AeroLock API Gateway",
    description="REST to gRPC translation layer with Rate Limiting, JSON Logging, and Real-Time WebSocket seat events.",
    version="1.1.0",
    lifespan=lifespan,
)

# 1. Initialize Rate Limiting
setup_rate_limiting(app)

# 2. Global Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Spits out a beautiful JSON log for every single request
    logger.info(
        f"Path: {request.url.path} | Method: {request.method} | Status: {response.status_code} | Time: {process_time:.4f}s"
    )
    return response

# The Health Check (Limited to 5 per minute so bots don't DDOS the ping)
@app.get("/health", tags=["System"])
@limiter.limit("5/minute")
async def health_check(request: Request):
    return {
        "status": "alive", 
        "service": "api-gateway",
        "inventory_target": os.getenv("INVENTORY_SERVICE_URL", "inventory-service:50052")
    }

app.include_router(booking.router, prefix="/api/v1/booking", tags=["Booking Flow"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["Real-Time"])

if __name__ == "__main__":
    gateway_port = int(os.getenv("GATEWAY_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=gateway_port, reload=True)