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
            SELECT
                b.id AS buckil_id,

                ca.affinity_score
                *
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

            FROM (

                SELECT
                    creator_signals.creator_id,

                    SUM(
                        creator_signals.interaction_weight
                        *
                        POW(
                            0.5,
                            GREATEST(
                                TIMESTAMPDIFF(
                                    HOUR,
                                    creator_signals.event_at,
                                    NOW()
                                ),
                                0
                            ) / (24.0 * 60.0)
                        )
                    ) AS affinity_score

                FROM (

                    /* --------------------------------
                       Views
                       -------------------------------- */

                    SELECT
                        b.createdBy AS creator_id,
                        1.0 AS interaction_weight,
                        bv.viewedAt AS event_at

                    FROM buckil_views bv

                    JOIN buckils b
                        ON b.id = bv.buckilId

                    WHERE bv.userId = :user_id


                    UNION ALL


                    /* --------------------------------
                       Likes
                       -------------------------------- */

                    SELECT
                        b.createdBy AS creator_id,
                        3.0 AS interaction_weight,
                        bl.createdAt AS event_at

                    FROM buckil_likes bl

                    JOIN buckils b
                        ON b.id = bl.buckilId

                    WHERE bl.userId = :user_id


                    UNION ALL


                    /* --------------------------------
                       Comments
                       -------------------------------- */

                    SELECT
                        b.createdBy AS creator_id,
                        4.0 AS interaction_weight,
                        bc.createdAt AS event_at

                    FROM buckil_comments bc

                    JOIN buckils b
                        ON b.id = bc.buckilId

                    WHERE bc.userId = :user_id


                    UNION ALL


                    /* --------------------------------
                       Shares
                       -------------------------------- */

                    SELECT
                        b.createdBy AS creator_id,
                        6.0 AS interaction_weight,
                        bs.createdAt AS event_at

                    FROM buckil_shares bs

                    JOIN buckils b
                        ON b.id = bs.buckilId

                    WHERE bs.userId = :user_id


                    UNION ALL


                    /* --------------------------------
                       Todo / Complete
                       -------------------------------- */

                    SELECT
                        b.createdBy AS creator_id,

                        CASE
                            WHEN tb.isDone = 1
                                THEN 10.0
                            ELSE 7.0
                        END AS interaction_weight,

                        CASE
                            WHEN tb.isDone = 1
                                THEN tb.updatedAt
                            ELSE tb.createdAt
                        END AS event_at

                    FROM todo_buckils tb

                    JOIN buckils b
                        ON b.id = tb.buckilId

                    WHERE tb.userId = :user_id


                    UNION ALL


                    /* --------------------------------
                       Contributions
                       -------------------------------- */

                    SELECT
                        b.createdBy AS creator_id,
                        8.0 AS interaction_weight,
                        con.createdAt AS event_at

                    FROM buckil_contributions con

                    JOIN buckils b
                        ON b.id = con.buckilId

                    WHERE con.userId = :user_id

                ) AS creator_signals

                WHERE creator_signals.creator_id <> :user_id

                GROUP BY creator_signals.creator_id

            ) AS ca

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