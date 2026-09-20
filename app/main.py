from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.database import engine, Base
from app.core.config import settings
from app.core.limiter import limiter
from app.api.routes import (
    router as user_router,
    essay_router,
    vocab_router,
    topic_router
)
from app.api.routes.ai_routes import ai_router
from app.api.routes.review_routes import review_router
from app.api.routes.auth_routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ESLATMA: productionda jadval yaratish/o'zgartirish Alembic orqali bo'lishi kerak.
    # Bu qator faqat local/dev muhitida qulaylik uchun qoldirilgan.
    if not settings.is_production:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created (dev mode)!")
    yield


app = FastAPI(
    title="IELTS Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Faqat aniq belgilangan domenlarga ruxsat — "*" + credentials xavfli kombinatsiya edi
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(essay_router)
app.include_router(vocab_router)
app.include_router(topic_router)
app.include_router(ai_router)
app.include_router(review_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "IELTS Platform API ishlamoqda 🚀"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
