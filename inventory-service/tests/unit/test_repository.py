import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from app.db.repository import InventoryRepository

@pytest.mark.asyncio
async def test_create_booking_success():
    """
    Test that a brand new booking is successfully committed to the database.
    """
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    
    repo = InventoryRepository(mock_session)

    success, booking_id = await repo.create_booking(
        seat_id="fake-seat-123", 
        user_id="user-456", 
        idempotency_key="new-key-789"
    )

    assert success is True
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_booking_duplicate_idempotency():
    """
    Test the Bouncer: If Postgres throws an IntegrityError, rollback and return False.
    """
    mock_session = MagicMock()
    mock_session.commit = AsyncMock(side_effect=IntegrityError(
        "duplicate key value violates unique constraint", params={}, orig=BaseException()
    ))
    mock_session.rollback = AsyncMock()

    repo = InventoryRepository(mock_session)

    success, booking_id = await repo.create_booking(
        seat_id="fake-seat-123", 
        user_id="user-456", 
        idempotency_key="used-key-789"
    )

    assert success is False
    assert booking_id is None
    mock_session.rollback.assert_awaited_once()