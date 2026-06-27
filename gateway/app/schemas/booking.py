from pydantic import BaseModel, Field

class LockRequest(BaseModel):
    flight_id: str = Field(..., description="The UUID of the flight")
    seat_id: str = Field(..., description="The UUID of the seat the user wants to lock")

class ConfirmBookingRequest(BaseModel):
    seat_id: str = Field(..., description="The UUID of the locked seat")
    user_id: str = Field(..., description="The ID of the user making the booking")
    token: str = Field(..., description="The 12-minute lock token received from Redis")
    idempotency_key: str = Field(..., description="A unique UUID to prevent double-charging the user")