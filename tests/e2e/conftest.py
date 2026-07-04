import pytest
import httpx
import uuid
import asyncpg
import asyncio

BASE_URL = "http://localhost:8000/api/v1"
DB_URL = "postgresql://aerolock_user:password123@localhost:5432/aerolock"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def get_fresh_seat():
    """Returns a flight_id and seat_id for an available seat."""
    conn = await asyncpg.connect(DB_URL)
    query = """
        SELECT s.flight_id, s.id 
        FROM seats s 
        LEFT JOIN bookings b ON s.id = b.seat_id 
        WHERE s.status = 'available' AND b.id IS NULL 
        LIMIT 1
    """
    row = await conn.fetchrow(query)
    await conn.close()
    if not row:
        pytest.skip("No truly available seats left in the database.")
    return str(row['flight_id']), str(row['id'])

@pytest.fixture
async def auth_headers():
    """Registers a new user and returns the Authorization header."""
    async with httpx.AsyncClient() as client:
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "Password123!"
        
        payload = {
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "User"
        }
        
        res = await client.post(f"{BASE_URL}/auth/register", json=payload)
        assert res.status_code == 200, f"Failed to register test user: {res.text}"
        
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def register_new_user():
    """Returns a function to register multiple users if needed."""
    async def _register():
        async with httpx.AsyncClient() as client:
            email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            payload = {
                "email": email,
                "password": "Password123!",
                "first_name": "Test",
                "last_name": "User"
            }
            res = await client.post(f"{BASE_URL}/auth/register", json=payload)
            token = res.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
    return _register
