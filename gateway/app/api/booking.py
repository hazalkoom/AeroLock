from fastapi import APIRouter, Depends
from app.schemas.booking import LockRequest, ConfirmBookingRequest
from app.clients.inventory_client import InventoryClient

router = APIRouter()

# Dependency to get the client
async def get_inventory_client():
    return InventoryClient()

@router.post("/lock", summary="Lock a seat for 12 minutes")
async def acquire_lock(request: LockRequest, client: InventoryClient = Depends(get_inventory_client)):
    """
    Attempts to temporarily lock a seat. 
    If successful, returns a token that MUST be used to confirm the booking.
    """
    return await client.acquire_lock(seat_id=request.seat_id)

@router.post("/confirm", summary="Confirm and pay for a booked seat")
async def confirm_booking(request: ConfirmBookingRequest, client: InventoryClient = Depends(get_inventory_client)):
    """
    Finalizes the booking. Requires the original lock token and an idempotency key 
    to prevent double-charging.
    """
    return await client.confirm_booking(
        seat_id=request.seat_id,
        user_id=request.user_id,
        idempotency_key=request.idempotency_key,
        token=request.token
    )