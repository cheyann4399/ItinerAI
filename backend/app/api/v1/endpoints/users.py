from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.security import generate_api_key, hash_api_key
from app.models.base import get_db
from app.models.user import User
from app.schemas.user import ApiKeyResponse, UserRead
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
  return current_user


@router.post("/me/api-key", response_model=ApiKeyResponse)
def create_api_key(
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
) -> ApiKeyResponse:
  plain_key = generate_api_key()
  current_user.api_key_hash = hash_api_key(plain_key)
  db.add(current_user)
  db.commit()
  return ApiKeyResponse(api_key=plain_key)
