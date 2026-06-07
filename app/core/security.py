import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt
from pwdlib import PasswordHash
from app.core.config import settings


# -------------------------
# Password hashing
# -------------------------
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# -------------------------
# JWT Access Token
# -------------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# -------------------------
# Refresh Token (random string)
# -------------------------
def create_refresh_token() -> str:
    return str(uuid.uuid4())