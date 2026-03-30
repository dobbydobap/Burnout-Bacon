from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    priority: str = "medium"
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None


class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    category: str
    priority: str
    status: str
    deadline: Optional[datetime]
    estimated_minutes: Optional[int]
    actual_minutes: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
