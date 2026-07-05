from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Session
)
from app.core.config import settings

# aiopg o'rniga oddiy psycopg2
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+aiopg", "postgresql"
).replace(
    "postgresql+asyncpg", "postgresql"
)

engine = create_engine(DATABASE_URL, echo=True)

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