from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# USER DTOs MODEL

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    passport_nationality: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    passport_nationality: Optional[str] = None
    created_at: datetime
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
