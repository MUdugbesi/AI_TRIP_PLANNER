import os
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status

import jwt
from pwdlib import PasswordHash
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from schema.user import UserResponse, UserLoginRequest, TokenResponse
from model.user_model import User


from dotenv import load_dotenv


load_dotenv()

# JWT secrets and algorithm
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# password hashing
pwd_hash = PasswordHash.recommended()
security_bearer = HTTPBearer()

# mock user data

def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
        db: Session = Depends(get_db)
) -> UserResponse:
    """
    Validates the JWT access token and queries the real SQL database
    to retrieve the active user profile.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Query the real SQL database instead of fake_users_db
        user_db = db.query(User).filter(User.id == user_id).first()
        if user_db is None or not user_db.is_active:
            raise credentials_exception

        return UserResponse(
            id=user_db.id, # type: ignore
            email=user_db.email, # type: ignore
            first_name=user_db.first_name, # type: ignore
            last_name=user_db.last_name, # type: ignore
            passport_nationality=user_db.passport_nationality, # type: ignore
            created_at=user_db.created_at, # type: ignore
            is_active=user_db.is_active # type: ignore
        )
    except jwt.PyJWTError:
        raise credentials_exception

def login_user_service(payload: UserLoginRequest, db:Session) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    access_token = create_access_token(user_id=user.id, email=user.email)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            passport_nationality=user.passport_nationality,
            created_at=user.created_at,
            is_active=user.is_active
        )
    )