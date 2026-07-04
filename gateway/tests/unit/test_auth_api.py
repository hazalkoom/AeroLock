import pytest
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_user_client

@pytest.fixture
def mock_user_client():
    client = AsyncMock()
    return client

@pytest.fixture
def auth_test_client(mock_user_client):
    app.dependency_overrides[get_user_client] = lambda: mock_user_client
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_user_client, None)

def test_register_user_success(auth_test_client, mock_user_client):
    mock_user_client.register.return_value = {
        "success": True,
        "access_token": "fake_token",
        "message": "User registered successfully",
        "user_id": "123"
    }

    response = auth_test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "password": "StrongPassword123!",
            "first_name": "John",
            "last_name": "Doe"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["access_token"] == "fake_token"
    mock_user_client.register.assert_called_once_with(
        email="test@test.com",
        password="StrongPassword123!",
        first_name="John",
        last_name="Doe"
    )

def test_register_user_invalid_payload(auth_test_client, mock_user_client):
    response = auth_test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "pass", # too short or missing fields
        }
    )
    
    assert response.status_code == 422 # Pydantic validation error

def test_login_user_success(auth_test_client, mock_user_client):
    mock_user_client.login.return_value = {
        "success": True,
        "access_token": "fake_token",
        "message": "Login successful",
        "user_id": "123"
    }

    response = auth_test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@test.com",
            "password": "StrongPassword123!"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["access_token"] == "fake_token"
    mock_user_client.login.assert_called_once_with(
        email="test@test.com",
        password="StrongPassword123!"
    )
