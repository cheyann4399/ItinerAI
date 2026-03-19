from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, hash_api_key
from app.models.base import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_current_user(
  db: Session = Depends(get_db),
  credentials: HTTPAuthorizationCredentials | None = Depends(security),
  x_api_key: str | None = Depends(api_key_header),
) -> User:
  if x_api_key:
    key_hash = hash_api_key(x_api_key)
    user = db.query(User).filter(User.api_key_hash == key_hash).first()
    if user:
      return user
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid API key",
    )
  if not credentials or credentials.credentials is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Not authenticated",
      headers={"WWW-Authenticate": "Bearer"},
    )
  sub = decode_access_token(credentials.credentials)
  if not sub:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  user = db.query(User).filter(User.id == int(sub)).first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found",
    )
  return user
