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
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1000, 9999)}"}
    
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
    headers = {"X-Forwarded-For": f"203.0.113.{random.randint(1000, 9999)}"}
    
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
