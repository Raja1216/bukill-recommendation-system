from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.recommendation import (
    RecommendationResponse,
    SimilarRecommendationResponse,
    TrendingRecommendationResponse,
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("/trending", response_model=TrendingRecommendationResponse)
def trending(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
):
    service = request.app.state.recommendation_service
    items = service.trending_items(limit)
    return {"count": len(items), "recommendations": items}


@router.get("/similar/{buckil_id}", response_model=SimilarRecommendationResponse)
def similar_buckils(
    buckil_id: int,
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
):
    service = request.app.state.recommendation_service
    items = service.similar(buckil_id, limit)
    if not items:
        raise HTTPException(status_code=404, detail="Buckil not found in the content model")
    return {
        "buckil_id": buckil_id,
        "count": len(items),
        "recommendations": items,
    }


@router.get("/{user_id}", response_model=RecommendationResponse)
def recommendations_for_user(
    user_id: int,
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
):
    service = request.app.state.recommendation_service
    try:
        items = service.recommend(user_id=user_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "user_id": user_id,
        "count": len(items),
        "recommendations": items,
    }
