from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str  # No default — app will crash if not set
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2 hours (was 1440/24h)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET: str = "uploads"

    # Encryption key for sensitive data (Fernet)
    ENCRYPTION_KEY: str = ""

    # Frontend URL for CORS
    FRONTEND_URL: str = "https://balikin-ads2026-kelompok11.vercel.app"

    # SMTP configuration for MFA email OTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
