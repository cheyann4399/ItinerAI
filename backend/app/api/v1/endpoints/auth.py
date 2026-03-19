from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
  create_access_token,
  hash_password,
  verify_password,
)
from app.models.base import get_db
from app.models.user import User
from app.schemas.user import Token, UserRead, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(
  payload: UserRegister,
  db: Session = Depends(get_db),
) -> User:
  if db.query(User).filter(User.email == payload.email).first():
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Email already registered",
    )
  pw_hash = hash_password(payload.password)
  user = User(
    email=payload.email,
    name=payload.name,
    password_hash=pw_hash,
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


@router.post("/login", response_model=Token)
def login(
  payload: UserLogin,
  db: Session = Depends(get_db),
) -> Token:
  user = db.query(User).filter(User.email == payload.email).first()
  if not user or not verify_password(payload.password, user.password_hash):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect email or password",
    )
  return Token(access_token=create_access_token(user.id))
