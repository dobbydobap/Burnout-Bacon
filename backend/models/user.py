from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class User(Document):
    name: str
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings_json: Optional[str] = None

    class Settings:
        name = "users"
        indexes = ["email"]
