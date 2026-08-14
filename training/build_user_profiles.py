import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz
from sklearn.preprocessing import normalize

from app.config import ARTIFACT_DIR
from app.repositories.interaction_repository import InteractionRepository


def build_user_profiles():
    buckil_ids = np.load(ARTIFACT_DIR / "buckil_ids.npy")
    buckil_vectors = load_npz(ARTIFACT_DIR / "buckil_vectors.npz").tocsr()

    interactions = InteractionRepository().get_weighted_interactions()
    if interactions.empty:
        raise RuntimeError("No user interactions found. Cannot build content user profiles.")

    buckil_to_index = {int(buckil_id): index for index, buckil_id in enumerate(buckil_ids.tolist())}
    interactions = interactions[interactions["buckil_id"].isin(buckil_to_index)].copy()

    if interactions.empty:
        raise RuntimeError("Interactions exist, but none belong to ACTIVE PUBLIC Buckils.")

    user_ids = np.array(sorted(interactions["user_id"].unique()), dtype=np.int64)
    user_to_index = {int(user_id): index for index, user_id in enumerate(user_ids.tolist())}

    rows = interactions["user_id"].map(user_to_index).to_numpy()
    cols = interactions["buckil_id"].map(buckil_to_index).to_numpy()
    values = interactions["score"].astype(np.float32).to_numpy()

    user_item_weights = csr_matrix(
        (values, (rows, cols)),
        shape=(len(user_ids), len(buckil_ids)),
        dtype=np.float32,
    )

    user_profiles = user_item_weights @ buckil_vectors
    user_profiles = normalize(user_profiles, norm="l2", axis=1, copy=False).tocsr()

    save_npz(ARTIFACT_DIR / "user_content_profiles.npz", user_profiles)
    np.save(ARTIFACT_DIR / "content_user_ids.npy", user_ids)

    print(f"User content profiles built: {len(user_ids)} users")


if __name__ == "__main__":
    build_user_profiles()
