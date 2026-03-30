from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query

from auth.dependencies import get_current_user
from models.user import User
from services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary(current_user: User = Depends(get_current_user)):
    return await analytics_service.get_summary(current_user.id)


@router.get("/daily")
async def get_daily(
    start: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end: date = Query(default_factory=date.today),
    current_user: User = Depends(get_current_user),
):
    return await analytics_service.get_daily_metrics(current_user.id, start, end)


@router.get("/heatmap")
async def get_heatmap(
    year: int = Query(default_factory=lambda: date.today().year),
    current_user: User = Depends(get_current_user),
):
    return await analytics_service.get_heatmap(current_user.id, year)


@router.get("/categories")
async def get_categories(current_user: User = Depends(get_current_user)):
    return await analytics_service.get_category_stats(current_user.id)


@router.get("/focus-patterns")
async def get_focus_patterns(current_user: User = Depends(get_current_user)):
    return await analytics_service.get_focus_patterns(current_user.id)
