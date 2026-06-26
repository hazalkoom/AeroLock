import pytest
import json
from unittest.mock import patch, AsyncMock
from app.cache import CacheManager

# We patch the Redis connection so it doesn't try to connect to localhost:6379 during tests
@patch("app.cache.Redis.from_url")
def test_cache_hit(mock_redis_url):
    # Setup the mock Redis instance
    mock_redis_instance = AsyncMock()
    mock_redis_url.return_value = mock_redis_instance
    
    # Fake data that Redis will return
    fake_flight_data = [{"flight_id": "123", "origin": "CAI", "destination": "DXB"}]
    mock_redis_instance.get.return_value = json.dumps(fake_flight_data)

    manager = CacheManager()
    
    # Execute
    result = pytest.helpers_namespace = manager.get_cached_search("CAI", "DXB", "2026-12-01")
    
    import asyncio
    result = asyncio.run(manager.get_cached_search("CAI", "DXB", "2026-12-01"))

    # Assertions
    assert result == fake_flight_data
    mock_redis_instance.get.assert_called_once()

@patch("app.cache.Redis.from_url")
async def test_cache_miss(mock_redis_url):
    mock_redis_instance = AsyncMock()
    mock_redis_url.return_value = mock_redis_instance
    
    # Simulate Redis returning None (Cache Miss)
    mock_redis_instance.get.return_value = None

    manager = CacheManager()
    result = await manager.get_cached_search("CAI", "DXB", "2026-12-01")

    assert result is None

@patch("app.cache.Redis.from_url")
async def test_set_cache(mock_redis_url):
    mock_redis_instance = AsyncMock()
    mock_redis_url.return_value = mock_redis_instance

    manager = CacheManager()
    fake_flight_data = [{"flight_id": "123", "origin": "CAI", "destination": "DXB"}]
    
    await manager.set_cached_search("CAI", "DXB", "2026-12-01", fake_flight_data)

    # Verify that the Redis SET command was actually fired with the correct parameters
    mock_redis_instance.set.assert_called_once()