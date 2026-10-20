from fastapi import APIRouter

from app.schemas.recommendation import RecommendationRequest

router = APIRouter(prefix="/api/v1", tags=["Recommendations"])


@router.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    return {
        "success": True,
        "message": "Recommendation request received",
        "input": request.model_dump(),
        "recommendations": []
    }