import pytest
import httpx

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_search_valid_route():
    """Positive: Standard search should return 200 and a list of flights."""
    import random
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1, 10000)}"}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.get(f"{BASE_URL}/search/?origin=CAI&destination=DXB&date=2026-12-01")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        data = res.json()
        assert isinstance(data, list)
        assert len(data) > 0, "No flights returned from DB"
        assert "available_seats" in data[0], "Response missing gRPC mapped fields"

@pytest.mark.asyncio
async def test_search_invalid_airport_code():
    """Negative: Gateway should block invalid parameters before hitting gRPC."""
    import random
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1, 10000)}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # 'NY' is 2 letters, Pydantic requires min_length=3
        res = await client.get(f"{BASE_URL}/search/?origin=NY&destination=DXB&date=2026-12-01")
        
        # Expecting a 422 Unprocessable Entity directly from FastAPI
        assert res.status_code == 422
        assert "detail" in res.json()