from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Itinerary(Base):
  __tablename__ = "itineraries"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
  title: Mapped[str] = mapped_column(String(255))
  description: Mapped[str | None] = mapped_column(Text(), nullable=True)
  content: Mapped[dict | None] = mapped_column(JSONB(), nullable=True)
  created_at: Mapped[datetime] = mapped_column(
    default=func.now(), server_default=func.now()
  )
  updated_at: Mapped[datetime] = mapped_column(
    default=func.now(),
    server_default=func.now(),
    onupdate=func.now(),
  )

  user = relationship("User", backref="itineraries")

