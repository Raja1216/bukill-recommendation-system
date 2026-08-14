import joblib
import numpy as np
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix, save_npz

from app.config import ARTIFACT_DIR
from app.repositories.buckil_repository import BuckilRepository
from app.repositories.interaction_repository import InteractionRepository


def train_collaborative():
    interactions = InteractionRepository().get_weighted_interactions()
    active_buckils = BuckilRepository().get_active_public_buckils()
    active_ids = set(active_buckils["id"].astype(int).tolist())

    interactions = interactions[interactions["buckil_id"].isin(active_ids)].copy()
    if interactions.empty:
        raise RuntimeError("No collaborative interactions available for ACTIVE PUBLIC Buckils.")

    user_ids = np.array(sorted(interactions["user_id"].unique()), dtype=np.int64)
    buckil_ids = np.array(sorted(interactions["buckil_id"].unique()), dtype=np.int64)

    user_to_index = {int(user_id): index for index, user_id in enumerate(user_ids.tolist())}
    buckil_to_index = {int(buckil_id): index for index, buckil_id in enumerate(buckil_ids.tolist())}

    rows = interactions["user_id"].map(user_to_index).to_numpy()
    cols = interactions["buckil_id"].map(buckil_to_index).to_numpy()
    values = interactions["score"].astype(np.float32).to_numpy()

    user_items = csr_matrix(
        (values, (rows, cols)),
        shape=(len(user_ids), len(buckil_ids)),
        dtype=np.float32,
    )

    factors = min(64, max(8, min(user_items.shape) if min(user_items.shape) > 0 else 8))
    model = AlternatingLeastSquares(
        factors=factors,
        regularization=0.05,
        iterations=20,
        random_state=42,
    )
    model.fit(user_items, show_progress=True)

    model.save(str(ARTIFACT_DIR / "collaborative_model.npz"))
    save_npz(ARTIFACT_DIR / "collaborative_user_items.npz", user_items)
    joblib.dump(
        {
            "user_to_index": user_to_index,
            "index_to_user": user_ids.tolist(),
            "buckil_to_index": buckil_to_index,
            "index_to_buckil": buckil_ids.tolist(),
        },
        ARTIFACT_DIR / "collaborative_mappings.joblib",
    )

    print(
        f"Collaborative model trained: {len(user_ids)} users x {len(buckil_ids)} Buckils, factors={factors}"
    )


if __name__ == "__main__":
    train_collaborative()
