from app.repositories.user_repository import UserRepository


class InterestRecommender:
    def __init__(self):
        self.user_repository = UserRepository()

    def recommend(self, user_id: int, limit: int = 100) -> list[dict]:
        candidates = self.user_repository.get_interest_candidates(user_id, limit)
        if candidates.empty:
            return []

        max_matches = max(float(candidates["match_count"].max()), 1.0)
        return [
            {
                "buckil_id": int(row.buckil_id),
                "interest_score": float(row.match_count) / max_matches,
            }
            for row in candidates.itertuples(index=False)
        ]
