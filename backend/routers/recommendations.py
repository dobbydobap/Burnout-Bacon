from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from models.user import User
from schemas.recommendation import RecommendationResponse
from services import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationResponse])
async def list_recommendations(current_user: User = Depends(get_current_user)):
    recs = await recommendation_service.get_recommendations(current_user.id)
    return [
        RecommendationResponse(
            id=str(r.id),
            rec_type=r.rec_type,
            title=r.title,
            body=r.body,
            is_acted_on=r.is_acted_on,
            related_task_id=str(r.related_task_id) if r.related_task_id else None,
            created_at=r.created_at,
        )
        for r in recs
    ]


@router.post("/generate")
async def generate(current_user: User = Depends(get_current_user)):
    recs = await recommendation_service.generate_recommendations(current_user.id)
    return [
        RecommendationResponse(
            id=str(r.id),
            rec_type=r.rec_type,
            title=r.title,
            body=r.body,
            is_acted_on=r.is_acted_on,
            related_task_id=str(r.related_task_id) if r.related_task_id else None,
            created_at=r.created_at,
        )
        for r in recs
    ]


@router.patch("/{rec_id}/acted")
async def mark_acted(rec_id: str, current_user: User = Depends(get_current_user)):
    await recommendation_service.mark_acted(current_user.id, rec_id)
    return {"ok": True}
