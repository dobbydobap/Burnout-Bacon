from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from models.user import User
from schemas.burnout import BurnoutResponse
from services import burnout_service

router = APIRouter(prefix="/api/burnout", tags=["burnout"])


@router.get("/current")
async def get_current(current_user: User = Depends(get_current_user)):
    assessment = await burnout_service.get_current(current_user.id)
    if not assessment:
        return {"risk_score": 0, "risk_level": "low", "factors_json": "[]", "recommendation": "No assessment yet."}
    return BurnoutResponse(
        id=str(assessment.id),
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        factors_json=assessment.factors_json,
        recommendation=assessment.recommendation,
        assessed_at=assessment.assessed_at,
    )


@router.get("/history")
async def get_history(current_user: User = Depends(get_current_user)):
    assessments = await burnout_service.get_history(current_user.id)
    return [
        BurnoutResponse(
            id=str(a.id),
            risk_score=a.risk_score,
            risk_level=a.risk_level,
            factors_json=a.factors_json,
            recommendation=a.recommendation,
            assessed_at=a.assessed_at,
        )
        for a in assessments
    ]


@router.post("/assess")
async def trigger_assessment(current_user: User = Depends(get_current_user)):
    assessment = await burnout_service.assess_burnout(current_user.id)
    return BurnoutResponse(
        id=str(assessment.id),
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        factors_json=assessment.factors_json,
        recommendation=assessment.recommendation,
        assessed_at=assessment.assessed_at,
    )
