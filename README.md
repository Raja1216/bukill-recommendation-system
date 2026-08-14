# Buckil Recommendation System V1

## Setup

1. Copy `.env.example` to `.env` and set MySQL credentials.
2. Create a virtual environment and install `requirements.txt`.
3. Test DB: `python test_db.py`
4. Train: `python -m training.train_all`
5. Run API: `uvicorn app.main:app --reload --port 8001`

## APIs

- `GET /health`
- `GET /api/v1/recommendations/{user_id}?limit=20`
- `GET /api/v1/recommendations/similar/{buckil_id}?limit=10`
- `GET /api/v1/recommendations/trending?limit=20`
