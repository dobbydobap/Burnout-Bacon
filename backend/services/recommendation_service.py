"""Recommendation engine based on analytics patterns."""
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from models.task import Task
from models.session import StudySession
from models.recommendation import Recommendation
from models.burnout import BurnoutAssessment


async def generate_recommendations(user_id: PydanticObjectId) -> list[Recommendation]:
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    sessions = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.actual_start >= week_ago,
    ).to_list()

    tasks = await Task.find(Task.user_id == user_id).to_list()
    latest_burnout = await BurnoutAssessment.find(
        BurnoutAssessment.user_id == user_id,
    ).sort("-assessed_at").first_or_none()

    recs = []

    # 1. Best productivity hours
    hourly_mins: dict[int, int] = {}
    for s in sessions:
        if s.actual_start and s.actual_duration_min:
            h = s.actual_start.hour
            hourly_mins[h] = hourly_mins.get(h, 0) + s.actual_duration_min
    if hourly_mins:
        best_hour = max(hourly_mins, key=hourly_mins.get)
        period = "morning" if best_hour < 12 else "afternoon" if best_hour < 17 else "evening"
        recs.append(Recommendation(
            user_id=user_id,
            rec_type="focus_tip",
            title="Optimize Your Schedule",
            body=f"You're most productive in the {period} (around {best_hour}:00). Schedule your hardest tasks then.",
        ))

    # 2. Session length optimization
    completed = [s for s in sessions if s.was_completed and s.actual_duration_min]
    incomplete = [s for s in sessions if not s.was_completed and s.actual_duration_min]
    if completed and incomplete:
        avg_completed = sum(s.actual_duration_min for s in completed) / len(completed)
        avg_incomplete = sum(s.actual_duration_min for s in incomplete) / len(incomplete)
        if avg_incomplete > avg_completed * 1.3:
            recs.append(Recommendation(
                user_id=user_id,
                rec_type="focus_tip",
                title="Shorten Your Sessions",
                body=f"Your completion rate drops for sessions over {int(avg_completed)}min. Try shorter focused blocks.",
            ))

    # 3. Category imbalance
    cat_mins: dict[str, int] = {}
    task_map = {t.id: t.category for t in tasks}
    for s in sessions:
        if s.task_id and s.task_id in task_map and s.actual_duration_min:
            cat = task_map[s.task_id]
            cat_mins[cat] = cat_mins.get(cat, 0) + s.actual_duration_min

    pending_cats = set(t.category for t in tasks if t.status in ("todo", "in_progress"))
    neglected = pending_cats - set(cat_mins.keys())
    for cat in neglected:
        recs.append(Recommendation(
            user_id=user_id,
            rec_type="redistribute",
            title=f"Don't Neglect {cat}",
            body=f"You have pending tasks in {cat} but haven't worked on it this week.",
        ))

    # 4. Burnout-based recommendations
    if latest_burnout and latest_burnout.risk_level in ("high", "critical"):
        recs.append(Recommendation(
            user_id=user_id,
            rec_type="break",
            title="Take a Recovery Break",
            body="Your burnout risk is elevated. Schedule a lighter day or take a full break tomorrow.",
        ))

    # 5. Workload tomorrow
    tomorrow = (now + timedelta(days=1)).date()
    tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
    tomorrow_end = tomorrow_start + timedelta(days=1)
    tomorrow_sessions = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.planned_start >= tomorrow_start,
        StudySession.planned_start < tomorrow_end,
    ).to_list()
    planned_mins = sum(s.planned_duration_min or 60 for s in tomorrow_sessions)
    if planned_mins > 360:
        recs.append(Recommendation(
            user_id=user_id,
            rec_type="reduce_load",
            title="Tomorrow Is Overloaded",
            body=f"You have {planned_mins // 60}h planned tomorrow. Consider moving a low-priority session.",
        ))

    # Save all
    for r in recs:
        await r.insert()

    return recs


async def get_recommendations(user_id: PydanticObjectId) -> list[Recommendation]:
    return await Recommendation.find(
        Recommendation.user_id == user_id,
    ).sort("-created_at").limit(20).to_list()


async def mark_acted(user_id: PydanticObjectId, rec_id: str) -> None:
    rec = await Recommendation.find_one(
        Recommendation.id == PydanticObjectId(rec_id),
        Recommendation.user_id == user_id,
    )
    if rec:
        rec.is_acted_on = True
        await rec.save()
