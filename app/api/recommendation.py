from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.recommendation import (
    UserRecommendationResponse,
    SimilarRecommendationResponse,
    PaginatedRecommendationResponse,
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("/trending", response_model=PaginatedRecommendationResponse)
def trending(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    service = request.app.state.recommendation_service
    # items = service.trending_items(limit)
    items = service.trending_paginated(limit=limit, offset=offset)
    return items


@router.get("/similar/{buckil_id}", response_model=SimilarRecommendationResponse)
def similar_buckils(
    buckil_id: int,
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    service = request.app.state.recommendation_service
    # items = service.similar(buckil_id, limit)
    items = service.similar_paginated( buckil_id=buckil_id, limit=limit, offset=offset,)
    if not items:
        raise HTTPException(status_code=404, detail="Buckil not found in the content model")
    return items


@router.get("/{user_id}", response_model=UserRecommendationResponse)
def recommendations_for_user(
    user_id: int,
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    service = request.app.state.recommendation_service
    try:
        # items = service.recommend(user_id=user_id, limit=limit)
        items = service.recommend_paginated(user_id=user_id, limit=limit, offset=offset,)
        return items
    except ValueError as exc:
        print(f"Recommendation error for user {user_id}:", repr(exc),)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
