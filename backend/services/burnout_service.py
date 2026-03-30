"""Rule-based burnout risk scoring engine."""
import json
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from models.task import Task
from models.session import StudySession
from models.burnout import BurnoutAssessment


async def assess_burnout(user_id: PydanticObjectId) -> BurnoutAssessment:
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    sessions_week = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.actual_start >= week_ago,
    ).to_list()

    sessions_prev_week = await StudySession.find(
        StudySession.user_id == user_id,
        StudySession.actual_start >= two_weeks_ago,
        StudySession.actual_start < week_ago,
    ).to_list()

    tasks = await Task.find(Task.user_id == user_id).to_list()

    factors = []
    score = 0.0

    # Factor 1: Overwork — average daily hours this week
    daily_mins: dict[str, int] = {}
    for s in sessions_week:
        if s.actual_start and s.actual_duration_min:
            d = s.actual_start.date().isoformat()
            daily_mins[d] = daily_mins.get(d, 0) + s.actual_duration_min

    if daily_mins:
        avg_daily_hours = sum(daily_mins.values()) / len(daily_mins) / 60
        if avg_daily_hours > 8:
            score += 0.25
            factors.append({"factor": "overwork", "weight": 0.25, "detail": f"Avg {avg_daily_hours:.1f}h/day this week"})
        elif avg_daily_hours > 5:
            score += 0.15
            factors.append({"factor": "overwork", "weight": 0.15, "detail": f"Avg {avg_daily_hours:.1f}h/day this week"})

    # Factor 2: Missed/incomplete sessions
    total_sessions = len(sessions_week)
    missed = sum(1 for s in sessions_week if not s.was_completed and s.actual_end)
    if total_sessions > 0:
        miss_rate = missed / total_sessions
        if miss_rate > 0.5:
            score += 0.2
            factors.append({"factor": "missed_sessions", "weight": 0.2, "detail": f"{missed}/{total_sessions} incomplete"})
        elif miss_rate > 0.25:
            score += 0.1
            factors.append({"factor": "missed_sessions", "weight": 0.1, "detail": f"{missed}/{total_sessions} incomplete"})

    # Factor 3: Declining focus ratings
    this_week_ratings = [s.focus_rating for s in sessions_week if s.focus_rating]
    prev_week_ratings = [s.focus_rating for s in sessions_prev_week if s.focus_rating]
    if this_week_ratings and prev_week_ratings:
        avg_this = sum(this_week_ratings) / len(this_week_ratings)
        avg_prev = sum(prev_week_ratings) / len(prev_week_ratings)
        if avg_this < avg_prev - 0.5:
            score += 0.15
            factors.append({"factor": "declining_focus", "weight": 0.15, "detail": f"Rating dropped from {avg_prev:.1f} to {avg_this:.1f}"})

    # Factor 4: No rest days
    days_with_sessions = len(daily_mins)
    if days_with_sessions >= 7:
        score += 0.15
        factors.append({"factor": "no_rest_days", "weight": 0.15, "detail": "Worked all 7 days this week"})

    # Factor 5: Overdue tasks pressure
    overdue = [t for t in tasks if t.deadline and t.deadline < now and t.status != "done"]
    if len(overdue) > 5:
        score += 0.2
        factors.append({"factor": "overdue_tasks", "weight": 0.2, "detail": f"{len(overdue)} overdue tasks"})
    elif len(overdue) > 2:
        score += 0.1
        factors.append({"factor": "overdue_tasks", "weight": 0.1, "detail": f"{len(overdue)} overdue tasks"})

    # Factor 6: Late-night work (sessions after 11pm)
    late_sessions = sum(
        1 for s in sessions_week
        if s.actual_start and s.actual_start.hour >= 23
    )
    if late_sessions >= 3:
        score += 0.15
        factors.append({"factor": "late_night_work", "weight": 0.15, "detail": f"{late_sessions} late-night sessions"})

    # Factor 7: Consecutive heavy days (>4h)
    sorted_days = sorted(daily_mins.items())
    consecutive_heavy = 0
    max_consecutive = 0
    for _, mins in sorted_days:
        if mins >= 240:
            consecutive_heavy += 1
            max_consecutive = max(max_consecutive, consecutive_heavy)
        else:
            consecutive_heavy = 0
    if max_consecutive >= 4:
        score += 0.15
        factors.append({"factor": "consecutive_heavy_days", "weight": 0.15, "detail": f"{max_consecutive} consecutive heavy days"})

    score = min(score, 1.0)

    if score < 0.3:
        risk_level = "low"
    elif score < 0.6:
        risk_level = "moderate"
    elif score < 0.8:
        risk_level = "high"
    else:
        risk_level = "critical"

    # Generate recommendation
    rec = _generate_recommendation(risk_level, factors)

    assessment = BurnoutAssessment(
        user_id=user_id,
        risk_score=round(score, 3),
        risk_level=risk_level,
        factors_json=json.dumps(factors),
        recommendation=rec,
    )
    await assessment.insert()
    return assessment


def _generate_recommendation(risk_level: str, factors: list[dict]) -> str:
    if risk_level == "low":
        return "You're doing great! Keep maintaining a healthy balance."

    factor_names = {f["factor"] for f in factors}
    recs = []

    if "overwork" in factor_names:
        recs.append("Reduce your daily work hours — aim for under 5 hours of deep work.")
    if "missed_sessions" in factor_names:
        recs.append("Try shorter session blocks (30-45 min) to improve completion rates.")
    if "no_rest_days" in factor_names:
        recs.append("Schedule at least one full rest day this week.")
    if "overdue_tasks" in factor_names:
        recs.append("Prioritize clearing overdue tasks or renegotiate their deadlines.")
    if "late_night_work" in factor_names:
        recs.append("Avoid working after 11 PM — shift heavy tasks to your peak hours.")
    if "consecutive_heavy_days" in factor_names:
        recs.append("Alternate heavy and light days to prevent cumulative fatigue.")
    if "declining_focus" in factor_names:
        recs.append("Your focus quality is dropping — consider taking a recovery break.")

    if not recs:
        recs.append("Consider reducing your workload and taking more breaks.")

    return " ".join(recs)


async def get_current(user_id: PydanticObjectId) -> BurnoutAssessment | None:
    return await BurnoutAssessment.find(
        BurnoutAssessment.user_id == user_id,
    ).sort("-assessed_at").first_or_none()


async def get_history(user_id: PydanticObjectId, limit: int = 30) -> list[BurnoutAssessment]:
    return await BurnoutAssessment.find(
        BurnoutAssessment.user_id == user_id,
    ).sort("-assessed_at").limit(limit).to_list()
