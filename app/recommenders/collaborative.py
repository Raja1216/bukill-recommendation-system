import joblib
from implicit.cpu.als import AlternatingLeastSquares
from scipy.sparse import load_npz

from app.config import ARTIFACT_DIR


class CollaborativeRecommender:
    def __init__(self):
        self.model = None
        self.user_items = None
        self.user_to_index = {}
        self.index_to_buckil = []

    def load(self):
        self.model = AlternatingLeastSquares.load(
            str(ARTIFACT_DIR / "collaborative_model.npz")
        )
        self.user_items = load_npz(
            ARTIFACT_DIR / "collaborative_user_items.npz"
        ).tocsr()
        mappings = joblib.load(ARTIFACT_DIR / "collaborative_mappings.joblib")
        self.user_to_index = mappings["user_to_index"]
        self.index_to_buckil = mappings["index_to_buckil"]

    def recommend(self, user_id: int, limit: int = 200) -> list[dict]:
        user_index = self.user_to_index.get(int(user_id))
        if user_index is None:
            return []

        item_indexes, scores = self.model.recommend(
            userid=user_index,
            user_items=self.user_items[user_index],
            N=int(limit),
            filter_already_liked_items=True,
        )

        return [
            {
                "buckil_id": int(self.index_to_buckil[int(item_index)]),
                "collaborative_score": float(score),
            }
            for item_index, score in zip(item_indexes, scores)
        ]
