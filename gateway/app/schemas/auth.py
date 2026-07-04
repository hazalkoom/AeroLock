from pydantic import BaseModel, EmailStr

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class LoginPayload(BaseModel):
    email: EmailStr
    password: str