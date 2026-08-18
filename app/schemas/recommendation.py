# from pydantic import BaseModel, Field


# class RecommendationItem(BaseModel):
#     buckil_id: int
#     score: float = Field(ge=0.0)
#     sources: list[str]
#     reason: str


# class RecommendationResponse(BaseModel):
#     user_id: int
#     count: int
#     recommendations: list[RecommendationItem]


# class SimilarRecommendationItem(BaseModel):
#     buckil_id: int
#     score: float


# class SimilarRecommendationResponse(BaseModel):
#     buckil_id: int
#     count: int
#     recommendations: list[SimilarRecommendationItem]


# class TrendingRecommendationResponse(BaseModel):
#     count: int
#     recommendations: list[RecommendationItem]



from typing import Optional

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    buckil_id: int
    score: float
    sources: list[str]
    reason: str


class PaginationMeta(BaseModel):
    limit: int
    offset: int
    next_offset: Optional[int] = None
    has_more: bool


class PaginatedRecommendationResponse(BaseModel):
    count: int
    pagination: PaginationMeta
    recommendations: list[RecommendationItem]


class UserRecommendationResponse(BaseModel):
    user_id: int
    count: int
    pagination: PaginationMeta
    recommendations: list[RecommendationItem]


class SimilarRecommendationResponse(BaseModel):
    buckil_id: int
    count: int
    pagination: PaginationMeta
    recommendations: list[RecommendationItem]