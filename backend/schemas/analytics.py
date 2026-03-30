from datetime import date
from pydantic import BaseModel


class DailyMetricResponse(BaseModel):
    date: date
    total_focus_minutes: int
    total_sessions: int
    tasks_completed: int
    tasks_created: int
    avg_focus_rating: float | None
    deep_work_minutes: int

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    total_focus_hours: float
    avg_session_duration: float
    completion_rate: float
    current_streak: int


class HeatmapEntry(BaseModel):
    date: str
    value: int
