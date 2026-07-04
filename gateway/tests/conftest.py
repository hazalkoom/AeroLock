import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.booking import get_inventory_client
from app.api.search import get_search_client
from app.core.security import get_current_user

@pytest.fixture
def mock_inventory_client():
    return AsyncMock()

@pytest.fixture
def mock_search_client():
    return AsyncMock()

@pytest.fixture
def mock_user_client():
    return AsyncMock()

@pytest.fixture
def auth_client():
    """Returns a TestClient with a mocked get_current_user dependency."""
    app.dependency_overrides[get_current_user] = lambda: "test-user-id"
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_client():
    """Returns a standard TestClient with no auth mocks."""
    yield TestClient(app)
    app.dependency_overrides.clear()
