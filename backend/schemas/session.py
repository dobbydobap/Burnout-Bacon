from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    task_id: Optional[str] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    planned_duration_min: Optional[int] = None
    session_type: str = "deep_work"


class SessionStart(BaseModel):
    task_id: Optional[str] = None
    session_type: str = "deep_work"


class SessionStop(BaseModel):
    was_completed: bool = True
    focus_rating: Optional[int] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    user_id: str
    task_id: Optional[str]
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    planned_duration_min: Optional[int]
    actual_duration_min: Optional[int]
    session_type: str
    focus_rating: Optional[int]
    notes: Optional[str]
    was_completed: bool
    created_at: datetime
    task_title: Optional[str] = None
