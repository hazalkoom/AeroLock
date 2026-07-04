import os
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from aerolock_common.logging import setup_logger

logger = setup_logger("gateway-security")

security = HTTPBearer()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "certs", "public_key.pem")

# Load the public key into memory on startup
try:
    with open(PUBLIC_KEY_PATH, "r") as f:
        PUBLIC_KEY = f.read()
except FileNotFoundError:
    logger.error("Public key not found! JWT verification will fail.")
    PUBLIC_KEY = ""

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Decodes the RS256 JWT and returns the user_id. 
    If the token is invalid, it throws a 401 Unauthorized instantly.
    """
    token = credentials.credentials
    try:
        # Notice we use the PUBLIC key here, and RS256
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token attempt: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")