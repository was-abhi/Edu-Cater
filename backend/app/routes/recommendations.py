
from fastapi import APIRouter, HTTPException
from sqlalchemy import text, bindparam
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
    WHERE cut.course_code IN :course_codes
      AND cut.category = :category
      AND cut.closing_rank >= :keam_rank
      AND c.college_type IN :types
    ORDER BY cut.closing_rank ASC
""").bindparams(
    bindparam("course_codes", expanding=True),
    bindparam("types", expanding=True),
)


@router.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                RECOMMENDATION_QUERY,
                {
                    "course_codes": request.courses,
                    "category": request.category,
                    "keam_rank": request.keam_rank,
                    "types": request.types,
                },
            )

            recommendations = [
                dict(row) for row in result.mappings()
            ]

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
