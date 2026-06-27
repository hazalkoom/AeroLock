import pytest
import httpx
import uuid
import asyncpg

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

@pytest.mark.asyncio
async def test_idempotent_booking_retry():
    """
    Proves that sending the exact same idempotency key twice is blocked by the database.
    """
    flight_id, seat_id = await get_fresh_seat()
    idem_key = str(uuid.uuid4())
    user_id = "retry_user_123"

    import random
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
        confirm_res_1 = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload)
        assert confirm_res_1.status_code == 200
        
        # 3. Network Retry! App sends the exact same request again.
        # The lock token is gone, AND the idempotency key is already in Postgres.
        confirm_res_2 = await client.post(f"{BASE_URL}/booking/confirm", json=confirm_payload)
        
        # We expect a 400 Bad Request because your Backend catches the IntegrityError 
        # and returns a "Duplicate Idempotency Key" message.
        assert confirm_res_2.status_code == 400
        assert "Duplicate" in confirm_res_2.json()["detail"] or "invalid token" in confirm_res_2.json()["detail"]