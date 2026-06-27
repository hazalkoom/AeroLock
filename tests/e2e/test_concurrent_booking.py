import pytest
import httpx
import asyncio
import asyncpg
import uuid

BASE_URL = "http://localhost:8000/api/v1"
DB_URL = "postgresql://aerolock_user:password123@localhost:5432/aerolock"

async def get_fresh_seat():
    conn = await asyncpg.connect(DB_URL)
    query = """
        SELECT s.flight_id, s.id 
        FROM seats s 
        LEFT JOIN bookings b ON s.id = b.seat_id 
        WHERE s.status = 'available' AND b.id IS NULL 
        LIMIT 1
    """
    row = await conn.fetchrow(query)
    await conn.close()
    if not row:
        pytest.skip("No available seats left in the database.")
    return str(row['flight_id']), str(row['id'])

async def attempt_lock(client: httpx.AsyncClient, flight_id: str, seat_id: str, run_id: str, user_index: int):
    """Simulates a unique user bypassing the rate limiter with a globally unique spoofed IP."""
    payload = {"flight_id": flight_id, "seat_id": seat_id}
    # Use a UUID-based unique octets so IPs never collide between test runs
    unique_ip = f"10.{int(run_id[:2], 16) % 255}.{int(run_id[2:4], 16) % 255}.{user_index + 1}"
    headers = {"X-Forwarded-For": unique_ip}
    
    return await client.post(f"{BASE_URL}/booking/lock", json=payload, headers=headers)

@pytest.mark.asyncio
async def test_concurrent_seat_locking():
    """
    Tests database row-level locking. 10 unique users fight for 1 dynamic seat.
    """
    flight_id, seat_id = await get_fresh_seat()

    run_id = uuid.uuid4().hex  # Unique per test run — prevents rate limit bleed
    async with httpx.AsyncClient() as client:
        # Fire 10 concurrent requests at the exact same seat, each with a unique IP
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
                
        # 1 lock acquired, 9 rejected. Perfect CI/CD concurrency test.
        assert success_count == 1, f"CRITICAL: {success_count} users acquired the lock!"
        assert conflict_count == 9, f"Expected 9 conflicts, got {conflict_count}"

        # Clean up: Confirm booking for the winner to release lock and mark seat booked
        if success_token:
            winner_ip = f"10.{int(run_id[:2], 16) % 255}.{int(run_id[2:4], 16) % 255}.100"
            confirm_payload = {
                "seat_id": seat_id,
                "user_id": "concurrent_winner",
                "token": success_token,
                "idempotency_key": str(uuid.uuid4())
            }
            confirm_res = await client.post(
                f"{BASE_URL}/booking/confirm",
                json=confirm_payload,
                headers={"X-Forwarded-For": winner_ip}
            )
            assert confirm_res.status_code == 200