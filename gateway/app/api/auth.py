from fastapi import APIRouter, Depends
from app.clients.user_client import UserClient
from app.schemas.auth import LoginPayload, RegisterPayload

router = APIRouter()

async def get_user_client() -> UserClient:
    return UserClient()

@router.post("/register", summary="Register a new user")
async def register_user(payload: RegisterPayload, client: UserClient = Depends(get_user_client)):
    return await client.register(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name
    )

@router.post("/login", summary="Login and get RS256 JWT")
async def login_user(payload: LoginPayload, client: UserClient = Depends(get_user_client)):
    return await client.login(email=payload.email, password=payload.password)