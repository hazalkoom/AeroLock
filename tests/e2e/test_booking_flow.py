import pytest
import httpx
import uuid
import asyncpg

BASE_URL = "http://localhost:8000/api/v1"
DB_URL = "postgresql://aerolock_user:password123@localhost:5432/aerolock"

async def get_fresh_seat():
    conn = await asyncpg.connect(DB_URL)
    # Find a seat that exists and has no corresponding entry in the bookings table
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
        pytest.skip("No truly available seats left.")
    return str(row['flight_id']), str(row['id'])


@pytest.mark.asyncio
async def test_successful_booking_flow():
    """
    Dynamically fetches an available seat, locks it, and books it. 
    Can be run 10,000 times in CI/CD without resetting the DB (until seats run out).
    """
    flight_id, seat_id = await get_fresh_seat()

    import random
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1, 10000)}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # 1. Acquire Lock
        lock_payload = {"flight_id": flight_id, "seat_id": seat_id}
        lock_res = await client.post(f"{BASE_URL}/booking/lock", json=lock_payload)
        assert lock_res.status_code == 200, f"Lock failed: {lock_res.text}"
        
        token = lock_res.json()["token"]
        
        # 2. Confirm Booking
        confirm_payload = {
            "seat_id": seat_id,
            "user_id": f"cicd_user_{uuid.uuid4().hex[:6]}",
            "token": token,
            "idempotency_key": str(uuid.uuid4())
        }
        
        confirm_res = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload)
        assert confirm_res.status_code == 200, f"Confirm failed: {confirm_res.text}"
        assert confirm_res.json()["success"] is True


@pytest.mark.asyncio
async def test_booking_exclusivity():
    """
    Test that once a seat is successfully booked, it cannot be locked again.
    """
    flight_id, seat_id = await get_fresh_seat()

    import random
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
        confirm_res_1 = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload_1)
        assert confirm_res_1.status_code == 200
        assert confirm_res_1.json()["success"] is True

        # 3. Second user tries to lock the same seat (Should fail with 409 Conflict)
        lock_res_2 = await client.post(f"{BASE_URL}/booking/lock", json={"flight_id": flight_id, "seat_id": seat_id})
        assert lock_res_2.status_code == 409
        assert "already booked" in lock_res_2.json()["detail"].lower()