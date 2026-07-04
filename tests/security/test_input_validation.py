import pytest
import httpx
import uuid
import random

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_search_input_validation_sql_injection():
    """
    Test that SQL injection payloads in the search parameters are rejected 
    by FastAPI's validation before hitting the database.
    """
    # The API expects exactly 3 character airport codes.
    malicious_origin = "CAI'; DROP TABLE flights;--"
    run_hex = uuid.uuid4().hex
    headers = {"X-Forwarded-For": f"10.{int(run_hex[:2], 16) % 255}.{int(run_hex[2:4], 16) % 255}.60"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.get(f"{BASE_URL}/search/?origin={malicious_origin}&destination=DXB&date=2024-12-01")
        # FastAPI should reject this due to max_length=3 with a 422 Unprocessable Entity
        assert res.status_code == 422
        assert "value_error" in res.text or "string_too_long" in res.text

@pytest.mark.asyncio
async def test_lock_input_validation_malformed_json():
    """
    Test that malformed JSON or incorrect data types are properly handled 
    by Pydantic and do not cause a 500 Internal Server Error.
    """
    run_hex = uuid.uuid4().hex
    headers = {"X-Forwarded-For": f"10.{int(run_hex[:2], 16) % 255}.{int(run_hex[2:4], 16) % 255}.61"}
    
    # 1. Missing fields
    payload_missing = {"flight_id": str(uuid.uuid4())}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.post(f"{BASE_URL}/booking/lock", json=payload_missing)
        assert res.status_code == 422
    
    # 2. Wrong data type (list instead of string/uuid)
    payload_wrong_type = {"flight_id": str(uuid.uuid4()), "seat_id": ["not_a_string"]}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.post(f"{BASE_URL}/booking/lock", json=payload_wrong_type)
        assert res.status_code == 422

    # 3. Buffer exhaustion / Extremely long payload
    long_string = "A" * 10000
    payload_long = {"flight_id": long_string, "seat_id": str(uuid.uuid4())}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.post(f"{BASE_URL}/booking/lock", json=payload_long)
        assert res.status_code in (422, 400, 409) # Should be rejected gracefully without a 500

@pytest.mark.asyncio
async def test_auth_input_validation():
    """
    Test that authentication endpoints reject invalid data (e.g. SQLi, extremely long fields)
    """
    run_hex = uuid.uuid4().hex
    headers = {"X-Forwarded-For": f"10.{int(run_hex[:2], 16) % 255}.{int(run_hex[2:4], 16) % 255}.62"}
    
    malicious_email = "test@example.com' OR 1=1--"
    payload = {
        "email": malicious_email,
        "password": "pass"
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.post(f"{BASE_URL}/auth/login", json=payload)
        # Should not crash the server or return 500
        assert res.status_code in (422, 401, 400, 200)
        if res.status_code == 200:
            assert res.json()["success"] is False
            
    payload_long = {
        "email": "a" * 1000 + "@example.com",
        "password": "p" * 1000
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.post(f"{BASE_URL}/auth/login", json=payload_long)
        # Should not crash the server
        assert res.status_code in (422, 401, 400, 200)
        if res.status_code == 200:
            assert res.json()["success"] is False

