from fastapi.testclient import TestClient
from app.main import app

# Create the test client
client = TestClient(app)

def test_health_check_rate_limit():
    """
    Test that the rate limiter successfully blocks IPs that exceed the threshold.
    The /health endpoint allows exactly 5 requests per minute.
    """
    # 1. Fire 5 successful requests
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    # 2. Fire the 6th request (The spammer)
    response = client.get("/health")
    
    # 3. Assert the bouncer kicks them out
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text