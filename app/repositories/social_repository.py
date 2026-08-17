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
            WITH friend_ids AS (

                SELECT DISTINCT friendUserId AS friend_id

                FROM friend_users

                WHERE userId = :user_id
                  AND status = 1
                  AND acceptionStatus = 1
                  AND friendUserId <> :user_id


                UNION


                SELECT DISTINCT userId AS friend_id

                FROM friend_users

                WHERE friendUserId = :user_id
                  AND status = 1
                  AND acceptionStatus = 1
                  AND userId <> :user_id
            ),

            social_signals AS (

                /* ----------------------------------
                   Followed creator created Buckil
                   ---------------------------------- */

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


                /* ----------------------------------
                   Friend created Buckil
                   ---------------------------------- */

                SELECT
                    b.id,
                    4.0,
                    b.createdAt

                FROM friend_ids f

                JOIN buckils b
                    ON b.createdBy = f.friend_id


                UNION ALL


                /* ----------------------------------
                   Friend liked Buckil
                   ---------------------------------- */

                SELECT
                    bl.buckilId,
                    2.0,
                    bl.createdAt

                FROM friend_ids f

                JOIN buckil_likes bl
                    ON bl.userId = f.friend_id


                UNION ALL


                /* ----------------------------------
                   Friend commented
                   ---------------------------------- */

                SELECT
                    bc.buckilId,
                    2.5,
                    bc.createdAt

                FROM friend_ids f

                JOIN buckil_comments bc
                    ON bc.userId = f.friend_id


                UNION ALL


                /* ----------------------------------
                   Friend shared
                   ---------------------------------- */

                SELECT
                    bs.buckilId,
                    4.0,
                    bs.createdAt

                FROM friend_ids f

                JOIN buckil_shares bs
                    ON bs.userId = f.friend_id


                UNION ALL


                /* ----------------------------------
                   Friend Todo / Completed
                   ---------------------------------- */

                SELECT
                    tb.buckilId,

                    CASE
                        WHEN tb.isDone = 1
                        THEN 5.0
                        ELSE 3.0
                    END,

                    CASE
                        WHEN tb.isDone = 1
                        THEN tb.updatedAt
                        ELSE tb.createdAt
                    END

                FROM friend_ids f

                JOIN todo_buckils tb
                    ON tb.userId = f.friend_id
            )

            SELECT
                ss.buckil_id,

                SUM(
                    ss.base_score
                    *
                    POW(
                        0.5,

                        GREATEST(
                            TIMESTAMPDIFF(
                                HOUR,
                                ss.event_at,
                                NOW()
                            ),
                            0
                        )

                        / (24.0 * 30.0)
                    )
                ) AS social_score

            FROM social_signals ss

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