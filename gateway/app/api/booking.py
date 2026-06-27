from fastapi import APIRouter, Depends, Request
from app.schemas.booking import LockRequest, ConfirmBookingRequest
from app.clients.inventory_client import InventoryClient
from app.middleware.rate_limit import limiter

router = APIRouter()

async def get_inventory_client():
    return InventoryClient()

@router.post("/lock", summary="Lock a seat for 10 minutes")
@limiter.limit("10/minute") 
async def acquire_lock(request: Request, payload: LockRequest, client: InventoryClient = Depends(get_inventory_client)):

    return await client.acquire_lock(flight_id=payload.flight_id, seat_id=payload.seat_id)

@router.post("/confirm", summary="Confirm and pay for a booked seat")
@limiter.limit("5/minute") 
async def confirm_booking(request: Request, payload: ConfirmBookingRequest, client: InventoryClient = Depends(get_inventory_client)):
    
    return await client.confirm_booking(
        seat_id=payload.seat_id,
        user_id=payload.user_id,
        idempotency_key=payload.idempotency_key,
        token=payload.token
    )