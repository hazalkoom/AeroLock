import pytest
import httpx
import uuid
import random

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_successful_booking_flow(get_fresh_seat, auth_headers):
    flight_id, seat_id = get_fresh_seat
    
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1, 10000)}"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        # 1. Acquire Lock
        lock_payload = {"flight_id": flight_id, "seat_id": seat_id}
        lock_res = await client.post(f"{BASE_URL}/booking/lock", json=lock_payload)
        assert lock_res.status_code == 200, f"Lock failed: {lock_res.text}"
        
        token = lock_res.json()["token"]
        
        # 2. Confirm Booking - needs auth
        confirm_payload = {
            "seat_id": seat_id,
            "user_id": f"cicd_user_{uuid.uuid4().hex[:6]}",  # Note: API route overrides this with JWT user_id
            "token": token,
            "idempotency_key": str(uuid.uuid4())
        }
        
        confirm_req_headers = {**headers, **auth_headers}
        confirm_res = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload, headers=confirm_req_headers)
        assert confirm_res.status_code == 200, f"Confirm failed: {confirm_res.text}"
        assert confirm_res.json()["success"] is True

@pytest.mark.asyncio
async def test_booking_exclusivity(get_fresh_seat, auth_headers):
    flight_id, seat_id = get_fresh_seat

    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1, 10000)}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # 1. Acquire Lock for first user
        lock_res = await client.post(f"{BASE_URL}/booking/lock", json={"flight_id": flight_id, "seat_id": seat_id})
        assert lock_res.status_code == 200
        token_1 = lock_res.json()["token"]

        # 2. Confirm Booking for first user
        confirm_payload_1 = {
            "seat_id": seat_id,
            "user_id": "user_first",
            "token": token_1,
            "idempotency_key": str(uuid.uuid4())
        }
        confirm_req_headers = {**headers, **auth_headers}
        confirm_res_1 = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload_1, headers=confirm_req_headers)
        assert confirm_res_1.status_code == 200
        assert confirm_res_1.json()["success"] is True

        # 3. Second user tries to lock the same seat (Should fail with 409 Conflict)
        lock_res_2 = await client.post(f"{BASE_URL}/booking/lock", json={"flight_id": flight_id, "seat_id": seat_id})
        assert lock_res_2.status_code == 409
        assert "already booked" in lock_res_2.json()["detail"].lower()