from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class BurnoutAssessment(Document):
    user_id: PydanticObjectId
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    risk_score: float = 0.0
    risk_level: str = "low"
    factors_json: Optional[str] = None
    recommendation: Optional[str] = None

    class Settings:
        name = "burnout_assessments"
        indexes = [
            [("user_id", 1), ("assessed_at", -1)],
        ]
