
import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from app.schemas.cutoff import CutoffRequest

load_dotenv()

ML_SERVER_URL = os.getenv(
    "ML_SERVER_URL",
    "http://127.0.0.1:8001",
).rstrip("/")

router = APIRouter(
    prefix="/api/v1",
    tags=["AI Recommendations"],
)


@router.post("/recommendations")
def get_recommendations(request: CutoffRequest):
    payload = {
        "keam_rank": request.keam_rank,
        "category": request.category.upper(),
        "courses": request.courses,
        "types": request.types,
    }

    try:
        response = httpx.post(
            f"{ML_SERVER_URL}/api/v1/recommend",
            json=payload,
            timeout=30.0,
        )

        if response.is_error:
            print("ML server status:", response.status_code)
            print("ML server response:", response.text)
            response.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="The recommendation server timed out.",
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "The recommendation server returned an error.",
                "upstream_status": exc.response.status_code,
                "upstream_response": exc.response.text,
            },
        )

    except httpx.RequestError as exc:
        print("ML server connection error:", str(exc))
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the recommendation server.",
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="The recommendation server returned an invalid response.",
        )
