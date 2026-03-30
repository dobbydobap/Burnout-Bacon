from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from models.user import User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _task_response(task) -> TaskResponse:
    return TaskResponse(
        id=str(task.id),
        user_id=str(task.user_id),
        title=task.title,
        description=task.description,
        category=task.category,
        priority=task.priority,
        status=task.status,
        deadline=task.deadline,
        estimated_minutes=task.estimated_minutes,
        actual_minutes=task.actual_minutes,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    current_user: User = Depends(get_current_user),
):
    tasks = await task_service.get_tasks(current_user.id, status, category, priority)
    return [_task_response(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    task = await task_service.get_task(current_user.id, task_id)
    return _task_response(task)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
):
    task = await task_service.create_task(current_user.id, data)
    return _task_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
):
    task = await task_service.update_task(current_user.id, task_id, data)
    return _task_response(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    await task_service.delete_task(current_user.id, task_id)
