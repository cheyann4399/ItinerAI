from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
  name: Mapped[str] = mapped_column(String(100))
  password_hash: Mapped[str] = mapped_column(String(255))
  api_key_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column(
    default=func.now(), server_default=func.now()
  )

