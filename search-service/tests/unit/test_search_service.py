import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.server import SearchServiceServicer
from aerolock_common.generated import search_pb2

@pytest.fixture
def mock_request():
    return search_pb2.SearchRequest(
        origin="CAI",
        destination="DXB",
        date="2026-12-01"
    )

@pytest.fixture
def mock_context():
    return AsyncMock()

@pytest.mark.asyncio
@patch("app.server.CacheManager")
async def test_search_flights_cache_hit(MockCacheManager, mock_request, mock_context):
    """
    Test that if data is in Redis, the database is completely bypassed.
    """
    # Setup Cache to return a HIT
    mock_cache_instance = MockCacheManager.return_value
    mock_cache_instance.get_cached_search = AsyncMock(return_value=[
        {
            "flight_id": "uuid-123", 
            "origin": "CAI", 
            "destination": "DXB", 
            "departure_time": "2026-12-01T10:00:00", 
            "arrival_time": "2026-12-01T14:00:00", 
            "price": 350.0, 
            "available_seats": 150
        }
    ])

    servicer = SearchServiceServicer()
    
    # We patch AsyncSessionLocal to prove it NEVER gets called
    with patch("app.server.AsyncSessionLocal") as MockSession:
        response = await servicer.SearchFlights(mock_request, mock_context)
        
        # Assertions
        assert len(response.flights) == 1
        assert response.flights[0].id == "uuid-123"
        MockSession.assert_not_called() # CRITICAL: DB was bypassed!

@pytest.mark.asyncio
@patch("app.server.CacheManager")
@patch("app.server.SearchRepository")
@patch("app.server.AsyncSessionLocal")
async def test_search_flights_cache_miss(MockSession, MockRepo, MockCacheManager, mock_request, mock_context):
    """
    Test that if data is missing in Redis, it queries the DB and saves it to Redis.
    """
    # Setup Cache to return a MISS
    mock_cache_instance = MockCacheManager.return_value
    mock_cache_instance.get_cached_search = AsyncMock(return_value=None)
    mock_cache_instance.set_cached_search = AsyncMock()

    # Setup Repo to return database rows
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.search_flights = AsyncMock(return_value=[
        {
            "flight_id": "uuid-999", 
            "origin": "CAI", 
            "destination": "DXB", 
            "departure_time": "2026-12-01T10:00:00", 
            "arrival_time": "2026-12-01T14:00:00", 
            "price": 500.0, 
            "available_seats": 10
        }
    ])

    servicer = SearchServiceServicer()
    response = await servicer.SearchFlights(mock_request, mock_context)

    # Assertions
    assert len(response.flights) == 1
    assert response.flights[0].id == "uuid-999"
    
    # Prove the DB was called
    mock_repo_instance.search_flights.assert_called_once_with("CAI", "DXB", "2026-12-01")
    
    # Prove the result was saved back to Redis for the next user
    mock_cache_instance.set_cached_search.assert_called_once()