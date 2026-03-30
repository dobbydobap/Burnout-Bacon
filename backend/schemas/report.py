from pydantic import BaseModel


class DailyReport(BaseModel):
    date: str
    total_sessions_planned: int
    sessions_completed: int
    sessions_missed: int
    total_focus_hours: float
    tasks_nearing_deadline: int
    burnout_risk_level: str


class WeeklyReport(BaseModel):
    week_start: str
    week_end: str
    productivity_score: float
    total_focus_hours: float
    tasks_completed: int
    completion_rate: float
    most_productive_day: str
    burnout_trend: str
    recommendations: list[str]
