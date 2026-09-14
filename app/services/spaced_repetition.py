"""
Yagona SM-2 (SuperMemo-2) spaced-repetition algoritmi.

Bot ham, webapp ham shu funksiyadan foydalanadi — shu tufayli endi
ikkita mos kelmaydigan takrorlash tizimi o'rniga bitta manba (DB) bo'ladi.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import UserVocabulary


def apply_review(db: Session, user_vocab: UserVocabulary, correct: bool) -> UserVocabulary:
    """
    Foydalanuvchi so'zni takrorlagandan keyin chaqiriladi.
    `correct=True`  -> "Esladim" / "Bildim"
    `correct=False` -> "Unutdim" / "Bilmadim"
    """
    if correct:
        user_vocab.correct_count += 1
        # Ease factor asta-sekin oshadi (juda oson bo'lib ketmasligi uchun chegaralanadi)
        user_vocab.ease_factor = min(user_vocab.ease_factor + 0.1, 3.0)
        user_vocab.interval_days = max(1, round(user_vocab.interval_days * user_vocab.ease_factor))
        if user_vocab.status == "new":
            user_vocab.status = "learning"
        elif user_vocab.interval_days >= 21:
            user_vocab.status = "mastered"
        else:
            user_vocab.status = "review"
    else:
        user_vocab.wrong_count += 1
        # Xato qilinsa — qiyinlashadi va ertaga qayta ko'rsatiladi
        user_vocab.ease_factor = max(user_vocab.ease_factor - 0.2, 1.3)
        user_vocab.interval_days = 1
        user_vocab.status = "learning"

    user_vocab.last_reviewed_at = datetime.utcnow()
    user_vocab.next_review_at = datetime.utcnow() + timedelta(days=user_vocab.interval_days)

    db.commit()
    db.refresh(user_vocab)
    return user_vocab
