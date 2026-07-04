import pytest
import httpx

from .conftest import BASE_URL

@pytest.mark.asyncio
async def test_auth_full_flow():
    # 1. Register a new user
    import uuid
    email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    register_payload = {
        "email": email,
        "password": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    async with httpx.AsyncClient() as client:
        reg_response = await client.post(f"{BASE_URL}/auth/register", json=register_payload)
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        reg_data = reg_response.json()
        assert "access_token" in reg_data
        
        # 2. Login
        login_payload = {
            "email": email,
            "password": "StrongPassword123!"
        }
        login_response = await client.post(f"{BASE_URL}/auth/login", json=login_payload)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        token = login_data["access_token"]
        assert token
        
        # 3. Access a protected endpoint (e.g., getting a lock requires JWT? No, lock is public. Confirm requires JWT)
        # Actually, let's just make sure the token is structurally a JWT
        parts = token.split(".")
        assert len(parts) == 3

@pytest.mark.asyncio
async def test_auth_login_invalid_credentials():
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrong_password"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/login", json=login_payload)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid" in data["detail"] or "failed" in data["detail"].lower()

@pytest.mark.asyncio
async def test_auth_register_duplicate():
    import uuid
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    async with httpx.AsyncClient() as client:
        # First registration
        r1 = await client.post(f"{BASE_URL}/auth/register", json=payload)
        assert r1.status_code == 200
        
        # Second registration
        r2 = await client.post(f"{BASE_URL}/auth/register", json=payload)
        assert r2.status_code == 400
        data = r2.json()
        assert "registered" in data["detail"].lower()
