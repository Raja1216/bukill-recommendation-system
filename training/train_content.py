import joblib
import numpy as np
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import ARTIFACT_DIR
from app.repositories.buckil_repository import BuckilRepository


def build_content_text(df):
    # Repeat important short fields so they influence similarity more strongly.
    return (
        df["name"].fillna("")
        + " " + df["name"].fillna("")
        + " " + df["subTitle"].fillna("")
        + " " + df["categories"].fillna("")
        + " " + df["categories"].fillna("")
        + " " + df["tags"].fillna("")
        + " " + df["tags"].fillna("")
        + " " + df["description"].fillna("")
        + " " + df["whyThisMatter"].fillna("")
        + " " + df["location"].fillna("")
    ).str.replace(r"\s+", " ", regex=True).str.strip()


def train_content():
    repository = BuckilRepository()
    buckils = repository.get_active_public_buckils()

    if buckils.empty:
        raise RuntimeError("No ACTIVE PUBLIC Buckils found for content training.")

    buckils["content"] = build_content_text(buckils)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        max_features=30000,
        min_df=1,
        norm="l2",
    )
    buckil_vectors = vectorizer.fit_transform(buckils["content"])

    joblib.dump(vectorizer, ARTIFACT_DIR / "tfidf_vectorizer.joblib")
    save_npz(ARTIFACT_DIR / "buckil_vectors.npz", buckil_vectors.tocsr())
    np.save(ARTIFACT_DIR / "buckil_ids.npy", buckils["id"].astype(int).to_numpy())

    metadata = buckils[["id", "createdBy", "categories", "createdAt"]].copy()
    joblib.dump(metadata, ARTIFACT_DIR / "buckil_metadata.joblib")

    print(f"Content model trained: {len(buckils)} Buckils, {buckil_vectors.shape[1]} TF-IDF features")


if __name__ == "__main__":
    train_content()
