from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_owner_or_bot
from app.models.models import User, UserVocabulary
from app.services.spaced_repetition import apply_review

review_router = APIRouter(prefix="/vocabulary/user", tags=["Review"])


class ReviewInput(BaseModel):
    correct: bool


@review_router.patch("/{telegram_id}/{vocab_id}/review")
def review_word(
    telegram_id: int,
    vocab_id: int,
    data: ReviewInput,
    db: Session = Depends(get_db),
    x_telegram_init_data: str | None = Header(default=None),
    x_bot_secret: str | None = Header(default=None),
):
    verify_owner_or_bot(telegram_id, x_telegram_init_data, x_bot_secret)

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")

    user_vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user.id,
        UserVocabulary.vocab_id == vocab_id,
    ).first()
    if not user_vocab:
        raise HTTPException(404, "Bu so'z foydalanuvchi vocabularysida topilmadi")

    updated = apply_review(db, user_vocab, data.correct)

    return {
        "status": "ok",
        "vocab_id": vocab_id,
        "new_status": updated.status,
        "interval_days": updated.interval_days,
        "next_review_at": updated.next_review_at,
        "correct_count": updated.correct_count,
        "wrong_count": updated.wrong_count,
    }


@review_router.get("/{telegram_id}/due")
def get_due_words(
    telegram_id: int,
    db: Session = Depends(get_db),
    x_telegram_init_data: str | None = Header(default=None),
    x_bot_secret: str | None = Header(default=None),
):
    """Hozir takrorlanishi kerak bo'lgan so'zlar (next_review_at <= hozir)."""
    from datetime import datetime

    verify_owner_or_bot(telegram_id, x_telegram_init_data, x_bot_secret)

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return {"words": []}

    due = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user.id,
        UserVocabulary.next_review_at <= datetime.utcnow(),
    ).all()

    return {"count": len(due), "vocab_ids": [uv.vocab_id for uv in due]}
