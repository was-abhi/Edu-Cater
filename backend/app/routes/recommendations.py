
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.schemas.recommendation import RecommendationRequest

router = APIRouter(prefix="/api/v1", tags=["Recommendations"])

RECOMMENDATION_QUERY = text("""
    SELECT
        c.id AS college_id,
        c.college_code,
        c.college_name,
        c.college_type,
        c.district,
        c.pass_percentage,
        cut.course_code,
        cut.category,
        cut.opening_rank,
        cut.closing_rank AS cutoff_rank
    FROM public.colleges c
    JOIN public.college_cutoffs cut
        ON c.college_code = cut.college_code
    WHERE cut.course_code = :course_code
      AND cut.category = :category
      AND cut.closing_rank >= :keam_rank
    ORDER BY cut.closing_rank ASC
""")


@router.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    recommendations = []

    try:
        with engine.connect() as connection:
            for course_code in request.courses:
                result = connection.execute(
                    RECOMMENDATION_QUERY,
                    {
                        "course_code": course_code,
                        "category": request.category,
                        "keam_rank": request.keam_rank,
                    },
                )

                for row in result.mappings():
                    college = dict(row)

                    if (
                        request.types
                        and college["college_type"] not in request.types
                    ):
                        continue

                    recommendations.append(college)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve college recommendations",
        )

    return {
        "success": True,
        "count": len(recommendations),
        "recommendations": recommendations,
    }
 