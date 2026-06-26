import pytest
from unittest.mock import AsyncMock
from app.lock.redis_lock import RedisLockManager

@pytest.mark.asyncio
async def test_acquire_lock_success():
    """
    Test that the Lock Manager correctly returns a token when Redis successfully sets the key.
    """

    mock_redis = AsyncMock()
    mock_redis.set.return_value = True

    manager = RedisLockManager(mock_redis)
    seat_id = "fake-seat-123"

    success, token = await manager.acquire_lock(seat_id)

    assert success is True
    assert token != ""
    assert isinstance(token, str)

    mock_redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_acquire_lock_failure():
    """
    Test that the Lock Manager fails gracefully if Redis says the seat is already locked.
    """

    mock_redis = AsyncMock()
    mock_redis.set.return_value = False

    manager = RedisLockManager(mock_redis)
    seat_id = "fake-seat-123"

    success, token = await manager.acquire_lock(seat_id)

    assert success is False
    assert token == ""
    mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_release_lock_success():
    """
    Test the Lua script execution logic.
    """
    mock_redis = AsyncMock()
    # The Lua script returns 1 if it successfully deleted the key
    mock_redis.eval.return_value = 1

    manager = RedisLockManager(mock_redis)
    
    released = await manager.release_lock("fake-seat", "fake-token")
    
    assert released is True
    mock_redis.eval.assert_called_once()
