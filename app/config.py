import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ARTIFACT_DIR = BASE_DIR / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))

CONTENT_CANDIDATES = int(os.getenv("CONTENT_CANDIDATES", "200"))
COLLAB_CANDIDATES = int(os.getenv("COLLAB_CANDIDATES", "200"))
INTEREST_CANDIDATES = int(os.getenv("INTEREST_CANDIDATES", "100"))
TRENDING_CANDIDATES = int(os.getenv("TRENDING_CANDIDATES", "100"))
RECENT_VIEW_EXCLUDE_HOURS = int(os.getenv("RECENT_VIEW_EXCLUDE_HOURS", "24"))

TIME_DECAY_HALF_LIFE_DAYS = 60.0
TRENDING_HALF_LIFE_DAYS = 7.0
MAX_USER_ITEM_INTERACTION_SCORE = 50.0

SOCIAL_CANDIDATES = int(os.getenv("SOCIAL_CANDIDATES", "200"))
CREATOR_AFFINITY_CANDIDATES = int(
    os.getenv("CREATOR_AFFINITY_CANDIDATES", "150")
)
FRESH_CANDIDATES = int(os.getenv("FRESH_CANDIDATES", "100"))

SOCIAL_HALF_LIFE_DAYS = 30.0
CREATOR_AFFINITY_HALF_LIFE_DAYS = 60.0
FRESH_HALF_LIFE_DAYS = 10.0

MAX_PER_CREATOR = 2
MAX_PER_CATEGORY = 3

EVENT_WEIGHTS = {
    "VIEW": 1.0,
    "LIKE": 3.0,
    "COMMENT": 4.0,
    "SHARE": 6.0,
    "TODO": 7.0,
    "CONTRIBUTION": 8.0,
    "COMPLETE": 10.0,
}

# Version-1 ranker. Later these weights can be learned from impression/click data.
HYBRID_WEIGHTS = {
    "content_score": 0.23,
    "collaborative_score": 0.23,
    "social_score": 0.18,
    "interest_score": 0.10,
    "creator_affinity_score": 0.08,
    "trending_score": 0.08,
    "freshness_score": 0.10,
}


