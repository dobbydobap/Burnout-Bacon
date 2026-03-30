from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    user_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    is_read: bool
    is_dismissed: bool
    related_task_id: Optional[str]
    created_at: datetime
