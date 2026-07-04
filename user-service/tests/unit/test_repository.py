import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from app.db.repository import UserRepository
from app.db.models import User

@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session

@pytest.fixture
def repo(mock_session):
    return UserRepository(mock_session)

@pytest.mark.asyncio
async def test_get_user_by_email_found(repo, mock_session):
    mock_result = MagicMock()
    fake_user = User(id="user-123", email="test@test.com")
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute.return_value = mock_result

    user = await repo.get_user_by_email("test@test.com")
    
    assert user == fake_user
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    user = await repo.get_user_by_email("nonexistent@test.com")
    
    assert user is None

@pytest.mark.asyncio
async def test_get_user_by_id_found(repo, mock_session):
    mock_result = MagicMock()
    fake_user = User(id="user-123", email="test@test.com")
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute.return_value = mock_result

    user = await repo.get_user_by_id("user-123")
    
    assert user == fake_user

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    user = await repo.get_user_by_id("fake-id")
    
    assert user is None

@pytest.mark.asyncio
@patch("app.db.repository.get_password_hash")
async def test_create_user_success(mock_hash, repo, mock_session):
    mock_hash.return_value = "$2b$hashed_pass"
    
    # We don't need execute to return anything special for create_user
    # but we need commit and refresh to work
    success, result = await repo.create_user("test@test.com", "pass123", "John", "Doe")
    
    assert success is True
    assert isinstance(result, User)
    assert result.email == "test@test.com"
    assert result.password_hash == "$2b$hashed_pass"
    
    mock_hash.assert_called_once_with("pass123")
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_create_user_duplicate_email(repo, mock_session):
    mock_session.commit.side_effect = IntegrityError(None, None, Exception("Duplicate"))
    
    success, result = await repo.create_user("test@test.com", "pass123", "John", "Doe")
    
    assert success is False
    assert "already registered" in result
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_db_error(repo, mock_session):
    mock_session.commit.side_effect = Exception("DB Down")
    
    success, result = await repo.create_user("test@test.com", "pass123", "John", "Doe")
    
    assert success is False
    assert "Internal database error" in result
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
@patch("app.db.repository.get_password_hash")
async def test_password_is_hashed_before_storage(mock_hash, repo, mock_session):
    mock_hash.return_value = "$2b$fakehash"
    
    await repo.create_user("test@test.com", "plain_text_pass", "John", "Doe")
    
    # Verify the plain text password was never stored
    added_user = mock_session.add.call_args[0][0]
    assert added_user.password_hash == "$2b$fakehash"
    assert added_user.password_hash != "plain_text_pass"
