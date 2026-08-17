import numpy as np
import pandas as pd

from app.config import FRESH_HALF_LIFE_DAYS
from app.repositories.buckil_repository import BuckilRepository


class FreshRecommender:

    def __init__(self):
        self.repository = BuckilRepository()

    def recommend(
        self,
        limit: int = 100,
    ) -> list[dict]:

        # Get recent Buckils
        df = self.repository.get_trending_pool(
            days=30,
            limit=max(limit * 10, 1000),
        )

        if df.empty:
            return []

        # Make sure createdAt exists
        if "createdAt" not in df.columns:
            print(
                "FreshRecommender error: createdAt column missing.",
                df.columns.tolist(),
            )
            return []

        # Convert createdAt to datetime
        created_at = pd.to_datetime(
            df["createdAt"],
            errors="coerce",
        )

        now = pd.Timestamp.now(tz=None)

        # Calculate age
        age_days = (
            now - created_at
        ).dt.total_seconds() / 86400

        age_days = (
            age_days
            .clip(lower=0)
            .fillna(30)
        )

        # IMPORTANT:
        # Create freshness_score BEFORE accessing it
        df["freshness_score"] = np.power(
            0.5,
            age_days / FRESH_HALF_LIFE_DAYS,
        )

        # Clean NaN / Infinity
        df["freshness_score"] = (
            df["freshness_score"]
            .replace(
                [np.inf, -np.inf],
                0.0,
            )
            .fillna(0.0)
        )

        # Remove rows without valid Buckil ID
        df = df[
            df["buckil_id"].notna()
        ].copy()

        # Sort newest/highest freshness first
        df = df.sort_values(
            by=[
                "freshness_score",
                "createdAt",
            ],
            ascending=[
                False,
                False,
            ],
        )

        df = df.head(limit)

        results = []

        for row in df.itertuples(index=False):

            if pd.isna(row.buckil_id):
                continue

            score = row.freshness_score

            if pd.isna(score):
                score = 0.0

            results.append(
                {
                    "buckil_id": int(
                        row.buckil_id
                    ),
                    "freshness_score": float(
                        score
                    ),
                }
            )

        return results