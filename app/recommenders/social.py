from app.repositories.social_repository import (
    SocialRepository,
)


class SocialRecommender:

    def __init__(self):
        self.repository = SocialRepository()

    def recommend(
        self,
        user_id: int,
        limit: int = 200,
    ) -> list[dict]:

        df = (
            self.repository
            .get_social_candidates(
                user_id=user_id,
                limit=limit,
            )
        )

        if df.empty:
            return []

        return [
            {
                "buckil_id": int(row.buckil_id),

                "social_score": float(
                    row.social_score
                ),
            }

            for row
            in df.itertuples(index=False)
        ]