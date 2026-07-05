from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.routes import (
    router as user_router,
    essay_router,
    vocab_router,
    topic_router
)
from app.api.routes.ai_routes import ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
    yield


app = FastAPI(
    title="IELTS Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_router)
app.include_router(essay_router)
app.include_router(vocab_router)
app.include_router(topic_router)
app.include_router(ai_router)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "IELTS Platform API ishlamoqda 🚀"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}