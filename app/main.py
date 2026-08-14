from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.recommendation import router as recommendation_router
from app.database import check_connection
from app.services.recommendation_service import RecommendationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_connection()

    service = RecommendationService()
    service.load_models()
    app.state.recommendation_service = service

    yield

    app.state.recommendation_service = None


app = FastAPI(
    title="Buckil Hybrid Recommendation Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(recommendation_router)


@app.get("/health")
def health():
    return {"status": "ok"}
