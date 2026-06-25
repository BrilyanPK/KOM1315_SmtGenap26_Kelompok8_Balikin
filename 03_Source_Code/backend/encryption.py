from cryptography.fernet import Fernet
from app.core.config import settings


# Initialize Fernet with the encryption key from settings
# If the key is empty (e.g. during testing without .env), fallback to a generated key to prevent crashes,
# but print a warning. In production, this should fail if not set.
if settings.ENCRYPTION_KEY:
    _cipher = Fernet(settings.ENCRYPTION_KEY.encode())
else:
    import warnings
    warnings.warn("ENCRYPTION_KEY is not set. Using a temporary key. Data will be lost upon restart.")
    _cipher = Fernet(Fernet.generate_key())


def encrypt_field(value: str) -> str:
    """Encrypt a plaintext string using Fernet."""
    if not value:
        return value
    try:
        return _cipher.encrypt(value.encode()).decode()
    except Exception:
        return value


def decrypt_field(encrypted_value: str) -> str:
    """Decrypt an encrypted string using Fernet. Returns original if not encrypted/invalid."""
    if not encrypted_value:
        return encrypted_value
    try:
        return _cipher.decrypt(encrypted_value.encode()).decode()
    except Exception:
        # Might be plaintext from before encryption was implemented
        return encrypted_value


def mask_phone(phone: str) -> str:
    """Mask a phone number, e.g., 0812****7890."""
    if not phone or len(phone) < 8:
        return "****"
    return f"{phone[:4]}****{phone[-4:]}"
