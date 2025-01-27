from pydantic import BaseModel, Field
from typing import Optional

from app.models import AuditModel


class RatingBase(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Rating score between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment for the rating")

class RatingCreate(RatingBase):
    pass

class RatingInDB(RatingBase, AuditModel):
    solution_slug: str
    username: str