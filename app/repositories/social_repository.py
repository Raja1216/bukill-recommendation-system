import pandas as pd
from sqlalchemy import text

from app.database import engine


class SocialRepository:

    def get_social_candidates(
        self,
        user_id: int,
        limit: int = 200,
    ) -> pd.DataFrame:

        query = text(
            """
            SELECT
                social_signals.buckil_id,

                SUM(
                    social_signals.base_score
                    *
                    POW(
                        0.5,
                        GREATEST(
                            TIMESTAMPDIFF(
                                HOUR,
                                social_signals.event_at,
                                NOW()
                            ),
                            0
                        ) / (24.0 * 30.0)
                    )
                ) AS social_score

            FROM (

                /* ========================================
                   FOLLOWED CREATOR CREATED BUCKIL
                   ======================================== */

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


                /* ========================================
                   FRIEND CREATED BUCKIL
                   ======================================== */

                SELECT
                    b.id AS buckil_id,
                    4.0 AS base_score,
                    b.createdAt AS event_at

                FROM buckils b

                JOIN (

                    SELECT
                        friendUserId AS friend_id

                    FROM friend_users

                    WHERE userId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND friendUserId <> :user_id


                    UNION


                    SELECT
                        userId AS friend_id

                    FROM friend_users

                    WHERE friendUserId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND userId <> :user_id

                ) AS friends

                    ON friends.friend_id = b.createdBy


                UNION ALL


                /* ========================================
                   FRIEND LIKED BUCKIL
                   ======================================== */

                SELECT
                    bl.buckilId AS buckil_id,
                    2.0 AS base_score,
                    bl.createdAt AS event_at

                FROM buckil_likes bl

                JOIN (

                    SELECT
                        friendUserId AS friend_id

                    FROM friend_users

                    WHERE userId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND friendUserId <> :user_id

                    UNION

                    SELECT
                        userId AS friend_id

                    FROM friend_users

                    WHERE friendUserId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND userId <> :user_id

                ) AS friends

                    ON friends.friend_id = bl.userId


                UNION ALL


                /* ========================================
                   FRIEND COMMENTED
                   ======================================== */

                SELECT
                    bc.buckilId AS buckil_id,
                    2.5 AS base_score,
                    bc.createdAt AS event_at

                FROM buckil_comments bc

                JOIN (

                    SELECT friendUserId AS friend_id
                    FROM friend_users
                    WHERE userId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND friendUserId <> :user_id

                    UNION

                    SELECT userId AS friend_id
                    FROM friend_users
                    WHERE friendUserId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND userId <> :user_id

                ) AS friends

                    ON friends.friend_id = bc.userId


                UNION ALL


                /* ========================================
                   FRIEND SHARED
                   ======================================== */

                SELECT
                    bs.buckilId AS buckil_id,
                    4.0 AS base_score,
                    bs.createdAt AS event_at

                FROM buckil_shares bs

                JOIN (

                    SELECT friendUserId AS friend_id
                    FROM friend_users
                    WHERE userId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND friendUserId <> :user_id

                    UNION

                    SELECT userId AS friend_id
                    FROM friend_users
                    WHERE friendUserId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND userId <> :user_id

                ) AS friends

                    ON friends.friend_id = bs.userId


                UNION ALL


                /* ========================================
                   FRIEND TODO / COMPLETE
                   ======================================== */

                SELECT
                    tb.buckilId AS buckil_id,

                    CASE
                        WHEN tb.isDone = 1
                            THEN 5.0
                        ELSE 3.0
                    END AS base_score,

                    CASE
                        WHEN tb.isDone = 1
                            THEN tb.updatedAt
                        ELSE tb.createdAt
                    END AS event_at

                FROM todo_buckils tb

                JOIN (

                    SELECT friendUserId AS friend_id
                    FROM friend_users
                    WHERE userId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND friendUserId <> :user_id

                    UNION

                    SELECT userId AS friend_id
                    FROM friend_users
                    WHERE friendUserId = :user_id
                      AND status = 1
                      AND acceptionStatus = 1
                      AND userId <> :user_id

                ) AS friends

                    ON friends.friend_id = tb.userId

            ) AS social_signals

            JOIN buckils b
                ON b.id = social_signals.buckil_id

            WHERE b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdBy <> :user_id

            GROUP BY social_signals.buckil_id

            HAVING social_score > 0

            ORDER BY social_score DESC

            LIMIT :limit
            """
        )

        return pd.read_sql(
            query,
            engine,
            params={
                "user_id": int(user_id),
                "limit": int(limit),
            },
        )