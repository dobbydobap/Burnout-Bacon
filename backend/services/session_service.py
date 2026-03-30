from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from models.session import StudySession
from models.task import Task
from schemas.session import SessionCreate, SessionStart, SessionStop


async def get_sessions(
    user_id: PydanticObjectId,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict]:
    query = {"user_id": user_id}
    if start_date:
        query["$or"] = [
            {"planned_start": {"$gte": start_date}},
            {"actual_start": {"$gte": start_date}},
        ]

    sessions = await StudySession.find(query).sort("-created_at").to_list()
    result = []
    for s in sessions:
        task_title = None
        if s.task_id:
            task = await Task.get(s.task_id)
            if task:
                task_title = task.title
        result.append({
            "id": str(s.id),
            "user_id": str(s.user_id),
            "task_id": str(s.task_id) if s.task_id else None,
            "planned_start": s.planned_start,
            "planned_end": s.planned_end,
            "actual_start": s.actual_start,
            "actual_end": s.actual_end,
            "planned_duration_min": s.planned_duration_min,
            "actual_duration_min": s.actual_duration_min,
            "session_type": s.session_type,
            "focus_rating": s.focus_rating,
            "notes": s.notes,
            "was_completed": s.was_completed,
            "created_at": s.created_at,
            "task_title": task_title,
        })
    return result


async def create_planned_session(user_id: PydanticObjectId, data: SessionCreate) -> StudySession:
    session = StudySession(
        user_id=user_id,
        task_id=PydanticObjectId(data.task_id) if data.task_id else None,
        planned_start=data.planned_start,
        planned_end=data.planned_end,
        planned_duration_min=data.planned_duration_min,
        session_type=data.session_type,
    )
    await session.insert()
    return session


async def start_session(user_id: PydanticObjectId, data: SessionStart) -> StudySession:
    session = StudySession(
        user_id=user_id,
        task_id=PydanticObjectId(data.task_id) if data.task_id else None,
        actual_start=datetime.utcnow(),
        session_type=data.session_type,
    )
    await session.insert()
    return session


async def stop_session(user_id: PydanticObjectId, session_id: str, data: SessionStop) -> StudySession:
    session = await StudySession.find_one(
        StudySession.id == PydanticObjectId(session_id),
        StudySession.user_id == user_id,
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.actual_end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already stopped")

    session.actual_end = datetime.utcnow()
    if session.actual_start:
        delta = session.actual_end - session.actual_start
        session.actual_duration_min = int(delta.total_seconds() / 60)

    session.was_completed = data.was_completed
    session.focus_rating = data.focus_rating
    session.notes = data.notes

    if session.task_id and session.actual_duration_min:
        task = await Task.get(session.task_id)
        if task:
            task.actual_minutes = (task.actual_minutes or 0) + session.actual_duration_min
            await task.save()

    await session.save()
    return session
