import pytest
from app.main import app
from app.api.booking import get_inventory_client
import grpc

def test_acquire_lock_success(test_client, mock_inventory_client):
    mock_inventory_client.acquire_lock.return_value = {
        "success": True,
        "token": "fake-test-token-123",
        "message": "Lock acquired successfully"
    }

    async def override_get_client():
        return mock_inventory_client

    app.dependency_overrides[get_inventory_client] = override_get_client

    response = test_client.post(
        "/api/v1/booking/lock",
        json={"flight_id": "valid-flight-uuid", "seat_id": "valid-seat-uuid"}
    )

    assert response.status_code == 200
    assert response.json()["token"] == "fake-test-token-123"

def test_acquire_lock_missing_seat_id(test_client):
    response = test_client.post(
        "/api/v1/booking/lock",
        json={"flight_id": "valid-flight-uuid"}
    )
    assert response.status_code == 422

def test_acquire_lock_missing_flight_id(test_client):
    response = test_client.post(
        "/api/v1/booking/lock",
        json={"seat_id": "valid-seat-uuid"}
    )
    assert response.status_code == 422

def test_acquire_lock_grpc_error(test_client, mock_inventory_client):
    from fastapi import HTTPException
    mock_inventory_client.acquire_lock.side_effect = HTTPException(status_code=500, detail="gRPC Error: ...")

    async def override_get_client():
        return mock_inventory_client

    app.dependency_overrides[get_inventory_client] = override_get_client

    response = test_client.post(
        "/api/v1/booking/lock",
        json={"flight_id": "valid-flight-uuid", "seat_id": "valid-seat-uuid"}
    )

    # Fast API handles uncaught exceptions as 500, or the gateway client raises HTTPException
    # Let's assume gateway client raises HTTPException(500) if AioRpcError, but we mocked it directly.
    # Actually wait, our app.api.booking calls client.acquire_lock. If we mock the client, it just raises it.
    assert response.status_code == 500

def test_acquire_lock_conflict(test_client, mock_inventory_client):
    from fastapi import HTTPException
    mock_inventory_client.acquire_lock.side_effect = HTTPException(status_code=409, detail="Seat already locked")

    async def override_get_client():
        return mock_inventory_client

    app.dependency_overrides[get_inventory_client] = override_get_client

    response = test_client.post(
        "/api/v1/booking/lock",
        json={"flight_id": "valid-flight-uuid", "seat_id": "valid-seat-uuid"}
    )

    # The client raises HTTPException(409) which FastAPI translates to 409
    assert response.status_code == 409
    assert response.json()["detail"] == "Seat already locked"

def test_confirm_booking_success(auth_client, mock_inventory_client):
    mock_inventory_client.confirm_booking.return_value = {
        "success": True,
        "booking_id": "fake-booking-uuid-999",
        "message": "Booking confirmed"
    }

    async def override_get_client():
        return mock_inventory_client

    app.dependency_overrides[get_inventory_client] = override_get_client

    response = auth_client.post(
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

def test_confirm_booking_missing_auth(test_client):
    # test_client doesn't have get_current_user overridden, so it will hit the real HTTPBearer
    response = test_client.post(
        "/api/v1/booking/confirm",
        json={
            "seat_id": "valid-seat-uuid",
            "user_id": "user-456",
            "token": "fake-test-token-123",
            "idempotency_key": "unique-key-789"
        }
    )

    assert response.status_code in [401, 403]