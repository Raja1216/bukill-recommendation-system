from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import bindparam, text

from app.database import engine


class BuckilRepository:
    def get_active_public_buckils(self) -> pd.DataFrame:
        query = text(
            """
            SELECT
                b.id,
                b.name,
                b.subTitle,
                b.description,
                b.whyThisMatter,
                b.tags,
                b.location,
                b.createdBy,
                b.likesCount,
                b.commentsCount,
                b.sharesCount,
                b.viewsCount,
                b.addToTodoCount,
                b.createdAt,
                b.updatedAt,
                b.postType,
                b.type,
                COALESCE(GROUP_CONCAT(DISTINCT c.name SEPARATOR ' '), '') AS categories
            FROM buckils b
            LEFT JOIN buckil_categories bc ON bc.buckilId = b.id
            LEFT JOIN categories c ON c.id = bc.categoryId AND c.status = 1
            WHERE b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
            GROUP BY
                b.id, b.name, b.subTitle, b.description, b.whyThisMatter,
                b.tags, b.location, b.createdBy, b.likesCount, b.commentsCount,
                b.sharesCount, b.viewsCount, b.addToTodoCount, b.createdAt,
                b.updatedAt, b.postType, b.type
            """
        )
        return pd.read_sql(query, engine)

    def get_trending_pool(self, days: int = 30, limit: int = 2000) -> pd.DataFrame:
        cutoff = datetime.now() - timedelta(days=days)
        query = text(
            """
            SELECT
                b.id AS buckil_id,
                b.createdBy,
                b.likesCount,
                b.commentsCount,
                b.sharesCount,
                b.viewsCount,
                b.addToTodoCount,
                b.createdAt
            FROM buckils b
            WHERE b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdAt >= :cutoff
            ORDER BY b.createdAt DESC
            LIMIT :limit
            """
        )
        return pd.read_sql(query, engine, params={"cutoff": cutoff, "limit": int(limit)})

    def get_eligible_ids(self, user_id: int, buckil_ids: list[int], recent_hours: int = 24) -> set[int]:
        if not buckil_ids:
            return set()

        cutoff = datetime.now() - timedelta(hours=recent_hours)
        statement = text(
            """
            SELECT b.id
            FROM buckils b
            WHERE b.id IN :buckil_ids
              AND b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdBy <> :user_id
              AND NOT EXISTS (
                    SELECT 1
                    FROM buckil_reports br
                    WHERE br.buckilId = b.id
                      AND br.userId = :user_id
              )
              AND NOT EXISTS (
                    SELECT 1
                    FROM buckil_block_users bu
                    WHERE
                        (bu.userId = :user_id AND bu.buckilId = b.id)
                        OR (bu.userId = :user_id AND bu.blockedUserId = b.createdBy)
                        OR (bu.userId = b.createdBy AND bu.blockedUserId = :user_id)
              )
              AND NOT EXISTS (
                    SELECT 1
                    FROM buckil_views bv
                    WHERE bv.buckilId = b.id
                      AND bv.userId = :user_id
                      AND bv.viewedAt >= :view_cutoff
              )
            """
        ).bindparams(bindparam("buckil_ids", expanding=True))

        with engine.connect() as connection:
            rows = connection.execute(
                statement,
                {
                    "buckil_ids": [int(x) for x in buckil_ids],
                    "user_id": int(user_id),
                    "view_cutoff": cutoff,
                },
            ).fetchall()
        return {int(row[0]) for row in rows}
