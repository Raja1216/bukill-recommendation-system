class FreshRecommender:
    """Phase-2 extension point for explicit new-content exploration."""

    def recommend(self, limit: int = 100) -> list[dict]:
        return []
