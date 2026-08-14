import numpy as np
import pandas as pd
from sqlalchemy import text

from app.config import (
    EVENT_WEIGHTS,
    MAX_USER_ITEM_INTERACTION_SCORE,
    TIME_DECAY_HALF_LIFE_DAYS,
)
from app.database import engine


class InteractionRepository:
    def get_raw_interactions(self) -> pd.DataFrame:
        # BuckilCompletionInstance has no userId in the supplied Prisma schema.
        # For V1, TodoBuckil.isDone is treated as a COMPLETE user signal.
        query = text(
            """
            SELECT userId AS user_id, buckilId AS buckil_id, 'VIEW' AS event_type, viewedAt AS event_at
            FROM buckil_views
            WHERE userId IS NOT NULL

            UNION ALL

            SELECT userId, buckilId, 'LIKE', createdAt
            FROM buckil_likes

            UNION ALL

            SELECT userId, buckilId, 'COMMENT', createdAt
            FROM buckil_comments

            UNION ALL

            SELECT userId, buckilId, 'SHARE', createdAt
            FROM buckil_shares

            UNION ALL

            SELECT
                userId,
                buckilId,
                CASE WHEN isDone = 1 THEN 'COMPLETE' ELSE 'TODO' END,
                CASE WHEN isDone = 1 THEN updatedAt ELSE createdAt END
            FROM todo_buckils

            UNION ALL

            SELECT userId, buckilId, 'CONTRIBUTION', createdAt
            FROM buckil_contributions
            """
        )
        return pd.read_sql(query, engine)

    def get_weighted_interactions(self) -> pd.DataFrame:
        interactions = self.get_raw_interactions()
        if interactions.empty:
            return pd.DataFrame(columns=["user_id", "buckil_id", "score"])

        interactions = interactions.dropna(subset=["user_id", "buckil_id", "event_at"]).copy()
        interactions["user_id"] = interactions["user_id"].astype(int)
        interactions["buckil_id"] = interactions["buckil_id"].astype(int)
        interactions["event_at"] = pd.to_datetime(interactions["event_at"], errors="coerce")
        interactions = interactions.dropna(subset=["event_at"])

        interactions["base_weight"] = interactions["event_type"].map(EVENT_WEIGHTS).fillna(0.0)
        now = pd.Timestamp.now(tz=None)
        age_days = (now - interactions["event_at"]).dt.total_seconds() / 86400.0
        age_days = age_days.clip(lower=0.0)
        interactions["time_decay"] = np.power(
            0.5,
            age_days / TIME_DECAY_HALF_LIFE_DAYS,
        )
        interactions["weighted_score"] = interactions["base_weight"] * interactions["time_decay"]

        result = (
            interactions.groupby(["user_id", "buckil_id"], as_index=False)["weighted_score"]
            .sum()
            .rename(columns={"weighted_score": "score"})
        )
        result["score"] = result["score"].clip(
            lower=0.0,
            upper=MAX_USER_ITEM_INTERACTION_SCORE,
        )
        return result[result["score"] > 0].reset_index(drop=True)
