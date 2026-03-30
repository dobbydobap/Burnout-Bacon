"""Cron webhook endpoints — called by Google Apps Script or manual triggers."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header

from config import settings
from models.user import User
from services import analytics_service, burnout_service, alert_service, reschedule_service, recommendation_service

router = APIRouter(prefix="/api/cron", tags=["cron"])


async def _get_all_users() -> list[User]:
    return await User.find_all().to_list()


@router.post("/daily-metrics")
async def daily_metrics():
    """Aggregate yesterday's metrics for all users."""
    yesterday = date.today() - timedelta(days=1)
    users = await _get_all_users()
    for user in users:
        await analytics_service.aggregate_daily_metrics(user.id, yesterday)
    return {"ok": True, "users_processed": len(users), "date": yesterday.isoformat()}


@router.post("/burnout-check")
async def burnout_check():
    """Run burnout assessment for all users."""
    users = await _get_all_users()
    results = []
    for user in users:
        assessment = await burnout_service.assess_burnout(user.id)
        await alert_service.generate_burnout_alerts(user.id, assessment)
        results.append({
            "user_id": str(user.id),
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
        })
    return {"ok": True, "results": results}


@router.post("/alert-sweep")
async def alert_sweep():
    """Run all alert checks for all users."""
    users = await _get_all_users()
    total_alerts = 0
    for user in users:
        alerts = await alert_service.run_all_checks(user.id)
        total_alerts += len(alerts)
    return {"ok": True, "alerts_generated": total_alerts}


@router.post("/reschedule-missed")
async def reschedule_missed():
    """Auto-reschedule missed sessions for all users."""
    users = await _get_all_users()
    total_rescheduled = 0
    for user in users:
        rescheduled = await reschedule_service.reschedule_missed_sessions(user.id)
        total_rescheduled += len(rescheduled)
    return {"ok": True, "sessions_rescheduled": total_rescheduled}


@router.post("/generate-recommendations")
async def generate_recommendations():
    """Generate recommendations for all users."""
    users = await _get_all_users()
    total_recs = 0
    for user in users:
        recs = await recommendation_service.generate_recommendations(user.id)
        total_recs += len(recs)
    return {"ok": True, "recommendations_generated": total_recs}


@router.get("/daily-summary")
async def daily_summary():
    """Return today's summary for all users."""
    from services import report_service
    users = await _get_all_users()
    summaries = []
    for user in users:
        report = await report_service.generate_daily_report(user.id, date.today())
        summaries.append({"user_id": str(user.id), **report})
    return {"ok": True, "summaries": summaries}
