import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.api.booking import get_inventory_client

# This creates a fake browser/frontend to send requests to your FastAPI app
client = TestClient(app)

def test_acquire_lock_success():
    """
    Test that the Gateway correctly accepts a valid JSON request 
    and returns the token from the mocked gRPC client.
    """
    # 1. Create a fake gRPC client that returns a perfect response
    mock_client = AsyncMock()
    mock_client.acquire_lock.return_value = {
        "success": True,
        "token": "fake-test-token-123",
        "message": "Lock acquired successfully"
    }

    # 2. Force FastAPI to use our mock instead of the real client
    async def override_get_client():
        return mock_client

    app.dependency_overrides[get_inventory_client] = override_get_client

    # 3. Fire the request
    response = client.post(
        "/api/v1/booking/lock",
        json={"seat_id": "valid-seat-uuid"}
    )

    # 4. Assertions
    assert response.status_code == 200
    assert response.json()["token"] == "fake-test-token-123"
    
    # Clean up the override for the next test
    app.dependency_overrides.clear()

def test_acquire_lock_missing_seat_id():
    """
    Test that Pydantic blocks the request with a 422 Unprocessable Entity 
    if the frontend developer forgets to send the seat_id.
    """
    # Notice we don't even need to mock the client here, because Pydantic 
    # intercepts the bad JSON before the route logic even executes.
    response = client.post(
        "/api/v1/booking/lock",
        json={} # Empty JSON!
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "seat_id"]

def test_confirm_booking_success():
    """
    Test the full payload confirmation route.
    """
    mock_client = AsyncMock()
    mock_client.confirm_booking.return_value = {
        "success": True,
        "booking_id": "fake-booking-uuid-999",
        "message": "Booking confirmed"
    }

    async def override_get_client():
        return mock_client

    app.dependency_overrides[get_inventory_client] = override_get_client

    response = client.post(
        "/api/v1/booking/confirm",
        json={
            "seat_id": "valid-seat-uuid",
            "user_id": "user-456",
            "token": "fake-test-token-123",
            "idempotency_key": "unique-key-789"
        }
    )

    assert response.status_code == 200
    assert response.json()["booking_id"] == "fake-booking-uuid-999"
    
    app.dependency_overrides.clear()