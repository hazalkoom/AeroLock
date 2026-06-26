from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

# We track users by their IP address
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app: FastAPI):
    """
    Attaches the slowapi limiter to the FastAPI application
    and registers the standard 429 Too Many Requests error handler.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)