from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Session
)
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+aiopg", "postgresql"
).replace(
    "postgresql+asyncpg", "postgresql"
)

# echo faqat development muhitida yoqiladi — productionda SQL loglanmaydi
engine = create_engine(DATABASE_URL, echo=not settings.is_production)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
