from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.models.models import Essay, User, SpeakingAttempt
from app.services.ai_service import (
    analyze_essay,
    check_grammar,
    generate_ideas,
    detect_highlights,
    get_writing_feedback,
    highlight_sample,
    transcribe_audio,
    evaluate_speaking,
)

ai_router = APIRouter(prefix="/ai", tags=["AI"])

# Pullik AI chaqiruvlari uchun cheklov — bitta IP daqiqasiga N marta
AI_RATE_LIMIT = "10/minute"
# Audio (transkripsiya + baholash) qimmatroq — kamroq limit
SPEAKING_RATE_LIMIT = "8/minute"
MAX_AUDIO_BYTES = 15 * 1024 * 1024  # ~15MB — 1-2 daqiqalik yozuv uchun yetarli


class EssayTextInput(BaseModel):
    text: str


class GrammarCheckInput(BaseModel):
    text: str


class IdeaGenInput(BaseModel):
    topic: str


class FeedbackInput(BaseModel):
    essay: str
    task_question: str = ""


class HighlightInput(BaseModel):
    text: str


class EssayAnalyzeInput(BaseModel):
    text: str
    essay_id: int | None = None  # berilsa, natija shu essayga keshlanadi


@ai_router.post("/essay/analyze")
@limiter.limit(AI_RATE_LIMIT)
def ai_analyze_essay(request: Request, data: EssayAnalyzeInput, db: Session = Depends(get_db)):
    # Agar essay_id berilgan bo'lsa va tahlil avval qilingan bo'lsa — qayta AI chaqirmaymiz
    essay = None
    if data.essay_id:
        essay = db.query(Essay).filter(Essay.id == data.essay_id).first()
        if essay and essay.ai_analysis:
            return essay.ai_analysis

    result = analyze_essay(data.text)

    if essay:
        essay.ai_analysis = result
        db.commit()

    return result


@ai_router.post("/essay/check-grammar")
@limiter.limit(AI_RATE_LIMIT)
def ai_check_grammar(request: Request, data: GrammarCheckInput):
    result = check_grammar(data.text)
    return {"errors": result}


@ai_router.post("/idea-generator")
@limiter.limit(AI_RATE_LIMIT)
def ai_generate_ideas(request: Request, data: IdeaGenInput):
    result = generate_ideas(data.topic)
    return result


@ai_router.post("/writing/feedback")
@limiter.limit(AI_RATE_LIMIT)
def ai_writing_feedback(request: Request, data: FeedbackInput):
    result = get_writing_feedback(data.essay, data.task_question)
    return result


@ai_router.post("/sample/highlight")
@limiter.limit(AI_RATE_LIMIT)
def ai_highlight_sample(request: Request, data: HighlightInput):
    result = highlight_sample(data.text)
    return {"highlights": result}


@ai_router.post("/highlights/detect")
@limiter.limit(AI_RATE_LIMIT)
def ai_detect_highlights(request: Request, data: HighlightInput):
    result = detect_highlights(data.text)
    return {"highlights": result}


# ─── SPEAKING: AUDIO YOZUVNI BAHOLASH ─────────────────────
@ai_router.post("/speaking/feedback")
@limiter.limit(SPEAKING_RATE_LIMIT)
async def ai_speaking_feedback(
    request: Request,
    audio: UploadFile = File(...),
    question: str = Form(...),
    part: int = Form(2),
    duration_sec: int | None = Form(None),
    question_id: int | None = Form(None),
    telegram_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio fayl bo'sh")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio fayl juda katta (max ~15MB)")

    transcript = transcribe_audio(audio_bytes, audio.filename or "audio.webm")
    if not transcript:
        return {
            "error": "Ovozni matnga o'girib bo'lmadi. Mikrofon yaxshi ishlayotganiga "
                     "va gapirganingizga ishonch hosil qiling, qayta urinib ko'ring."
        }

    result = evaluate_speaking(transcript, question, part, duration_sec)
    result["transcript"] = transcript

    # Ixtiyoriy: telegram_id berilgan bo'lsa, urinishni saqlaymiz (statistikasi uchun).
    # Bu yerda qattiq auth talab qilmaymiz — /ai/writing/feedback kabi ochiq
    # endpointlar bilan bir xil naqsh; saqlash xato bersa ham natija qaytariladi.
    if telegram_id:
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                attempt = SpeakingAttempt(
                    user_id=user.id,
                    question_id=question_id,
                    part=part,
                    question_text=question,
                    transcript=transcript,
                    duration_sec=duration_sec,
                    ai_feedback=result,
                    ai_band=result.get("band"),
                )
                db.add(attempt)
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"SpeakingAttempt saqlashda xato: {e}")

    return result
