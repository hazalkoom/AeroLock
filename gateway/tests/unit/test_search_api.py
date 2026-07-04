import pytest
from app.main import app
from app.api.search import get_search_client
import grpc

def test_search_flights_success(test_client, mock_search_client):
    mock_search_client.search_flights.return_value = [
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

    async def override_get_client():
        return mock_search_client

    app.dependency_overrides[get_search_client] = override_get_client

    response = test_client.get("/api/v1/search/?origin=CAI&destination=DXB&date=2026-12-01")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["origin"] == "CAI"
    assert data[0]["price"] == 350.0

def test_search_flights_invalid_airport_code(test_client):
    response = test_client.get("/api/v1/search/?origin=NY&destination=DXB&date=2026-12-01")
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["query", "origin"]

def test_search_empty_results(test_client, mock_search_client):
    mock_search_client.search_flights.return_value = []

    async def override_get_client():
        return mock_search_client

    app.dependency_overrides[get_search_client] = override_get_client

    response = test_client.get("/api/v1/search/?origin=CAI&destination=DXB&date=2026-12-01")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_search_grpc_unavailable(test_client, mock_search_client):
    from fastapi import HTTPException
    mock_search_client.search_flights.side_effect = HTTPException(status_code=500, detail="gRPC Error")

    async def override_get_client():
        return mock_search_client

    app.dependency_overrides[get_search_client] = override_get_client

    response = test_client.get("/api/v1/search/?origin=CAI&destination=DXB&date=2026-12-01")
    
    assert response.status_code == 500