"""Alert generation: deadline risks, inactivity, overwork, burnout alerts."""
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from models.task import Task
from models.session import StudySession
from models.alert import Alert
from models.burnout import BurnoutAssessment


async def check_deadline_risks(user_id: PydanticObjectId) -> list[Alert]:
    now = datetime.utcnow()
    tasks = await Task.find(
        Task.user_id == user_id,
        Task.status != "done",
        Task.status != "cancelled",
        Task.deadline != None,
    ).to_list()

    alerts = []
    for task in tasks:
        if not task.deadline:
            continue
        hours_left = (task.deadline - now).total_seconds() / 3600
        remaining_mins = (task.estimated_minutes or 0) - (task.actual_minutes or 0)

        if hours_left <= 0:
            alert = Alert(
                user_id=user_id,
                alert_type="deadline_risk",
                severity="critical",
                title=f"Overdue: {task.title}",
                message=f"This task is past its deadline with {remaining_mins}min of work remaining.",
                related_task_id=task.id,
            )
        elif hours_left <= 24 and remaining_mins > 60:
            alert = Alert(
                user_id=user_id,
                alert_type="deadline_risk",
                severity="critical",
                title=f"Due Soon: {task.title}",
                message=f"Due in {int(hours_left)}h with ~{remaining_mins}min of work remaining.",
                related_task_id=task.id,
            )
        elif hours_left <= 48 and remaining_mins > 120:
            alert = Alert(
                user_id=user_id,
                alert_type="deadline_risk",
                severity="warning",
                title=f"Deadline Approaching: {task.title}",
                message=f"Due in {int(hours_left)}h — you may need to increase your pace.",
                related_task_id=task.id,
            )
        else:
            continue

        await alert.insert()
        alerts.append(alert)

    return alerts


async def check_inactivity(user_id: PydanticObjectId) -> list[Alert]:
    now = datetime.utcnow()
    three_days_ago = now - timedelta(days=3)

    tasks = await Task.find(
        Task.user_id == user_id,
        Task.status != "done",
        Task.status != "cancelled",
    ).to_list()

    alerts = []
    for task in tasks:
        # Check if any session for this task in last 3 days
        recent = await StudySession.find(
            StudySession.user_id == user_id,
            StudySession.task_id == task.id,
            StudySession.actual_start >= three_days_ago,
        ).count()

        if recent == 0 and task.created_at < three_days_ago:
            alert = Alert(
                user_id=user_id,
                alert_type="inactivity",
                severity="info",
                title=f"No Activity: {task.title}",
                message=f"This task has had no sessions in the past 3 days.",
                related_task_id=task.id,
            )
            await alert.insert()
            alerts.append(alert)

    return alerts


async def check_overwork(user_id: PydanticObjectId) -> list[Alert]:
    now = datetime.utcnow()
    alerts = []

    # Check last 3 days for consecutive heavy workload
    for days_ago in range(3):
        day = now - timedelta(days=days_ago)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)

        sessions = await StudySession.find(
            StudySession.user_id == user_id,
            StudySession.actual_start >= day_start,
            StudySession.actual_start < day_end,
        ).to_list()

        total_mins = sum(s.actual_duration_min or 0 for s in sessions)
        if total_mins < 300:  # Less than 5 hours, no consecutive heavy
            break
    else:
        # All 3 days were heavy
        alert = Alert(
            user_id=user_id,
            alert_type="burnout_risk",
            severity="warning",
            title="3 Consecutive Heavy Days",
            message="You've worked over 5 hours for 3 days in a row. Consider taking a lighter day.",
        )
        await alert.insert()
        alerts.append(alert)

    return alerts


async def generate_burnout_alerts(user_id: PydanticObjectId, assessment: BurnoutAssessment) -> list[Alert]:
    alerts = []

    if assessment.risk_level in ("high", "critical"):
        alert = Alert(
            user_id=user_id,
            alert_type="burnout_risk",
            severity="critical" if assessment.risk_level == "critical" else "warning",
            title=f"Burnout Risk: {assessment.risk_level.title()}",
            message=assessment.recommendation or "Your burnout risk is elevated. Please take steps to reduce your workload.",
        )
        await alert.insert()
        alerts.append(alert)

    return alerts


async def run_all_checks(user_id: PydanticObjectId) -> list[Alert]:
    """Run all alert checks. Called by cron."""
    # Clear recent duplicate alerts (don't spam)
    recent = datetime.utcnow() - timedelta(hours=12)
    recent_alerts = await Alert.find(
        Alert.user_id == user_id,
        Alert.created_at >= recent,
    ).to_list()
    recent_types = {(a.alert_type, str(a.related_task_id)) for a in recent_alerts}

    all_alerts = []

    deadline_alerts = await check_deadline_risks(user_id)
    for a in deadline_alerts:
        key = (a.alert_type, str(a.related_task_id))
        if key in recent_types:
            await a.delete()  # Remove duplicate
        else:
            all_alerts.append(a)

    inactivity_alerts = await check_inactivity(user_id)
    for a in inactivity_alerts:
        key = (a.alert_type, str(a.related_task_id))
        if key in recent_types:
            await a.delete()
        else:
            all_alerts.append(a)

    overwork_alerts = await check_overwork(user_id)
    all_alerts.extend(overwork_alerts)

    return all_alerts
