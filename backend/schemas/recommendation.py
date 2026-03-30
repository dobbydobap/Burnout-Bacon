from datetime import datetime
from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    id: int
    rec_type: str
    title: str
    body: str
    is_acted_on: bool
    related_task_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
