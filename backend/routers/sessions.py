from datetime import datetime

from fastapi import APIRouter, Depends, Query

from auth.dependencies import get_current_user
from models.user import User
from schemas.session import SessionCreate, SessionStart, SessionStop, SessionResponse
from services import session_service
from services import planner_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _session_response(data: dict) -> SessionResponse:
    return SessionResponse(**data)


def _session_from_doc(session, task_title=None) -> SessionResponse:
    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        task_id=str(session.task_id) if session.task_id else None,
        planned_start=session.planned_start,
        planned_end=session.planned_end,
        actual_start=session.actual_start,
        actual_end=session.actual_end,
        planned_duration_min=session.planned_duration_min,
        actual_duration_min=session.actual_duration_min,
        session_type=session.session_type,
        focus_rating=session.focus_rating,
        notes=session.notes,
        was_completed=session.was_completed,
        created_at=session.created_at,
        task_title=task_title,
    )


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    sessions = await session_service.get_sessions(current_user.id, start_date, end_date)
    return [_session_response(s) for s in sessions]


@router.post("", response_model=SessionResponse, status_code=201)
async def create_planned_session(
    data: SessionCreate,
    current_user: User = Depends(get_current_user),
):
    session = await session_service.create_planned_session(current_user.id, data)
    return _session_from_doc(session)


@router.post("/start", response_model=SessionResponse, status_code=201)
async def start_session(
    data: SessionStart,
    current_user: User = Depends(get_current_user),
):
    session = await session_service.start_session(current_user.id, data)
    return _session_from_doc(session)


@router.post("/{session_id}/stop", response_model=SessionResponse)
async def stop_session(
    session_id: str,
    data: SessionStop,
    current_user: User = Depends(get_current_user),
):
    session = await session_service.stop_session(current_user.id, session_id, data)
    task_title = None
    if session.task_id:
        from models.task import Task
        task = await Task.get(session.task_id)
        if task:
            task_title = task.title
    return _session_from_doc(session, task_title)


@router.post("/auto-plan", response_model=list[SessionResponse])
async def auto_plan(
    task_id: str,
    session_length: int = 60,
    max_daily_hours: float = 4.0,
    current_user: User = Depends(get_current_user),
):
    sessions = await planner_service.auto_distribute_sessions(
        current_user.id, task_id, max_daily_hours, session_length,
    )
    return [_session_from_doc(s) for s in sessions]
