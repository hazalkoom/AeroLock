import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.server import UserService
from aerolock_common.generated import user_pb2
import grpc

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = "user-123"
    user.email = "test@test.com"
    user.first_name = "John"
    user.last_name = "Doe"
    user.role = "user"
    user.password_hash = "$2b$hashed_pass"
    return user

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
@patch("app.server.create_access_token")
async def test_register_user_success(mock_token, MockRepo, MockSession, user_service, mock_context, fake_user):
    mock_token.return_value = "fake_jwt_token"
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.create_user = AsyncMock(return_value=(True, fake_user))

    request = MagicMock(email="test@test.com", password="pass", first_name="John", last_name="Doe")
    
    response = await user_service.RegisterUser(request, mock_context)
    
    assert response.success is True
    assert response.access_token == "fake_jwt_token"
    assert response.user_id == "user-123"

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
async def test_register_user_duplicate(MockRepo, MockSession, user_service, mock_context):
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.create_user = AsyncMock(return_value=(False, "Email already registered."))

    request = MagicMock(email="test@test.com", password="pass", first_name="John", last_name="Doe")
    
    response = await user_service.RegisterUser(request, mock_context)
    
    assert response.success is False
    assert response.access_token == ""
    assert "already registered" in response.message

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
@patch("app.server.verify_password")
@patch("app.server.create_access_token")
async def test_login_success(mock_token, mock_verify, MockRepo, MockSession, user_service, mock_context, fake_user):
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.get_user_by_email = AsyncMock(return_value=fake_user)
    mock_verify.return_value = True
    mock_token.return_value = "fake_jwt_token"

    request = MagicMock(email="test@test.com", password="correct_pass")
    
    response = await user_service.LoginUser(request, mock_context)
    
    assert response.success is True
    assert response.access_token == "fake_jwt_token"
    assert response.user_id == "user-123"

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
@patch("app.server.verify_password")
async def test_login_wrong_password(mock_verify, MockRepo, MockSession, user_service, mock_context, fake_user):
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.get_user_by_email = AsyncMock(return_value=fake_user)
    mock_verify.return_value = False

    request = MagicMock(email="test@test.com", password="wrong_pass")
    
    response = await user_service.LoginUser(request, mock_context)
    
    assert response.success is False
    assert response.access_token == ""
    assert "Invalid email or password" in response.message

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
async def test_login_user_not_found(MockRepo, MockSession, user_service, mock_context):
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.get_user_by_email = AsyncMock(return_value=None)

    request = MagicMock(email="fake@test.com", password="pass")
    
    response = await user_service.LoginUser(request, mock_context)
    
    assert response.success is False
    assert response.access_token == ""

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
async def test_get_profile_success(MockRepo, MockSession, user_service, mock_context, fake_user):
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.get_user_by_id = AsyncMock(return_value=fake_user)

    request = MagicMock(user_id="user-123")
    
    response = await user_service.GetProfile(request, mock_context)
    
    assert response.id == "user-123"
    assert response.email == "test@test.com"
    assert response.first_name == "John"

@pytest.mark.asyncio
@patch("app.server.AsyncSessionLocal")
@patch("app.server.UserRepository")
async def test_get_profile_not_found(MockRepo, MockSession, user_service, mock_context):
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.get_user_by_id = AsyncMock(return_value=None)

    request = MagicMock(user_id="fake-id")
    
    response = await user_service.GetProfile(request, mock_context)
    
    mock_context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)
    mock_context.set_details.assert_called_once_with("User not found")
