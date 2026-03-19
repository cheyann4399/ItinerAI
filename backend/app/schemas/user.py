from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
  email: EmailStr
  name: str


class UserCreate(UserBase):
  pass


class UserRegister(BaseModel):
  email: EmailStr
  name: str
  password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
  email: EmailStr
  password: str


class UserRead(UserBase):
  model_config = ConfigDict(from_attributes=True)
  id: int
  created_at: datetime


class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"


class ApiKeyResponse(BaseModel):
  api_key: str
