import numpy as np
import pandas as pd

from app.config import TRENDING_HALF_LIFE_DAYS
from app.repositories.buckil_repository import BuckilRepository


class TrendingRecommender:
    def __init__(self):
        self.buckil_repository = BuckilRepository()

    def recommend(self, limit: int = 100) -> list[dict]:
        df = self.buckil_repository.get_trending_pool(days=30, limit=max(2000, int(limit) * 10))
        if df.empty:
            return []

        created_at = pd.to_datetime(df["createdAt"], errors="coerce")
        age_days = (
            pd.Timestamp.now(tz=None) - created_at
        ).dt.total_seconds().div(86400.0).clip(lower=0.0).fillna(30.0)

        engagement = (
            df["likesCount"].fillna(0).astype(float) * 3.0
            + df["commentsCount"].fillna(0).astype(float) * 4.0
            + df["sharesCount"].fillna(0).astype(float) * 6.0
            + df["addToTodoCount"].fillna(0).astype(float) * 7.0
            + df["viewsCount"].fillna(0).astype(float) * 0.2
        )

        freshness = np.power(0.5, age_days / TRENDING_HALF_LIFE_DAYS)
        df["trending_score"] = np.log1p(engagement) * freshness
        df = df.sort_values(["trending_score", "createdAt"], ascending=[False, False]).head(int(limit))

        return [
            {
                "buckil_id": int(row.buckil_id),
                "trending_score": float(row.trending_score),
            }
            for row in df.itertuples(index=False)
        ]
