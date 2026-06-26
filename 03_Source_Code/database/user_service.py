from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User, RoleEnum
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, create_mfa_token
from app.services.activity_log_service import ActivityLogService
from app.services.email_service import EmailService
import secrets
from datetime import datetime, timedelta


class UserService:
    @staticmethod
    def register(db: Session, user_data: UserCreate) -> User:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        if user_data.role != RoleEnum.PENCARI:
            raise HTTPException(status_code=403, detail="Can only register as Pencari")

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        ActivityLogService.log(db, new_user.id, "REGISTER_USER", f"User {new_user.email} registered")
        return new_user

    @staticmethod
    def login(db: Session, email: str, password: str, request_host: str) -> dict:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            ActivityLogService.log(
                db, user.id if user else None, "LOGIN", f"Gagal masuk sistem untuk {email}", ip_address=request_host, status="Peringatan"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.mfa_enabled and user.role in [RoleEnum.PETUGAS, RoleEnum.ADMIN]:
            # Generate 6 digit OTP
            otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
            user.otp_code = get_password_hash(otp)
            user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
            db.commit()
            
            # Send email
            EmailService.send_otp_email(user.email, otp)
            
            mfa_token = create_mfa_token(subject=user.id)
            ActivityLogService.log(db, user.id, "LOGIN_MFA_STARTED", f"OTP dikirim ke {user.email}", ip_address=request_host, status="Berhasil")
            return {"requires_mfa": True, "mfa_token": mfa_token}

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

        ActivityLogService.log(db, user.id, "LOGIN", f"Berhasil masuk sistem", ip_address=request_host, status="Berhasil")
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    @staticmethod
    def get_all(db: Session) -> list:
        return db.query(User).all()

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def update_me(db: Session, user_data: UserUpdate, current_user: User) -> User:
        if user_data.email and user_data.email != current_user.email:
            existing = db.query(User).filter(User.email == user_data.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already taken")
            current_user.email = user_data.email
            
        if user_data.full_name:
            current_user.full_name = user_data.full_name

        db.commit()
        db.refresh(current_user)

        ActivityLogService.log(db, current_user.id, "UPDATE_PROFILE", f"User updated their profile")
        return current_user

    @staticmethod
    def create_by_admin(db: Session, user_data: UserCreate, admin_user: User) -> User:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        ActivityLogService.log(db, admin_user.id, "CREATE_USER", f"Admin created user {new_user.email} with role {new_user.role}")
        return new_user

    @staticmethod
    def update_by_admin(db: Session, user_id: str, user_data: UserUpdate, admin_user: User) -> User:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_data.full_name:
            db_user.full_name = user_data.full_name
        if user_data.email:
            db_user.email = user_data.email
        if user_data.role:
            db_user.role = user_data.role

        db.commit()
        db.refresh(db_user)

        ActivityLogService.log(db, admin_user.id, "UPDATE_USER", f"Admin updated user {db_user.email}")
        return db_user

    @staticmethod
    def delete_by_admin(db: Session, user_id: str, admin_user: User) -> dict:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        email = db_user.email
        db.delete(db_user)
        db.commit()

        ActivityLogService.log(db, admin_user.id, "DELETE_USER", f"Admin deleted user {email}")
        return {"detail": "User deleted"}

    @staticmethod
    def verify_otp(db: Session, user_id: str, otp_code: str, request_host: str) -> dict:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not user.otp_code or not user.otp_expires_at:
            raise HTTPException(status_code=400, detail="MFA not initiated")
            
        if datetime.utcnow() > user.otp_expires_at:
            raise HTTPException(status_code=400, detail="OTP has expired")
            
        if not verify_password(otp_code, user.otp_code):
            ActivityLogService.log(db, user.id, "LOGIN_MFA_FAILED", f"Gagal verifikasi OTP", ip_address=request_host, status="Peringatan")
            raise HTTPException(status_code=400, detail="Invalid OTP code")
            
        # Clear OTP
        user.otp_code = None
        user.otp_expires_at = None
        db.commit()
        
        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

        ActivityLogService.log(db, user.id, "LOGIN", f"Berhasil masuk sistem (MFA)", ip_address=request_host, status="Berhasil")
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    @staticmethod
    def toggle_mfa(db: Session, user: User) -> dict:
        user.mfa_enabled = not user.mfa_enabled
        db.commit()
        ActivityLogService.log(db, user.id, "TOGGLE_MFA", f"MFA disetel ke {user.mfa_enabled}")
        return {"mfa_enabled": user.mfa_enabled}
