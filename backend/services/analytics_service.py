from datetime import datetime, timedelta, date

from beanie import PydanticObjectId

from models.task import Task
from models.session import StudySession
from models.metric import ProductivityMetric


async def get_summary(user_id: PydanticObjectId) -> dict:
    tasks = await Task.find(Task.user_id == user_id).to_list()
    sessions = await StudySession.find(StudySession.user_id == user_id).to_list()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "done")
    pending = sum(1 for t in tasks if t.status in ("todo", "in_progress"))
    overdue = sum(
        1 for t in tasks
        if t.deadline and t.deadline < datetime.utcnow() and t.status != "done"
    )

    focus_mins = sum(s.actual_duration_min or 0 for s in sessions)
    completed_sessions = [s for s in sessions if s.actual_duration_min]
    avg_duration = (
        sum(s.actual_duration_min for s in completed_sessions) / len(completed_sessions)
        if completed_sessions else 0
    )

    # Streak: consecutive days with at least one session
    session_dates = sorted(set(
        s.actual_start.date() for s in sessions if s.actual_start
    ), reverse=True)
    streak = 0
    check_date = date.today()
    for d in session_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d
        else:
            break

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "overdue_tasks": overdue,
        "total_focus_hours": round(focus_mins / 60, 1),
        "avg_session_duration": round(avg_duration, 1),
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
        "current_streak": streak,
    }


async def get_daily_metrics(
    user_id: PydanticObjectId,
    start: date,
    end: date,
) -> list[dict]:
    metrics = await ProductivityMetric.find(
        ProductivityMetric.user_id == user_id,
        ProductivityMetric.date >= start,
        ProductivityMetric.date <= end,
    ).sort("date").to_list()

    return [
        {
            "date": m.date.isoformat(),
            "total_focus_minutes": m.total_focus_minutes,
            "total_sessions": m.total_sessions,
            "tasks_completed": m.tasks_completed,
            "tasks_created": m.tasks_created,
            "avg_focus_rating": m.avg_focus_rating,
            "deep_work_minutes": m.deep_work_minutes,
        }
        for m in metrics
    ]


async def get_heatmap(user_id: PydanticObjectId, year: int) -> list[dict]:
    sessions = await StudySession.find(
        StudySession.user_id == user_id,
    ).to_list()

    daily = {}
    for s in sessions:
        if not s.actual_start or s.actual_start.year != year:
            continue
        d = s.actual_start.date().isoformat()
        daily[d] = daily.get(d, 0) + (s.actual_duration_min or 0)

    start = date(year, 1, 1)
    end = min(date(year, 12, 31), date.today())
    result = []
    current = start
    while current <= end:
        result.append({"date": current.isoformat(), "value": daily.get(current.isoformat(), 0)})
        current += timedelta(days=1)
    return result


async def get_category_stats(user_id: PydanticObjectId) -> list[dict]:
    tasks = await Task.find(Task.user_id == user_id).to_list()
    sessions = await StudySession.find(StudySession.user_id == user_id).to_list()

    # Map task_id -> category
    task_map = {t.id: t for t in tasks}

    cat_stats: dict[str, dict] = {}
    for t in tasks:
        if t.category not in cat_stats:
            cat_stats[t.category] = {
                "category": t.category,
                "total_tasks": 0,
                "completed_tasks": 0,
                "total_focus_minutes": 0,
                "avg_focus_rating": [],
            }
        cat_stats[t.category]["total_tasks"] += 1
        if t.status == "done":
            cat_stats[t.category]["completed_tasks"] += 1

    for s in sessions:
        if s.task_id and s.task_id in task_map:
            cat = task_map[s.task_id].category
            if cat in cat_stats:
                cat_stats[cat]["total_focus_minutes"] += s.actual_duration_min or 0
                if s.focus_rating:
                    cat_stats[cat]["avg_focus_rating"].append(s.focus_rating)

    result = []
    for cs in cat_stats.values():
        ratings = cs.pop("avg_focus_rating")
        cs["avg_focus_rating"] = round(sum(ratings) / len(ratings), 1) if ratings else None
        cs["completion_rate"] = (
            round(cs["completed_tasks"] / cs["total_tasks"] * 100, 1)
            if cs["total_tasks"] > 0 else 0
        )
        result.append(cs)
    return result


async def get_focus_patterns(user_id: PydanticObjectId) -> dict:
    sessions = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.actual_start != None,
    ).to_list()

    # Hour of day distribution
    hourly = [0] * 24
    # Day of week distribution (0=Mon, 6=Sun)
    daily = [0] * 7

    for s in sessions:
        if s.actual_start and s.actual_duration_min:
            hourly[s.actual_start.hour] += s.actual_duration_min
            daily[s.actual_start.weekday()] += s.actual_duration_min

    return {
        "hourly": [{"hour": h, "minutes": hourly[h]} for h in range(24)],
        "daily": [
            {"day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d], "minutes": daily[d]}
            for d in range(7)
        ],
    }


async def aggregate_daily_metrics(user_id: PydanticObjectId, target_date: date) -> None:
    """Aggregate sessions and tasks into a daily metric snapshot."""
    start = datetime.combine(target_date, datetime.min.time())
    end = start + timedelta(days=1)

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

    tasks_created = await Task.find(
        Task.user_id == user_id,
        Task.created_at >= start,
        Task.created_at < end,
    ).count()

    focus_mins = sum(s.actual_duration_min or 0 for s in sessions)
    deep_mins = sum(
        s.actual_duration_min or 0 for s in sessions if s.session_type == "deep_work"
    )
    ratings = [s.focus_rating for s in sessions if s.focus_rating]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

    existing = await ProductivityMetric.find_one(
        ProductivityMetric.user_id == user_id,
        ProductivityMetric.date == target_date,
    )

    if existing:
        existing.total_focus_minutes = focus_mins
        existing.total_sessions = len(sessions)
        existing.tasks_completed = tasks_completed
        existing.tasks_created = tasks_created
        existing.avg_focus_rating = avg_rating
        existing.deep_work_minutes = deep_mins
        await existing.save()
    else:
        await ProductivityMetric(
            user_id=user_id,
            date=target_date,
            total_focus_minutes=focus_mins,
            total_sessions=len(sessions),
            tasks_completed=tasks_completed,
            tasks_created=tasks_created,
            avg_focus_rating=avg_rating,
            deep_work_minutes=deep_mins,
        ).insert()
