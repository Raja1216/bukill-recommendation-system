import pandas as pd
from sqlalchemy import text

from app.database import engine


class UserRepository:
    def exists(self, user_id: int) -> bool:
        query = text(
            """
            SELECT 1
            FROM users
            WHERE id = :user_id
              AND status = 1
              AND userActive = 1
            LIMIT 1
            """
        )
        with engine.connect() as connection:
            return connection.execute(query, {"user_id": int(user_id)}).first() is not None

    def get_interests(self, user_id: int) -> pd.DataFrame:
        query = text(
            """
            SELECT
                ui.categoryId AS category_id,
                ui.interest,
                c.name AS category_name
            FROM user_interests ui
            LEFT JOIN categories c ON c.id = ui.categoryId
            WHERE ui.userId = :user_id
            """
        )
        return pd.read_sql(query, engine, params={"user_id": int(user_id)})

    def get_interest_candidates(self, user_id: int, limit: int = 100) -> pd.DataFrame:
        query = text(
            """
            SELECT
                b.id AS buckil_id,
                COUNT(DISTINCT bc.categoryId) AS match_count
            FROM user_interests ui
            JOIN buckil_categories bc ON bc.categoryId = ui.categoryId
            JOIN buckils b ON b.id = bc.buckilId
            WHERE ui.userId = :user_id
              AND ui.categoryId IS NOT NULL
              AND b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdBy <> :user_id
            GROUP BY b.id
            ORDER BY match_count DESC,
                     b.addToTodoCount DESC,
                     b.likesCount DESC,
                     b.createdAt DESC
            LIMIT :limit
            """
        )
        return pd.read_sql(
            query,
            engine,
            params={"user_id": int(user_id), "limit": int(limit)},
        )
