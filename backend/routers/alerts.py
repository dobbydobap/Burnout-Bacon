from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from models.alert import Alert
from models.user import User
from schemas.alert import AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _alert_response(alert: Alert) -> AlertResponse:
    return AlertResponse(
        id=str(alert.id),
        user_id=str(alert.user_id),
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        is_read=alert.is_read,
        is_dismissed=alert.is_dismissed,
        related_task_id=str(alert.related_task_id) if alert.related_task_id else None,
        created_at=alert.created_at,
    )


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    is_read: bool | None = None,
    alert_type: str | None = None,
    current_user: User = Depends(get_current_user),
):
    query = {"user_id": current_user.id, "is_dismissed": False}
    if is_read is not None:
        query["is_read"] = is_read
    if alert_type:
        query["alert_type"] = alert_type
    alerts = await Alert.find(query).sort("-created_at").to_list()
    return [_alert_response(a) for a in alerts]


@router.patch("/{alert_id}/read")
async def mark_read(
    alert_id: str,
    current_user: User = Depends(get_current_user),
):
    alert = await Alert.find_one(
        Alert.id == PydanticObjectId(alert_id),
        Alert.user_id == current_user.id,
    )
    if alert:
        alert.is_read = True
        await alert.save()
    return {"ok": True}


@router.patch("/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
):
    alert = await Alert.find_one(
        Alert.id == PydanticObjectId(alert_id),
        Alert.user_id == current_user.id,
    )
    if alert:
        alert.is_dismissed = True
        await alert.save()
    return {"ok": True}
