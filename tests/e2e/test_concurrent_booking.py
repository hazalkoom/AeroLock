import pytest
import httpx
import asyncio
import uuid

BASE_URL = "http://localhost:8000/api/v1"

async def attempt_lock(client: httpx.AsyncClient, flight_id: str, seat_id: str, run_id: str, user_index: int):
    payload = {"flight_id": flight_id, "seat_id": seat_id}
    unique_ip = f"10.{int(run_id[:2], 16) % 255}.{int(run_id[2:4], 16) % 255}.{user_index + 1}"
    headers = {"X-Forwarded-For": unique_ip}
    
    return await client.post(f"{BASE_URL}/booking/lock", json=payload, headers=headers)

@pytest.mark.asyncio
async def test_concurrent_seat_locking(get_fresh_seat, auth_headers):
    flight_id, seat_id = get_fresh_seat

    run_id = uuid.uuid4().hex
    async with httpx.AsyncClient() as client:
        tasks = [attempt_lock(client, flight_id, seat_id, run_id, i) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        
        success_count = 0
        conflict_count = 0
        
        success_token = None
        for res in responses:
            if res.status_code == 200:
                success_count += 1
                success_token = res.json()["token"]
            elif res.status_code == 409:
                conflict_count += 1
                
        assert success_count == 1, f"CRITICAL: {success_count} users acquired the lock!"
        assert conflict_count == 9, f"Expected 9 conflicts, got {conflict_count}"

        if success_token:
            winner_ip = f"10.{int(run_id[:2], 16) % 255}.{int(run_id[2:4], 16) % 255}.100"
            confirm_payload = {
                "seat_id": seat_id,
                "user_id": "concurrent_winner",
                "token": success_token,
                "idempotency_key": str(uuid.uuid4())
            }
            confirm_headers = {"X-Forwarded-For": winner_ip}
            confirm_headers.update(auth_headers)
            
            confirm_res = await client.post(
                f"{BASE_URL}/booking/confirm",
                json=confirm_payload,
                headers=confirm_headers
            )
            assert confirm_res.status_code == 200