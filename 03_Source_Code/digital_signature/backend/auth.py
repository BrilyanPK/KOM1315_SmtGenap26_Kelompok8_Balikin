from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import SessionDep, CurrentUser
from typing import Any
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate, MFALoginResponse, OTPVerifyRequest
from app.services.user_service import UserService
from app.core.rate_limit import limiter
from jose import jwt, JWTError
from app.core.config import settings
from app.models import User
from app.core.security import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserCreate, session: SessionDep):
    return UserService.register(session, user_data)


@router.post("/login", response_model=Any)
@limiter.limit("5/minute")
def login(
    request: Request,
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return UserService.login(
        session, form_data.username, form_data.password, request.client.host
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user

@router.patch("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate, 
    session: SessionDep, 
    current_user: CurrentUser
):
    return UserService.update_me(session, user_data, current_user)

from pydantic import BaseModel
class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_token(request: Request, body: RefreshTokenRequest, session: SessionDep):
    try:
        payload = jwt.decode(
            body.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    access_token = create_access_token(subject=user.id, role=user.role.value)
    return {"access_token": access_token, "refresh_token": body.refresh_token, "token_type": "bearer"}

@router.post("/verify-otp", response_model=Token)
@limiter.limit("10/minute")
def verify_otp(request: Request, body: OTPVerifyRequest, session: SessionDep):
    try:
        payload = jwt.decode(
            body.mfa_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "mfa":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
        
    return UserService.verify_otp(session, user_id, body.otp_code, request.client.host if request.client else "")

@router.post("/toggle-mfa")
def toggle_mfa(session: SessionDep, current_user: CurrentUser):
    # Only Admin and Petugas can toggle MFA
    from app.models import RoleEnum
    if current_user.role not in [RoleEnum.PETUGAS, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Not allowed to use MFA")
    return UserService.toggle_mfa(session, current_user)
