from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query

from auth.dependencies import get_current_user
from models.user import User
from services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/daily")
async def daily_report(
    target_date: date = Query(default_factory=date.today),
    current_user: User = Depends(get_current_user),
):
    return await report_service.generate_daily_report(current_user.id, target_date)


@router.get("/weekly")
async def weekly_report(
    week_start: date = Query(default_factory=lambda: date.today() - timedelta(days=date.today().weekday())),
    current_user: User = Depends(get_current_user),
):
    return await report_service.generate_weekly_report(current_user.id, week_start)
