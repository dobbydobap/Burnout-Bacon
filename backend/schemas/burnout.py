from datetime import datetime
from pydantic import BaseModel


class BurnoutResponse(BaseModel):
    id: int
    risk_score: float
    risk_level: str
    factors_json: str | None
    recommendation: str | None
    assessed_at: datetime

    class Config:
        from_attributes = True
