import pytest
import httpx
import uuid
import random

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_idempotent_booking_retry(get_fresh_seat, auth_headers):
    flight_id, seat_id = get_fresh_seat
    idem_key = str(uuid.uuid4())
    user_id = "retry_user_123"

    run_hex = uuid.uuid4().hex
    headers = {"X-Forwarded-For": f"10.{int(run_hex[:2], 16) % 255}.{int(run_hex[2:4], 16) % 255}.{random.randint(1, 200)}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # 1. Lock the seat
        lock_res = await client.post(f"{BASE_URL}/booking/lock", json={"flight_id": flight_id, "seat_id": seat_id})
        assert lock_res.status_code == 200
        token = lock_res.json()["token"]

        confirm_payload = {
            "seat_id": seat_id,
            "user_id": user_id,
            "token": token,
            "idempotency_key": idem_key
        }

        # 2. Confirm First Time (Should Succeed)
        confirm_req_headers = {**headers, **auth_headers}
        confirm_res_1 = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload, headers=confirm_req_headers)
        assert confirm_res_1.status_code == 200
        
        # 3. Network Retry! App sends the exact same request again.
        confirm_res_2 = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload, headers=confirm_req_headers)
        
        assert confirm_res_2.status_code == 400
        assert "Duplicate" in confirm_res_2.json()["detail"] or "invalid token" in confirm_res_2.json()["detail"]