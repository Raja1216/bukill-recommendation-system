from app.config import (
    CONTENT_CANDIDATES,
    COLLAB_CANDIDATES,
    INTEREST_CANDIDATES,
    TRENDING_CANDIDATES,
    SOCIAL_CANDIDATES,
    CREATOR_AFFINITY_CANDIDATES,
    FRESH_CANDIDATES,
)
from app.filters.buckil_filter import BuckilFilter
from app.ranking.diversity import diversify
from app.ranking.hybrid import HybridRanker
from app.recommenders.collaborative import CollaborativeRecommender
from app.recommenders.content import ContentRecommender
from app.recommenders.interest import InterestRecommender
from app.recommenders.trending import TrendingRecommender
from app.repositories.user_repository import UserRepository
from app.recommenders.social import SocialRecommender
from app.recommenders.fresh import FreshRecommender
from app.recommenders.creator_affinity import CreatorAffinityRecommender
from app.exceptions import UserNotFoundError


class RecommendationService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.content = ContentRecommender()
        self.collaborative = CollaborativeRecommender()
        self.interest = InterestRecommender()
        self.social = SocialRecommender()
        self.creator_affinity = CreatorAffinityRecommender()
        self.trending = TrendingRecommender()
        self.fresh = FreshRecommender()
        self.ranker = HybridRanker()
        self.filter = BuckilFilter()

    def load_models(self):
        self.content.load()
        self.collaborative.load()

    def recommend(self, user_id: int, limit: int = 20) -> list[dict]:
        if not self.user_repository.exists(user_id):
            raise UserNotFoundError(f"User {user_id} not found or inactive")

        content_candidates = self.content.recommend(user_id, CONTENT_CANDIDATES)
        collaborative_candidates = self.collaborative.recommend(user_id, COLLAB_CANDIDATES)
        interest_candidates = self.interest.recommend(user_id, INTEREST_CANDIDATES)
        social_candidates = self.social.recommend(user_id, SOCIAL_CANDIDATES)
        creator_candidates = self.creator_affinity.recommend(user_id, CREATOR_AFFINITY_CANDIDATES,)
        trending_candidates = self.trending.recommend(TRENDING_CANDIDATES)
        fresh_candidates = self.fresh.recommend(FRESH_CANDIDATES)

        print("\n========== RECOMMENDATION DEBUG ==========")

        print("USER:", user_id)

        print(
            "CONTENT:",
            len(content_candidates)
        )

        print(
            "COLLABORATIVE:",
            len(collaborative_candidates)
        )

        print(
            "INTEREST:",
            len(interest_candidates)
        )

        print(
            "SOCIAL:",
            len(social_candidates)
        )

        print(
            "CREATOR AFFINITY:",
            len(creator_candidates)
        )

        print(
            "TRENDING:",
            len(trending_candidates)
        )

        print(
            "FRESH:",
            len(fresh_candidates)
        )

        print("==========================================\n")
        
        ranked = self.ranker.rank(
            [
                content_candidates,
                collaborative_candidates,
                social_candidates,
                interest_candidates,
                creator_candidates,
                trending_candidates,
                fresh_candidates,
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
