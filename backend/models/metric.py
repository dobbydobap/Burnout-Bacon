from datetime import date
from typing import Optional

from beanie import Document, PydanticObjectId


class ProductivityMetric(Document):
    user_id: PydanticObjectId
    date: date
    total_focus_minutes: int = 0
    total_sessions: int = 0
    tasks_completed: int = 0
    tasks_created: int = 0
    avg_focus_rating: Optional[float] = None
    deep_work_minutes: int = 0
    longest_streak_min: int = 0
    categories_json: Optional[str] = None

    class Settings:
        name = "productivity_metrics"
        indexes = [
            [("user_id", 1), ("date", 1)],
        ]
