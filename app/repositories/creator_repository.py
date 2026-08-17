import pandas as pd
from sqlalchemy import text

from app.database import engine


class CreatorRepository:

    def get_creator_affinity_candidates(
        self,
        user_id: int,
        limit: int = 150,
    ) -> pd.DataFrame:

        query = text(
            """
            WITH creator_signals AS (

                SELECT
                    b.createdBy AS creator_id,
                    1.0 AS interaction_weight,
                    bv.viewedAt AS event_at
                FROM buckil_views bv
                JOIN buckils b
                    ON b.id = bv.buckilId
                WHERE bv.userId = :user_id


                UNION ALL


                SELECT
                    b.createdBy,
                    3.0,
                    bl.createdAt
                FROM buckil_likes bl
                JOIN buckils b
                    ON b.id = bl.buckilId
                WHERE bl.userId = :user_id


                UNION ALL


                SELECT
                    b.createdBy,
                    4.0,
                    bc.createdAt
                FROM buckil_comments bc
                JOIN buckils b
                    ON b.id = bc.buckilId
                WHERE bc.userId = :user_id


                UNION ALL


                SELECT
                    b.createdBy,
                    6.0,
                    bs.createdAt
                FROM buckil_shares bs
                JOIN buckils b
                    ON b.id = bs.buckilId
                WHERE bs.userId = :user_id


                UNION ALL


                SELECT
                    b.createdBy,
                    CASE
                        WHEN tb.isDone = 1
                            THEN 10.0
                        ELSE 7.0
                    END,
                    CASE
                        WHEN tb.isDone = 1
                            THEN tb.updatedAt
                        ELSE tb.createdAt
                    END
                FROM todo_buckils tb
                JOIN buckils b
                    ON b.id = tb.buckilId
                WHERE tb.userId = :user_id


                UNION ALL


                SELECT
                    b.createdBy,
                    8.0,
                    con.createdAt
                FROM buckil_contributions con
                JOIN buckils b
                    ON b.id = con.buckilId
                WHERE con.userId = :user_id
            ),

            creator_affinity AS (

                SELECT
                    creator_id,

                    SUM(
                        interaction_weight *
                        POW(
                            0.5,
                            GREATEST(
                                TIMESTAMPDIFF(
                                    HOUR,
                                    event_at,
                                    NOW()
                                ),
                                0
                            ) / (24.0 * 60.0)
                        )
                    ) AS affinity_score

                FROM creator_signals

                WHERE creator_id <> :user_id

                GROUP BY creator_id
            )

            SELECT
                b.id AS buckil_id,

                ca.affinity_score *

                POW(
                    0.5,
                    GREATEST(
                        TIMESTAMPDIFF(
                            HOUR,
                            b.createdAt,
                            NOW()
                        ),
                        0
                    ) / (24.0 * 30.0)
                ) AS creator_affinity_score

            FROM creator_affinity ca

            JOIN buckils b
                ON b.createdBy = ca.creator_id

            WHERE b.buckilStatus = 'ACTIVE'
              AND b.privacySetting = 'PUBLIC'
              AND b.isUnattainable = 0
              AND b.createdBy <> :user_id

            ORDER BY creator_affinity_score DESC

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