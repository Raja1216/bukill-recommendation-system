import pandas as pd
from sqlalchemy import text

from app.database import engine


class SocialRepository:
    def get_social_candidates(self, user_id: int, limit: int = 200):

        friend_ids_sql = """
            (
                SELECT DISTINCT
                    friendUserId AS friend_id
                FROM friend_users
                WHERE userId = :user_id
                  AND status = 1
                  AND acceptionStatus = 1
                  AND friendUserId <> :user_id
    
                UNION
    
                SELECT DISTINCT
                    userId AS friend_id
                FROM friend_users
                WHERE friendUserId = :user_id
                  AND status = 1
                  AND acceptionStatus = 1
                  AND userId <> :user_id
            )
        """
    
        query = text(f"""
            SELECT
                ss.buckil_id,
    
                SUM(
                    ss.base_score *
                    POW(
                        0.5,
                        GREATEST(
                            TIMESTAMPDIFF(
                                HOUR,
                                ss.event_at,
                                NOW()
                            ),
                            0
                        ) / (24.0 * 30.0)
                    )
                ) AS social_score
    
            FROM
            (
                /* ==========================================
                   1. Followed creator created Buckil
                   ========================================== */
    
                SELECT
                    b.id AS buckil_id,
                    5.0 AS base_score,
                    b.createdAt AS event_at
    
                FROM follow_users fu
    
                JOIN buckils b
                    ON b.createdBy = fu.followedId
    
                WHERE fu.followedByUserId = :user_id
                  AND fu.followedId <> :user_id
    
    
                UNION ALL
    
    
                /* ==========================================
                   2. Friend created Buckil
                   ========================================== */
    
                SELECT
                    b.id AS buckil_id,
                    4.0 AS base_score,
                    b.createdAt AS event_at
    
                FROM {friend_ids_sql} AS f
    
                JOIN buckils b
                    ON b.createdBy = f.friend_id
    
    
                UNION ALL
    
    
                /* ==========================================
                   3. Friend liked Buckil
                   ========================================== */
    
                SELECT
                    bl.buckilId AS buckil_id,
                    2.0 AS base_score,
                    bl.createdAt AS event_at
    
                FROM {friend_ids_sql} AS f
    
                JOIN buckil_likes bl
                    ON bl.userId = f.friend_id
    
    
                UNION ALL
    
    
                /* ==========================================
                   4. Friend commented
                   ========================================== */
    
                SELECT
                    bc.buckilId AS buckil_id,
                    2.5 AS base_score,
                    bc.createdAt AS event_at
    
                FROM {friend_ids_sql} AS f
    
                JOIN buckil_comments bc
                    ON bc.userId = f.friend_id
    
    
                UNION ALL
    
    
                /* ==========================================
                   5. Friend shared
                   ========================================== */
    
                SELECT
                    bs.buckilId AS buckil_id,
                    4.0 AS base_score,
                    bs.createdAt AS event_at
    
                FROM {friend_ids_sql} AS f
    
                JOIN buckil_shares bs
                    ON bs.userId = f.friend_id
    
    
                UNION ALL
    
    
                /* ==========================================
                   6. Friend Todo / Completed
                   ========================================== */
    
                SELECT
                    tb.buckilId AS buckil_id,
    
                    CASE
                        WHEN tb.isDone = 1 THEN 5.0
                        ELSE 3.0
                    END AS base_score,
    
                    CASE
                        WHEN tb.isDone = 1 THEN tb.updatedAt
                        ELSE tb.createdAt
                    END AS event_at
    
                FROM {friend_ids_sql} AS f
    
                JOIN todo_buckils tb
                    ON tb.userId = f.friend_id
    
            ) AS ss
    
            JOIN buckils b
                ON b.id = ss.buckil_id
    
            WHERE b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdBy <> :user_id
    
            GROUP BY ss.buckil_id
    
            HAVING social_score > 0
    
            ORDER BY social_score DESC
    
            LIMIT :limit
        """)
    
        return pd.read_sql(
            query,
            self.engine,
            params={
                "user_id": int(user_id),
                "limit": int(limit)
            }
        )