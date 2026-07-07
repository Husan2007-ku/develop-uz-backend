from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UserCreate, UserResponse
from app.services import (
    get_or_create_user,
    get_user_by_telegram_id,
    get_user_stats
)
from app.models.models import (
    Essay, Vocabulary, Topic,
    EssayHighlight, UserEssayNote
)

# ─── USERS ────────────────────────────────
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user, is_new = get_or_create_user(db, user_data)
    return user


@router.get("/{telegram_id}", response_model=UserResponse)
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user


@router.get("/{telegram_id}/stats")
def get_stats(telegram_id: int, db: Session = Depends(get_db)):
    stats = get_user_stats(db, telegram_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return stats


# ─── ESSAYS ───────────────────────────────
essay_router = APIRouter(prefix="/essays", tags=["Essays"])


@essay_router.get("/")
def get_essays(
    topic_id: int = None,
    question_type: str = None,
    band_score: float = None,
    is_premium: bool = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Essay)
    if topic_id:
        query = query.filter(Essay.topic_id == topic_id)
    if question_type:
        query = query.filter(Essay.question_type == question_type)
    if band_score:
        query = query.filter(Essay.band_score == band_score)
    if is_premium is not None:
        query = query.filter(Essay.is_premium == is_premium)

    total = query.count()
    essays = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "essays": [
            {
                "id": e.id,
                "title": e.title,
                "question_type": e.question_type,
                "band_score": e.band_score,
                "word_count": e.word_count,
                "is_premium": e.is_premium,
                "topic_id": e.topic_id,
            }
            for e in essays
        ]
    }


@essay_router.get("/{essay_id}")
def get_essay(essay_id: int, db: Session = Depends(get_db)):
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if not essay:
        raise HTTPException(status_code=404, detail="Essay topilmadi")

    highlights = db.query(EssayHighlight).filter(
        EssayHighlight.essay_id == essay_id
    ).all()

    return {
        "id": essay.id,
        "title": essay.title,
        "content": essay.content,
        "question_type": essay.question_type,
        "band_score": essay.band_score,
        "word_count": essay.word_count,
        "is_premium": essay.is_premium,
        "ai_analysis": essay.ai_analysis,
        "topic_id": essay.topic_id,
        "highlights": [
            {
                "id": h.id,
                "text": h.text,
                "highlight_type": h.highlight_type,
                "start_index": h.start_index,
                "end_index": h.end_index,
                "explanation_uz": h.explanation_uz,
                "example": h.example,
            }
            for h in highlights
        ]
    }


@essay_router.get("/{essay_id}/notes/{telegram_id}")
def get_essay_notes(
    essay_id: int,
    telegram_id: int,
    db: Session = Depends(get_db)
):
    from app.models.models import User
    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()
    if not user:
        return {"vocab_notes": "", "grammar_notes": ""}

    note = db.query(UserEssayNote).filter(
        UserEssayNote.essay_id == essay_id,
        UserEssayNote.user_id == user.id
    ).first()

    if not note:
        return {"vocab_notes": "", "grammar_notes": ""}

    return {
        "vocab_notes": note.vocab_notes or "",
        "grammar_notes": note.grammar_notes or ""
    }


@essay_router.put("/{essay_id}/notes/{telegram_id}")
def save_essay_notes(
    essay_id: int,
    telegram_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    from app.models.models import User
    from datetime import datetime

    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    note = db.query(UserEssayNote).filter(
        UserEssayNote.essay_id == essay_id,
        UserEssayNote.user_id == user.id
    ).first()

    if note:
        note.vocab_notes = data.get("vocab_notes", note.vocab_notes)
        note.grammar_notes = data.get("grammar_notes", note.grammar_notes)
        note.updated_at = datetime.utcnow()
    else:
        note = UserEssayNote(
            user_id=user.id,
            essay_id=essay_id,
            vocab_notes=data.get("vocab_notes", ""),
            grammar_notes=data.get("grammar_notes", ""),
        )
        db.add(note)

    db.commit()
    return {"status": "saved"}


# ─── VOCABULARY ───────────────────────────
vocab_router = APIRouter(prefix="/vocabulary", tags=["Vocabulary"])


@vocab_router.get("/")
def get_vocabulary(
    cefr_level: str = None,
    topic_id: int = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Vocabulary)
    if cefr_level:
        query = query.filter(Vocabulary.cefr_level == cefr_level)
    if topic_id:
        query = query.filter(Vocabulary.topic_id == topic_id)

    total = query.count()
    words = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "words": [
            {
                "id": w.id,
                "word": w.word,
                "translation_uz": w.translation_uz,
                "word_type": w.word_type,
                "cefr_level": w.cefr_level,
                "example_1": w.example_1,
                "collocations": w.collocations,
                "synonyms": w.synonyms,
                "word_family": w.word_family,
            }
            for w in words
        ]
    }


@vocab_router.get("/search/{query}")
def search_vocabulary(query: str, db: Session = Depends(get_db)):
    words = db.query(Vocabulary).filter(
        Vocabulary.word.ilike(f"%{query}%")
    ).limit(10).all()

    return {
        "results": [
            {
                "id": w.id,
                "word": w.word,
                "translation_uz": w.translation_uz,
                "cefr_level": w.cefr_level,
                "word_type": w.word_type,
                "example_1": w.example_1,
                "collocations": w.collocations,
                "word_family": w.word_family,
            }
            for w in words
        ]
    }


@vocab_router.get("/daily/{telegram_id}")
def get_daily_vocab(telegram_id: int, db: Session = Depends(get_db)):
    words = db.query(Vocabulary).limit(10).all()
    return {
        "words": [
            {
                "id": w.id,
                "word": w.word,
                "translation_uz": w.translation_uz,
                "word_type": w.word_type,
                "cefr_level": w.cefr_level,
                "example_1": w.example_1,
            }
            for w in words
        ]
    }


# ─── TOPICS ───────────────────────────────
topic_router = APIRouter(prefix="/topics", tags=["Topics"])


@topic_router.get("/")
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return [
        {
            "id": t.id,
            "name_en": t.name_en,
            "name_uz": t.name_uz,
            "icon": t.icon,
        }
        for t in topics
    ]
@vocab_router.post("/user/add")
def add_to_user_vocab(
    data: dict,
    db: Session = Depends(get_db)
):
    from app.models.models import User, UserVocabulary
    from datetime import datetime

    telegram_id = data.get("telegram_id")
    vocab_id = data.get("vocab_id")

    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    existing = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user.id,
        UserVocabulary.vocab_id == vocab_id
    ).first()
    if existing:
        return {"status": "already_exists"}

    uv = UserVocabulary(
        user_id=user.id,
        vocab_id=vocab_id,
        source=data.get("source", "manual"),
        status="new",
        ease_factor=2.5,
        interval_days=1,
        next_review_at=datetime.utcnow()
    )
    db.add(uv)
    db.commit()
    return {"status": "saved"}


@vocab_router.get("/user/{telegram_id}")
def get_user_vocab(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    from app.models.models import User, UserVocabulary

    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()
    if not user:
        return {"words": []}

    user_vocabs = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user.id
    ).all()

    result = []
    for uv in user_vocabs:
        w = db.query(Vocabulary).filter(
            Vocabulary.id == uv.vocab_id
        ).first()
        if w:
            result.append({
                "id": w.id,
                "word": w.word,
                "translation_uz": w.translation_uz,
                "word_type": w.word_type,
                "cefr_level": w.cefr_level,
                "example_1": w.example_1,
                "collocations": w.collocations,
                "word_family": w.word_family,
                "status": uv.status,
                "correct_count": uv.correct_count,
                "wrong_count": uv.wrong_count,
            })

    return {"words": result}