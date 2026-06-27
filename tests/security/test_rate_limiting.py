import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_search_rate_limiting():
    """
    Test that the search endpoint is rate limited to 20 requests per minute per IP.
    """
    import random
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1000, 9999)}"}  # Unique IP for this test
    
    async with httpx.AsyncClient(headers=headers) as client:
        # Send 20 successful requests
        for _ in range(20):
            res = await client.get(f"{BASE_URL}/search/?origin=CAI&destination=DXB&date=2024-12-01")
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            
        # The 21st request should be rate limited (429)
        res = await client.get(f"{BASE_URL}/search/?origin=CAI&destination=DXB&date=2024-12-01")
        assert res.status_code == 429, f"Expected 429 Too Many Requests, got {res.status_code}"

@pytest.mark.asyncio
async def test_lock_rate_limiting():
    """
    Test that the booking lock endpoint is rate limited to 10 requests per minute per IP.
    """
    import random
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1000, 9999)}"}  # Unique IP for this test
    payload = {"flight_id": "00000000-0000-0000-0000-000000000000", "seat_id": "00000000-0000-0000-0000-000000000000"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        # Send 10 requests. (We don't care if they fail with 404/400 from business logic, 
        # the rate limiter executes before business logic in SlowAPI).
        for _ in range(10):
            res = await client.post(f"{BASE_URL}/booking/lock", json=payload)
            # Even if it's 404 (seat not found), it shouldn't be 429 yet.
            assert res.status_code != 429, f"Got 429 too early on request {_}"
            
        # The 11th request should be rate limited (429)
        res = await client.post(f"{BASE_URL}/booking/lock", json=payload)
        assert res.status_code == 429, f"Expected 429 Too Many Requests, got {res.status_code}"
