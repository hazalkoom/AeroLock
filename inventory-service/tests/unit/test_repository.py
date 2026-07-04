import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from app.db.repository import InventoryRepository
from app.db.models import Seat

@pytest.mark.asyncio
async def test_create_booking_success():
    mock_session = AsyncMock()
    
    mock_seat = Seat(status="available")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_seat
    mock_session.execute.return_value = mock_result
    
    repo = InventoryRepository(mock_session)

    success, booking_id = await repo.create_booking(
        seat_id="fake-seat-123", 
        user_id="user-456", 
        idempotency_key="new-key-789"
    )

    assert success is True
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_booking_duplicate_idempotency():
    mock_session = AsyncMock()
    
    mock_seat = Seat(status="available")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_seat
    mock_session.execute.return_value = mock_result
    
    mock_session.commit.side_effect = IntegrityError(
        "dup", params={}, orig=BaseException()
    )

    repo = InventoryRepository(mock_session)

    success, message = await repo.create_booking(
        seat_id="fake-seat-123", 
        user_id="user-456", 
        idempotency_key="used-key-789"
    )

    assert success is False
    mock_session.rollback.assert_awaited_once()
    assert "Duplicate" in message

@pytest.mark.asyncio
async def test_create_booking_seat_not_available():
    mock_session = AsyncMock()
    mock_seat = Seat(status="booked")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_seat
    mock_session.execute.return_value = mock_result
    
    repo = InventoryRepository(mock_session)
    success, message = await repo.create_booking(
        seat_id="fake-seat", user_id="user", idempotency_key="key"
    )
    
    assert success is False
    assert "Seat is not available" in message
    
@pytest.mark.asyncio
async def test_create_booking_seat_not_found():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    repo = InventoryRepository(mock_session)
    success, message = await repo.create_booking(
        seat_id="fake-seat", user_id="user", idempotency_key="key"
    )
    
    assert success is False
    assert "Seat is not available" in message