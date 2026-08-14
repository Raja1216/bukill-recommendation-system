class SocialRecommender:
    """Phase-2 extension point. Add friend/follow candidate generation here."""

    def recommend(self, user_id: int, limit: int = 200) -> list[dict]:
        return []
