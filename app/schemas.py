from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PositionCreate(BaseModel):
    title: str = Field(..., max_length=255, description="Short label for the position")
    description: str = Field(..., max_length=2000, description="Longer description of the position")


class PositionSummary(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    vote_count: int

    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    voter_name: Optional[str] = Field(
        None, max_length=255, description="Optional name to identify the voter"
    )


class PositionDetail(PositionSummary):
    votes: List[VoteCreate] = Field(default_factory=list)
