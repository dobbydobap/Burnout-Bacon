"""Daily and weekly report generation."""
from datetime import datetime, timedelta, date

from beanie import PydanticObjectId

from models.task import Task
from models.session import StudySession
from models.burnout import BurnoutAssessment


async def generate_daily_report(user_id: PydanticObjectId, target_date: date) -> dict:
    start = datetime.combine(target_date, datetime.min.time())
    end = start + timedelta(days=1)

    sessions = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.actual_start >= start,
        StudySession.actual_start < end,
    ).to_list()

    planned = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.planned_start >= start,
        StudySession.planned_start < end,
    ).to_list()

    tasks = await Task.find(
        Task.user_id == user_id,
        Task.deadline != None,
    ).to_list()

    completed = sum(1 for s in sessions if s.was_completed)
    missed = sum(1 for s in planned if not s.actual_start and s.planned_end and s.planned_end < datetime.utcnow())
    focus_mins = sum(s.actual_duration_min or 0 for s in sessions)

    nearing_deadline = sum(
        1 for t in tasks
        if t.deadline and t.status != "done"
        and 0 < (t.deadline - datetime.utcnow()).total_seconds() < 48 * 3600
    )

    burnout = await BurnoutAssessment.find(
        BurnoutAssessment.user_id == user_id,
    ).sort("-assessed_at").first_or_none()

    return {
        "date": target_date.isoformat(),
        "total_sessions_planned": len(planned),
        "sessions_completed": completed,
        "sessions_missed": missed,
        "total_focus_hours": round(focus_mins / 60, 1),
        "tasks_nearing_deadline": nearing_deadline,
        "burnout_risk_level": burnout.risk_level if burnout else "low",
    }


async def generate_weekly_report(user_id: PydanticObjectId, week_start: date) -> dict:
    start = datetime.combine(week_start, datetime.min.time())
    end = start + timedelta(days=7)

    sessions = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.actual_start >= start,
        StudySession.actual_start < end,
    ).to_list()

    tasks_completed = await Task.find(
        Task.user_id == user_id,
        Task.completed_at >= start,
        Task.completed_at < end,
    ).count()

    focus_mins = sum(s.actual_duration_min or 0 for s in sessions)
    total = len(sessions)
    completed = sum(1 for s in sessions if s.was_completed)
    completion_rate = round(completed / total * 100, 1) if total > 0 else 0

    # Most productive day
    daily_mins: dict[str, int] = {}
    for s in sessions:
        if s.actual_start and s.actual_duration_min:
            d = s.actual_start.strftime("%A")
            daily_mins[d] = daily_mins.get(d, 0) + s.actual_duration_min
    most_productive = max(daily_mins, key=daily_mins.get) if daily_mins else "N/A"

    # Burnout trend
    burnouts = await BurnoutAssessment.find(
        BurnoutAssessment.user_id == user_id,
        BurnoutAssessment.assessed_at >= start,
        BurnoutAssessment.assessed_at < end,
    ).sort("assessed_at").to_list()

    if len(burnouts) >= 2:
        trend = "increasing" if burnouts[-1].risk_score > burnouts[0].risk_score else "decreasing"
    else:
        trend = "stable"

    # Simple recommendations
    recs = []
    if completion_rate < 50:
        recs.append("Try shorter session blocks to improve completion.")
    if focus_mins / 60 > 35:
        recs.append("You worked over 35h this week — schedule lighter days.")
    if tasks_completed < 3:
        recs.append("Break large tasks into smaller, completable units.")
    if not recs:
        recs.append("Good week! Maintain your current pace.")

    return {
        "week_start": week_start.isoformat(),
        "week_end": (week_start + timedelta(days=6)).isoformat(),
        "productivity_score": completion_rate,
        "total_focus_hours": round(focus_mins / 60, 1),
        "tasks_completed": tasks_completed,
        "completion_rate": completion_rate,
        "most_productive_day": most_productive,
        "burnout_trend": trend,
        "recommendations": recs,
    }
