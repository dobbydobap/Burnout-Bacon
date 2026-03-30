from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Alert(Document):
    user_id: PydanticObjectId
    alert_type: str
    severity: str = "info"
    title: str
    message: str
    is_read: bool = False
    is_dismissed: bool = False
    related_task_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "alerts"
        indexes = [
            [("user_id", 1), ("is_read", 1), ("created_at", -1)],
        ]
