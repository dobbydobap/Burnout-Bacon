from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Recommendation(Document):
    user_id: PydanticObjectId
    rec_type: str
    title: str
    body: str
    is_acted_on: bool = False
    related_task_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "recommendations"
