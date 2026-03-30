"""Auto-reschedule missed sessions into future available slots."""
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from models.session import StudySession


async def reschedule_missed_sessions(user_id: PydanticObjectId) -> list[StudySession]:
    now = datetime.utcnow()

    # Find planned sessions that were never started (past their planned_end)
    missed = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.planned_end < now,
        StudySession.actual_start == None,
    ).to_list()

    if not missed:
        return []

    # Get future existing sessions
    future = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.planned_start >= now,
    ).to_list()

    daily_booked: dict[str, int] = {}
    for s in future:
        if s.planned_start:
            d = s.planned_start.date().isoformat()
            daily_booked[d] = daily_booked.get(d, 0) + (s.planned_duration_min or 60)

    rescheduled = []
    current_day = now.date() + timedelta(days=1)
    max_daily = 240  # 4 hours

    for m in missed:
        duration = m.planned_duration_min or 60
        placed = False

        for day_offset in range(14):  # Try next 2 weeks
            day = current_day + timedelta(days=day_offset)
            day_key = day.isoformat()
            booked = daily_booked.get(day_key, 0)

            if booked + duration <= max_daily:
                # Find a slot (start at 9am, step 2h)
                for hour in range(9, 21, 2):
                    slot_start = datetime.combine(day, datetime.min.time().replace(hour=hour))
                    conflict = any(
                        s.planned_start and s.planned_start.date() == day
                        and abs((s.planned_start - slot_start).total_seconds()) < 3600
                        for s in future
                    )
                    if not conflict:
                        m.planned_start = slot_start
                        m.planned_end = slot_start + timedelta(minutes=duration)
                        await m.save()
                        daily_booked[day_key] = booked + duration
                        rescheduled.append(m)
                        placed = True
                        break

                if placed:
                    break

    return rescheduled


async def rebalance_overloaded_days(user_id: PydanticObjectId) -> int:
    now = datetime.utcnow()
    next_week = now + timedelta(days=7)

    sessions = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.planned_start >= now,
        StudySession.planned_start <= next_week,
        StudySession.actual_start == None,
    ).sort("planned_start").to_list()

    daily: dict[str, list[StudySession]] = {}
    for s in sessions:
        if s.planned_start:
            d = s.planned_start.date().isoformat()
            daily.setdefault(d, []).append(s)

    moved = 0
    max_daily = 300  # 5 hours

    for day_key, day_sessions in daily.items():
        total_mins = sum(s.planned_duration_min or 60 for s in day_sessions)
        if total_mins <= max_daily:
            continue

        # Sort by priority (keep critical tasks, move low priority)
        excess = total_mins - max_daily
        # Move last sessions to next light day
        for s in reversed(day_sessions):
            if excess <= 0:
                break
            dur = s.planned_duration_min or 60
            # Find a lighter day
            for offset in range(1, 4):
                target = (datetime.fromisoformat(day_key) + timedelta(days=offset)).date()
                target_key = target.isoformat()
                target_total = sum(
                    ss.planned_duration_min or 60
                    for ss in daily.get(target_key, [])
                )
                if target_total + dur <= max_daily:
                    for hour in range(9, 21, 2):
                        slot = datetime.combine(target, datetime.min.time().replace(hour=hour))
                        s.planned_start = slot
                        s.planned_end = slot + timedelta(minutes=dur)
                        await s.save()
                        daily.setdefault(target_key, []).append(s)
                        excess -= dur
                        moved += 1
                        break
                    break

    return moved
