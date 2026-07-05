from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    telegram_id: int
    name: str
    username: Optional[str] = None
    band_level: str = "B2"


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    name: str
    username: Optional[str]
    subscription_type: str
    xp_points: int
    streak_days: int
    band_level: str
    created_at: datetime

    class Config:
        from_attributes = True