from typing import Literal

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    keam_rank: int = Field(gt=0)
    category: Literal[
        "general",
        "obc",
        "bx",
        "sc",
        "st",
    ]
    courses: list[str] = Field(min_length=1)
    types: list[str] = Field(min_length=1)