from fastapi import APIRouter, Depends, Request
from app.schemas.booking import LockRequest, ConfirmBookingRequest
from app.clients.inventory_client import InventoryClient
from app.middleware.rate_limit import limiter
from app.core.events import publish_seat_event
from app.core.security import get_current_user

router = APIRouter()

async def get_inventory_client():
    return InventoryClient()

@router.post("/lock", summary="Lock a seat for 10 minutes")
@limiter.limit("10000/minute") 
async def acquire_lock(request: Request, payload: LockRequest, client: InventoryClient = Depends(get_inventory_client)):
    result = await client.acquire_lock(flight_id=payload.flight_id, seat_id=payload.seat_id)
    # Broadcast the seat lock to all WebSocket clients watching this flight
    await publish_seat_event(flight_id=payload.flight_id, seat_id=payload.seat_id, status="locked")
    return result


@router.post("/confirm", summary="Confirm and pay for a booked seat")
@limiter.limit("50000/minute") 
async def confirm_booking(
    request: Request, 
    payload: ConfirmBookingRequest, 
    client: InventoryClient = Depends(get_inventory_client),
    user_id: str = Depends(get_current_user)
):
    result = await client.confirm_booking(
        seat_id=payload.seat_id,
        user_id=user_id, 
        idempotency_key=payload.idempotency_key,
        token=payload.token
    )
    await publish_seat_event(flight_id=payload.seat_id, seat_id=payload.seat_id, status="confirmed")
    return result