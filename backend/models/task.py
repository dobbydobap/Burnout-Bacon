from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Task(Document):
    user_id: PydanticObjectId
    title: str
    description: Optional[str] = None
    category: str
    priority: str = "medium"
    status: str = "todo"
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Settings:
        name = "tasks"
        indexes = [
            [("user_id", 1), ("status", 1)],
            [("user_id", 1), ("deadline", 1)],
            [("user_id", 1), ("category", 1)],
        ]
