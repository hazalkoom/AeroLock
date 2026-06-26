import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.api.search import get_search_client

client = TestClient(app)

def test_search_flights_success():
    """
    Test that a valid HTTP GET request correctly calls the gRPC client
    and returns a 200 OK with the flight data.
    """
    # 1. Setup the fake gRPC client response
    mock_client = AsyncMock()
    mock_client.search_flights.return_value = [
        {
            "id": "uuid-test-123",
            "origin": "CAI",
            "destination": "DXB",
            "departure_time": "2026-12-01T10:00:00",
            "arrival_time": "2026-12-01T14:00:00",
            "price": 350.0,
            "available_seats": 150
        }
    ]

    # 2. Override the dependency
    async def override_get_client():
        return mock_client

    app.dependency_overrides[get_search_client] = override_get_client

    # 3. Fire the request
    response = client.get("/api/v1/search/?origin=CAI&destination=DXB&date=2026-12-01")

    # 4. Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["origin"] == "CAI"
    assert data[0]["price"] == 350.0
    
    # Clean up for the next test
    app.dependency_overrides.clear()

def test_search_flights_invalid_airport_code():
    """
    Test that Pydantic blocks the request with a 422 if the origin 
    or destination is not exactly 3 characters.
    """
    # Notice we don't mock the client here, because Pydantic intercepts 
    # the bad request before the route logic executes.
    
    # 'NY' is 2 characters, Pydantic demands min_length=3
    response = client.get("/api/v1/search/?origin=NY&destination=DXB&date=2026-12-01")

    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["query", "origin"]