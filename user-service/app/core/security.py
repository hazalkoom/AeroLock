import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# Token validity: 24 hours
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Decode back to string so PostgreSQL can store it in the VARCHAR column
    return hashed.decode('utf-8')

def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "role": role, "exp": expire}
    
    # RS256 Magic
    encoded_jwt = jwt.encode(to_encode, settings.private_key, algorithm="RS256")
    return encoded_jwt