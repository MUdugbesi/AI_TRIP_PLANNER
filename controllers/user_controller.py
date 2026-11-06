import uuid

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schema.user import TokenResponse, UserRegisterRequest, UserResponse, UserLoginRequest
from model.user_model import User

from services.auth_services import get_password_hash, create_access_token, login_user_service

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])
@router.post("/register", response_model=TokenResponse,
             status_code=status.HTTP_201_CREATED)
def register_user(payload:UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    new_user_id = str(uuid.uuid4())
    hashed_pwd = get_password_hash(payload.password)

    new_user = User(
        id=new_user_id,
        email=payload.email,
        hashed_password=hashed_pwd,
        first_name=payload.first_name,
        last_name=payload.last_name,
        passport_nationality=payload.passport_nationality, # type: ignore
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(new_user_id, payload.email)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            passport_nationality=new_user.passport_nationality,
            created_at=new_user.created_at,
            is_active=new_user.is_active
        )
    )

@router.post("/login", response_model=TokenResponse)
def login_user(payload:UserLoginRequest, db: Session = Depends(get_db)):
    return login_user_service(payload, db)
