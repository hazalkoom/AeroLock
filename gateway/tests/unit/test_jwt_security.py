import pytest
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import patch, MagicMock
from app.core.security import get_current_user

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
async def test_get_current_user_success(mock_jwt_decode):
    mock_jwt_decode.return_value = {"sub": "user-123", "role": "user"}
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
    
    user_id = await get_current_user(credentials=creds)
    
    assert user_id == "user-123"
    mock_jwt_decode.assert_called_once()

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
async def test_get_current_user_expired_token(mock_jwt_decode):
    mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Expired")
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired_token")
    
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=creds)
        
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
async def test_get_current_user_invalid_token(mock_jwt_decode):
    mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid")
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
    
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=creds)
        
    assert exc.value.status_code == 401
    assert "invalid" in exc.value.detail.lower()

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
async def test_get_current_user_missing_sub(mock_jwt_decode):
    mock_jwt_decode.return_value = {"role": "user"} # Missing 'sub'
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token_without_sub")
    
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=creds)
        
    assert exc.value.status_code == 401
    assert "invalid token payload" in exc.value.detail.lower()
