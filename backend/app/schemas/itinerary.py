from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItineraryBase(BaseModel):
  title: str = Field(..., max_length=255)
  description: str | None = None
  content: dict | None = None


class ItineraryCreate(ItineraryBase):
  pass


class ItineraryUpdate(BaseModel):
  title: str | None = Field(None, max_length=255)
  description: str | None = None
  content: dict | None = None


class ItineraryRead(ItineraryBase):
  model_config = ConfigDict(from_attributes=True)
  id: int
  user_id: int
  created_at: datetime
  updated_at: datetime
