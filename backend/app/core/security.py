import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(plain: str) -> str:
  return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
  return pwd_context.verify(plain, hashed)


def hash_api_key(plain: str) -> str:
  return hashlib.sha256(plain.encode()).hexdigest()


def generate_api_key() -> str:
  return secrets.token_urlsafe(32)


def create_access_token(subject: str | int) -> str:
  expire = datetime.now(timezone.utc) + timedelta(
    minutes=settings.access_token_expire_minutes
  )
  to_encode = {"sub": str(subject), "exp": expire}
  return jwt.encode(
    to_encode, settings.secret_key, algorithm=settings.algorithm
  )


def decode_access_token(token: str) -> str | None:
  try:
    payload = jwt.decode(
      token, settings.secret_key, algorithms=[settings.algorithm]
    )
    return payload.get("sub")
  except JWTError:
    return None
