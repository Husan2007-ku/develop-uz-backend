from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import (
    analyze_essay,
    check_grammar,
    generate_ideas,
    detect_highlights,
    get_writing_feedback,
    highlight_sample,
)

ai_router = APIRouter(prefix="/ai", tags=["AI"])


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


@ai_router.post("/essay/analyze")
def ai_analyze_essay(data: EssayTextInput):
    result = analyze_essay(data.text)
    return result


@ai_router.post("/essay/check-grammar")
def ai_check_grammar(data: GrammarCheckInput):
    result = check_grammar(data.text)
    return {"errors": result}


@ai_router.post("/idea-generator")
def ai_generate_ideas(data: IdeaGenInput):
    result = generate_ideas(data.topic)
    return result


@ai_router.post("/writing/feedback")
def ai_writing_feedback(data: FeedbackInput):
    result = get_writing_feedback(data.essay, data.task_question)
    return result


@ai_router.post("/sample/highlight")
def ai_highlight_sample(data: HighlightInput):
    result = highlight_sample(data.text)
    return {"highlights": result}


@ai_router.post("/highlights/detect")
def ai_detect_highlights(data: HighlightInput):
    result = detect_highlights(data.text)
    return {"highlights": result}