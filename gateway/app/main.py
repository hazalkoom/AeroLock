from fastapi import FastAPI
from app.core.config import settings
from app.api import booking
import uvicorn

app = FastAPI(
    title="AeroLock API Gateway",
    description="REST to gRPC translation layer for the AeroLock system.",
    version="1.0.0"
)

# The Health Check
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "alive", 
        "service": "api-gateway",
        "inventory_target": settings.INVENTORY_SERVICE_URL
    }

# --- REGISTER YOUR ROUTERS HERE ---
app.include_router(booking.router, prefix="/api/v1/booking", tags=["Booking Flow"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.GATEWAY_PORT, reload=True)