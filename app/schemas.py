from pydantic import BaseModel, field_validator, Field
from datetime import datetime, timezone
from typing import Optional
import pytz


tz = pytz.timezone('Europe/Moscow')

class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True

class LinkCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = Field(default=None, example=datetime.now(tz).strftime("%Y-%m-%d %H:%M"))

class LinkUpdate(BaseModel):
    short_code_old: str
    short_code_new: str

class Link(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: str
    last_accessed_at: Optional[datetime] = None
    access_count: int
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True