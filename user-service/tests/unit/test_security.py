import pytest
import jwt
from datetime import datetime, timezone
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

def test_hash_password_returns_bcrypt_format():
    hashed = get_password_hash("my_secret_password")
    assert hashed.startswith("$2b$")

def test_hash_password_unique_salts():
    hash1 = get_password_hash("password")
    hash2 = get_password_hash("password")
    assert hash1 != hash2

def test_verify_password_correct():
    hashed = get_password_hash("correct_password")
    assert verify_password("correct_password", hashed) is True

def test_verify_password_incorrect():
    hashed = get_password_hash("correct_password")
    assert verify_password("wrong_password", hashed) is False

def test_verify_password_empty():
    hashed = get_password_hash("correct_password")
    assert verify_password("", hashed) is False

def test_create_access_token_decodable():
    token = create_access_token("user-123", "admin")
    
    # decode the token without verifying signature (since we only have private key loaded here)
    payload = jwt.decode(token, options={"verify_signature": False})
    
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"

def test_create_access_token_contains_claims():
    token = create_access_token("user-123", "user")
    payload = jwt.decode(token, options={"verify_signature": False})
    
    assert "sub" in payload
    assert "role" in payload
    assert "exp" in payload

def test_create_access_token_expiry():
    token = create_access_token("user-123", "user")
    payload = jwt.decode(token, options={"verify_signature": False})
    
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    diff = exp_time - now
    # Check that expiry is about 24 hours (1440 mins = 86400 seconds) from now
    assert 86000 < diff.total_seconds() <= 86400
