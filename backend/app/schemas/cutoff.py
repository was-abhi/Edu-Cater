
from typing import Literal

from pydantic import BaseModel, Field


class CutoffRequest(BaseModel):
    keam_rank: int = Field(gt=0)

    category: Literal[
        "GN", "SC", "ST", "EZ",
        "MU", "BH", "BX", "EW"
    ]

    courses: list[
        Literal["CS", "ME", "EC", "CE", "EE", "AD", "CY", "AH"]
    ] = Field(min_length=1)

    types: list[str] = Field(min_length=1)
