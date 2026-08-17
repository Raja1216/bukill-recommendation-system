import pandas as pd
from app.repositories.creator_repository import CreatorRepository


class CreatorAffinityRecommender:

    def __init__(self):
        self.repository = CreatorRepository()

    def recommend(
        self,
        user_id: int,
        limit: int = 150,
    ) -> list[dict]:

        df = self.repository.get_creator_affinity_candidates(
            user_id=user_id,
            limit=limit,
        )

        if df.empty:
            return []

        result = []

        for row in df.itertuples(index=False):
        
            if pd.isna(row.buckil_id):
                continue
            
            score = row.creator_affinity_score
        
            if pd.isna(score):
                score = 0.0
        
            result.append(
                {
                    "buckil_id": int(row.buckil_id),
                    "creator_affinity_score": float(score),
                }
            )
        
        return result