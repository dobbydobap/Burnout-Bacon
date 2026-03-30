"""Smart session distribution — auto-plan sessions across available slots."""
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from models.task import Task
from models.session import StudySession


async def auto_distribute_sessions(
    user_id: PydanticObjectId,
    task_id: str,
    max_daily_hours: float = 4.0,
    session_length_min: int = 60,
    preferred_start_hour: int = 9,
    preferred_end_hour: int = 21,
) -> list[StudySession]:
    task = await Task.find_one(
        Task.id == PydanticObjectId(task_id),
        Task.user_id == user_id,
    )
    if not task:
        return []

    remaining_mins = (task.estimated_minutes or 60) - (task.actual_minutes or 0)
    if remaining_mins <= 0:
        return []

    deadline = task.deadline or (datetime.utcnow() + timedelta(days=7))
    now = datetime.utcnow()

    # Calculate how many sessions we need
    num_sessions = max(1, remaining_mins // session_length_min)
    if remaining_mins % session_length_min > 0:
        num_sessions += 1

    # Get existing sessions for the user in the time range
    existing = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.planned_start >= now,
        StudySession.planned_start <= deadline,
    ).to_list()

    # Build a map of daily booked minutes
    daily_booked: dict[str, int] = {}
    for s in existing:
        if s.planned_start:
            d = s.planned_start.date().isoformat()
            daily_booked[d] = daily_booked.get(d, 0) + (s.planned_duration_min or 60)

    max_daily_mins = int(max_daily_hours * 60)
    created = []
    current_day = now.date() + timedelta(days=1)  # Start tomorrow
    end_day = deadline.date()
    sessions_to_create = num_sessions

    while sessions_to_create > 0 and current_day <= end_day:
        day_key = current_day.isoformat()
        booked = daily_booked.get(day_key, 0)
        available = max_daily_mins - booked

        if available >= session_length_min:
            # Find an open hour slot
            hour = preferred_start_hour
            while hour < preferred_end_hour and sessions_to_create > 0:
                slot_start = datetime.combine(current_day, datetime.min.time().replace(hour=hour))
                # Check no conflict
                conflict = any(
                    s.planned_start and s.planned_start.date() == current_day
                    and s.planned_start.hour == hour
                    for s in existing
                )
                if not conflict and available >= session_length_min:
                    actual_len = min(session_length_min, remaining_mins)
                    session = StudySession(
                        user_id=user_id,
                        task_id=task.id,
                        planned_start=slot_start,
                        planned_end=slot_start + timedelta(minutes=actual_len),
                        planned_duration_min=actual_len,
                        session_type="deep_work",
                    )
                    await session.insert()
                    created.append(session)
                    sessions_to_create -= 1
                    remaining_mins -= actual_len
                    available -= actual_len
                    daily_booked[day_key] = booked + actual_len

                hour += 2  # Space sessions 2 hours apart

        current_day += timedelta(days=1)

    return created
