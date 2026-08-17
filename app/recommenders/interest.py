from sqlalchemy import text

from app.database import engine


class InterestRecommender:

    def recommend(
        self,
        user_id: int,
        limit: int = 100,
    ) -> list[dict]:

        query = text(
            """
            SELECT
                b.id AS buckil_id,
                COUNT(DISTINCT bc.categoryId) AS match_count

            FROM user_interests ui

            JOIN categories c
                ON (
                    (
                        ui.categoryId IS NOT NULL
                        AND c.id = ui.categoryId
                    )
                    OR
                    (
                        ui.categoryId IS NULL
                        AND ui.interest IS NOT NULL
                        AND LOWER(TRIM(c.name))
                            = LOWER(TRIM(ui.interest))
                    )
                )

            JOIN buckil_categories bc
                ON bc.categoryId = c.id

            JOIN buckils b
                ON b.id = bc.buckilId

            WHERE ui.userId = :user_id

              AND b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdBy <> :user_id

            GROUP BY b.id

            ORDER BY match_count DESC

            LIMIT :limit
            """
        )

        import pandas as pd

        df = pd.read_sql(
            query,
            engine,
            params={
                "user_id": int(user_id),
                "limit": int(limit),
            },
        )

        if df.empty:
            return []

        max_matches = max(
            float(df["match_count"].max()),
            1.0,
        )

        df["interest_score"] = (
            df["match_count"] / max_matches
        )

        return [
            {
                "buckil_id": int(row.buckil_id),
                "interest_score": float(
                    row.interest_score
                ),
            }
            for row in df.itertuples(index=False)
        ]