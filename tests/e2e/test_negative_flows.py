import pytest
import httpx
import uuid

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_lock_nonexistent_seat():
    """Negative: Try to lock a seat that is completely fake."""
    import uuid
    run_hex = uuid.uuid4().hex
    headers = {"X-Forwarded-For": f"10.{int(run_hex[:2], 16) % 255}.{int(run_hex[2:4], 16) % 255}.50"}
    async with httpx.AsyncClient(headers=headers) as client:
        payload = {
            "flight_id": str(uuid.uuid4()), 
            "seat_id": str(uuid.uuid4())
        }
        res = await client.post(f"{BASE_URL}/booking/lock", json=payload)
        
        # The Inventory gRPC should check the DB, see the seat doesn't exist, and return a failure.
        # The Gateway translates that failure into a 409 Conflict.
        assert res.status_code == 409
        assert "Seat does not exist" in res.json()["detail"]

@pytest.mark.asyncio
async def test_confirm_invalid_token():
    """Negative: Try to confirm a booking using a fake Redis token."""
    import uuid
    run_hex = uuid.uuid4().hex
    headers = {"X-Forwarded-For": f"10.{int(run_hex[:2], 16) % 255}.{int(run_hex[2:4], 16) % 255}.51"}
    async with httpx.AsyncClient(headers=headers) as client:
        payload = {
            "seat_id": str(uuid.uuid4()),
            "user_id": "hacker_99",
            "token": "fake-bullshit-token",
            "idempotency_key": str(uuid.uuid4())
        }
        res = await client.post(f"{BASE_URL}/booking/confirm", json=payload)
        
        # Redis Lua script will fail to match the token, so it returns a failure.
        # The Gateway translates that into a 400 Bad Request.
        assert res.status_code == 400
        assert "expired or invalid" in res.json()["detail"].lower()