from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class StudySession(Document):
    user_id: PydanticObjectId
    task_id: Optional[PydanticObjectId] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    planned_duration_min: Optional[int] = None
    actual_duration_min: Optional[int] = None
    session_type: str = "deep_work"
    focus_rating: Optional[int] = None
    notes: Optional[str] = None
    was_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "study_sessions"
        indexes = [
            [("user_id", 1), ("actual_start", -1)],
            "task_id",
        ]
