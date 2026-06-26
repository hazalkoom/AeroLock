import pytest
from unittest.mock import AsyncMock, patch
from aerolock_common.generated import inventory_pb2
from app.services.inventory_service import InventoryService

@pytest.mark.asyncio
@patch("app.services.inventory_service.RedisLockManager")
@patch("app.services.inventory_service.InventoryRepository")
@patch("app.services.inventory_service.Async_session_local")
async def test_confirm_booking_idempotency_rejection(mock_session_maker, mock_repo_class, mock_lock_class):
    """
    Test that the gRPC service correctly handles a duplicate idempotency key rejection from the Repo.
    """
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b"valid-token"

    mock_lock_instance = mock_lock_class.return_value
    mock_lock_instance.release_lock = AsyncMock()

    mock_session = AsyncMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    mock_repo_instance = mock_repo_class.return_value
    
    mock_repo_instance.create_booking = AsyncMock(return_value=(False, None))

    service = InventoryService(mock_redis)
    request = inventory_pb2.ConfirmBookingRequest(
        seat_id="seat-123",
        user_id="user-456",
        idempotency_key="already-used-key",
        token="valid-token"
    )
    context = AsyncMock()

    response = await service.ConfirmBooking(request, context)

    assert response.success is False
    assert response.message == "Transaction rejected by the bouncer (Duplicate Idempotency Key)."
    mock_lock_instance.release_lock.assert_not_called()