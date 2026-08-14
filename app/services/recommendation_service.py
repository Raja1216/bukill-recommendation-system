from app.config import (
    CONTENT_CANDIDATES,
    COLLAB_CANDIDATES,
    INTEREST_CANDIDATES,
    TRENDING_CANDIDATES,
)
from app.filters.buckil_filter import BuckilFilter
from app.ranking.diversity import diversify
from app.ranking.hybrid import HybridRanker
from app.recommenders.collaborative import CollaborativeRecommender
from app.recommenders.content import ContentRecommender
from app.recommenders.interest import InterestRecommender
from app.recommenders.trending import TrendingRecommender
from app.repositories.user_repository import UserRepository


class RecommendationService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.content = ContentRecommender()
        self.collaborative = CollaborativeRecommender()
        self.interest = InterestRecommender()
        self.trending = TrendingRecommender()
        self.ranker = HybridRanker()
        self.filter = BuckilFilter()

    def load_models(self):
        self.content.load()
        self.collaborative.load()

    def recommend(self, user_id: int, limit: int = 20) -> list[dict]:
        if not self.user_repository.exists(user_id):
            raise ValueError(f"User {user_id} not found or inactive")

        content_candidates = self.content.recommend(user_id, CONTENT_CANDIDATES)
        collaborative_candidates = self.collaborative.recommend(user_id, COLLAB_CANDIDATES)
        interest_candidates = self.interest.recommend(user_id, INTEREST_CANDIDATES)
        trending_candidates = self.trending.recommend(TRENDING_CANDIDATES)

        ranked = self.ranker.rank(
            [
                content_candidates,
                collaborative_candidates,
                interest_candidates,
                trending_candidates,
            ]
        )

        filtered = self.filter.apply(user_id, ranked)
        final_items = diversify(filtered, limit)

        return [
            {
                "buckil_id": int(item["buckil_id"]),
                "score": float(item["score"]),
                "sources": item["sources"],
                "reason": item["reason"],
            }
            for item in final_items[:limit]
        ]

    def similar(self, buckil_id: int, limit: int = 10) -> list[dict]:
        items = self.content.similar(buckil_id, limit)
        return [
            {
                "buckil_id": int(item["buckil_id"]),
                "score": float(item["content_score"]),
            }
            for item in items
        ]

    def trending_items(self, limit: int = 20) -> list[dict]:
        items = self.trending.recommend(limit)
        if not items:
            return []

        max_score = max(float(item["trending_score"]) for item in items) or 1.0
        return [
            {
                "buckil_id": int(item["buckil_id"]),
                "score": round(float(item["trending_score"]) / max_score, 6),
                "sources": ["trending"],
                "reason": "Trending now",
            }
            for item in items
        ]
