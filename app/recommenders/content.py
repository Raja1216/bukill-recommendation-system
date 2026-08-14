import numpy as np
from scipy.sparse import load_npz

from app.config import ARTIFACT_DIR


class ContentRecommender:
    def __init__(self):
        self.buckil_ids = None
        self.buckil_vectors = None
        self.user_ids = None
        self.user_profiles = None
        self.user_to_index = {}
        self.buckil_to_index = {}

    def load(self):
        self.buckil_ids = np.load(ARTIFACT_DIR / "buckil_ids.npy")
        self.buckil_vectors = load_npz(ARTIFACT_DIR / "buckil_vectors.npz").tocsr()
        self.user_ids = np.load(ARTIFACT_DIR / "content_user_ids.npy")
        self.user_profiles = load_npz(ARTIFACT_DIR / "user_content_profiles.npz").tocsr()

        self.user_to_index = {int(user_id): i for i, user_id in enumerate(self.user_ids.tolist())}
        self.buckil_to_index = {int(buckil_id): i for i, buckil_id in enumerate(self.buckil_ids.tolist())}

    def recommend(self, user_id: int, limit: int = 200) -> list[dict]:
        user_index = self.user_to_index.get(int(user_id))
        if user_index is None:
            return []

        profile = self.user_profiles[user_index]
        if profile.nnz == 0:
            return []

        # Both matrices are L2-normalized, so their dot product is cosine similarity.
        scores = (profile @ self.buckil_vectors.T).toarray().ravel()
        return self._top_scores(scores, limit, "content_score")

    def similar(self, buckil_id: int, limit: int = 10) -> list[dict]:
        item_index = self.buckil_to_index.get(int(buckil_id))
        if item_index is None:
            return []

        item_vector = self.buckil_vectors[item_index]
        scores = (item_vector @ self.buckil_vectors.T).toarray().ravel()
        scores[item_index] = -np.inf
        return self._top_scores(scores, limit, "content_score")

    def _top_scores(self, scores: np.ndarray, limit: int, score_key: str) -> list[dict]:
        if scores.size == 0 or limit <= 0:
            return []

        finite_indexes = np.where(np.isfinite(scores) & (scores > 0))[0]
        if finite_indexes.size == 0:
            return []

        k = min(int(limit), finite_indexes.size)
        finite_scores = scores[finite_indexes]

        if k == finite_indexes.size:
            top_indexes = finite_indexes[np.argsort(-finite_scores)]
        else:
            local = np.argpartition(-finite_scores, k - 1)[:k]
            top_indexes = finite_indexes[local]
            top_indexes = top_indexes[np.argsort(-scores[top_indexes])]

        return [
            {
                "buckil_id": int(self.buckil_ids[index]),
                score_key: float(scores[index]),
            }
            for index in top_indexes[:k]
        ]
