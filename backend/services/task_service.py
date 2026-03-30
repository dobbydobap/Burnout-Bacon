from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from models.task import Task
from schemas.task import TaskCreate, TaskUpdate


async def get_tasks(
    user_id: PydanticObjectId,
    status_filter: str | None = None,
    category: str | None = None,
    priority: str | None = None,
) -> list[Task]:
    query = {"user_id": user_id}
    if status_filter:
        query["status"] = status_filter
    if category:
        query["category"] = category
    if priority:
        query["priority"] = priority
    return await Task.find(query).sort("-created_at").to_list()


async def get_task(user_id: PydanticObjectId, task_id: str) -> Task:
    task = await Task.find_one(
        Task.id == PydanticObjectId(task_id),
        Task.user_id == user_id,
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def create_task(user_id: PydanticObjectId, data: TaskCreate) -> Task:
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority,
        deadline=data.deadline,
        estimated_minutes=data.estimated_minutes,
    )
    await task.insert()
    return task


async def update_task(user_id: PydanticObjectId, task_id: str, data: TaskUpdate) -> Task:
    task = await get_task(user_id, task_id)
    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] == "done" and task.status != "done":
        update_data["completed_at"] = datetime.utcnow()

    update_data["updated_at"] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(task, key, value)

    await task.save()
    return task


async def delete_task(user_id: PydanticObjectId, task_id: str) -> None:
    task = await get_task(user_id, task_id)
    await task.delete()
