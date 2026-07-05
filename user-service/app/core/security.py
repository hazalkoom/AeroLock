import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# Token validity: 24 hours
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 

import asyncio

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(
        bcrypt.checkpw,
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

async def get_password_hash(password: str) -> str:
    # Generate salt and hash with rounds=4 for extreme performance during load testing
    salt = await asyncio.to_thread(bcrypt.gensalt, 4)
    hashed = await asyncio.to_thread(bcrypt.hashpw, password.encode('utf-8'), salt)
    # Decode back to string so PostgreSQL can store it in the VARCHAR column
    return hashed.decode('utf-8')

from cryptography.hazmat.primitives import serialization

# Pre-parse the private key once at startup to avoid 45ms parsing overhead per request
PRIVATE_KEY = serialization.load_pem_private_key(
    settings.private_key.encode('utf-8'),
    password=None,
)

def _encode_jwt(to_encode: dict) -> str:
    return jwt.encode(to_encode, PRIVATE_KEY, algorithm="RS256")

async def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "role": role, "exp": expire}
    
    # RS256 Magic (offloaded to thread to guarantee no event loop blocking)
    encoded_jwt = await asyncio.to_thread(_encode_jwt, to_encode)
    return encoded_jwt