import os
import sys

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_BASE_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from model.recommender import CollegeRecommender

app = FastAPI(
    title="Edu-Cater ML Recommendation Server",
    description="Microservice providing AI/ML-driven college recommendations matching student rank, category, preferred courses, and preferred college types.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = CollegeRecommender()

# EXACT User-Specified Input Model
class RecommendationRequest(BaseModel):
    keam_rank: int = Field(gt=0, description="Student's KEAM entrance exam rank")
    category: Literal[
        "general", "obc", "bx", "sc", "st",
        "ez", "mu", "ew", "gn", "bh",
        "ezhava", "muslim", "ews", "open", "sm",
        "GN", "BH", "BX", "SC", "ST", "EZ", "MU", "EW"
    ] = Field(description="Reservation category supported by the recommendation engine")
    courses: List[str] = Field(min_length=1, description="Courses in preferred order (e.g., ['CS', 'CY'])")
    types: List[str] = Field(min_length=1, description="Types in preferred order: 'government', 'private', 'autonomous'")

    class Config:
        json_schema_extra = {
            "example": {
                "keam_rank": 4500,
                "category": "bx",
                "courses": ["CS", "CY"],
                "types": ["government", "autonomous"]
            }
        }

class CollegeRecommendation(BaseModel):
    college_id: int = Field(..., description="Foreign key matching Supabase public.colleges.id")
    college_code: str = Field(..., description="Official KEAM 3-letter college code (e.g., TCR, TVE, MDL)")
    college_name: str
    college_type: str
    course_code: str
    course_name: str
    applied_category: str
    reservation_quota_used: bool
    admission_probability: float
    recommendation_category: str
    category_opening_rank: int
    category_closing_rank: int
    pass_percentage: float
    district: str
    nba_accredited: bool
    naac_accredited: bool

class RecommendationResponse(BaseModel):
    status: str
    student_rank: int
    category: str
    courses: List[str]
    types: List[str]
    total_recommendations: int
    college_ids: List[int] = Field(..., description="List of IDs for FastAPI backend to query Supabase directly")
    recommendations: List[CollegeRecommendation]

@app.get("/")
def root():
    return {
        "service": "Edu-Cater ML Recommendation Server",
        "status": "online",
        "allowed_engineering_branches": ["CSE / CS", "MECH / ME", "EC", "CIVIL / CE", "EEE / EE", "AI_DS / AD", "CSE_CYBER / CY", "CSE_AI / AH"],
        "supported_categories": [
            "general", "obc", "bx", "sc", "st",
            "ez", "mu", "ew", "gn", "bh"
        ],
        "supported_types": ["government", "private", "autonomous"],
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/recommend", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest):
    """
    Main ML recommendation endpoint:
    Receives exact student inputs:
      - keam_rank
      - category (general, obc, bx, sc, st)
      - courses in preferred order
      - types in preferred order
    Returns top 5 college recommendations and their corresponding Supabase IDs.
    """
    try:
        results = recommender.recommend(
            keam_rank=payload.keam_rank,
            courses=payload.courses,
            types=payload.types,
            category=payload.category,
            top_n=5
        )

        college_ids = [item['college_id'] for item in results]

        return {
            "status": "success",
            "student_rank": payload.keam_rank,
            "category": payload.category,
            "courses": payload.courses,
            "types": payload.types,
            "total_recommendations": len(results),
            "college_ids": college_ids,
            "recommendations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("model.server:app", host="0.0.0.0", port=8001, reload=False)
