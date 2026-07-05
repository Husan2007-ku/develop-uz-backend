from datetime import datetime
from sqlalchemy import (
    String, Integer, Float, BigInteger,
    Boolean, Text, ForeignKey, JSON
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    subscription_type: Mapped[str] = mapped_column(
        String(20), default="free"
    )
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )
    xp_points: Mapped[int] = mapped_column(default=0)
    streak_days: Mapped[int] = mapped_column(default=0)
    last_active_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    band_level: Mapped[str] = mapped_column(
        String(5), default="B2"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    vocab_progress = relationship(
        "UserVocabulary", back_populates="user"
    )
    essay_progress = relationship(
        "UserEssay", back_populates="user"
    )
    essay_notes = relationship(
        "UserEssayNote", back_populates="user"
    )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String(100))
    name_uz: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(10), default="📚")

    essays = relationship("Essay", back_populates="topic")
    vocabulary = relationship("Vocabulary", back_populates="topic")


class Essay(Base):
    __tablename__ = "essays"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    question_type: Mapped[str] = mapped_column(String(50))
    band_score: Mapped[float] = mapped_column(Float)
    content: Mapped[str] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(default=0)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_analysis: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    topic = relationship("Topic", back_populates="essays")
    user_essays = relationship(
        "UserEssay", back_populates="essay"
    )
    highlights = relationship(
        "EssayHighlight", back_populates="essay"
    )
    user_notes = relationship(
        "UserEssayNote", back_populates="essay"
    )


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(100), index=True)
    translation_uz: Mapped[str] = mapped_column(String(300))
    word_type: Mapped[str] = mapped_column(String(20))
    cefr_level: Mapped[str] = mapped_column(String(5))
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id"), nullable=True
    )
    definition_uz: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    example_1: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    example_2: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    example_3: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    collocations: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    synonyms: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )
    word_family: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    topic = relationship("Topic", back_populates="vocabulary")
    user_progress = relationship(
        "UserVocabulary", back_populates="vocab"
    )


class UserVocabulary(Base):
    __tablename__ = "user_vocabulary"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vocab_id: Mapped[int] = mapped_column(
        ForeignKey("vocabulary.id")
    )
    source: Mapped[str] = mapped_column(
        String(20), default="manual"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="new"
    )
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(default=1)
    next_review_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    correct_count: Mapped[int] = mapped_column(default=0)
    wrong_count: Mapped[int] = mapped_column(default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    user = relationship("User", back_populates="vocab_progress")
    vocab = relationship(
        "Vocabulary", back_populates="user_progress"
    )


class UserEssay(Base):
    __tablename__ = "user_essays"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    essay_id: Mapped[int] = mapped_column(ForeignKey("essays.id"))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    user_written_text: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    ai_band_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    ai_feedback: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user = relationship("User", back_populates="essay_progress")
    essay = relationship("Essay", back_populates="user_essays")


class EssayHighlight(Base):
    __tablename__ = "essay_highlights"

    id: Mapped[int] = mapped_column(primary_key=True)
    essay_id: Mapped[int] = mapped_column(ForeignKey("essays.id"))
    start_index: Mapped[int] = mapped_column(Integer)
    end_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    highlight_type: Mapped[str] = mapped_column(String(20))
    explanation_uz: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    example: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    essay = relationship("Essay", back_populates="highlights")


class UserEssayNote(Base):
    __tablename__ = "user_essay_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    essay_id: Mapped[int] = mapped_column(ForeignKey("essays.id"))
    vocab_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    grammar_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    user = relationship("User", back_populates="essay_notes")
    essay = relationship("Essay", back_populates="user_notes")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id"), nullable=True
    )
    article_type: Mapped[str] = mapped_column(
        String(20), default="academic"
    )
    cefr_level: Mapped[str] = mapped_column(String(5), default="C1")
    content: Mapped[str] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(default=0)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    writing_task_q: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    ai_analysis: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    topic = relationship("Topic")
    highlights = relationship(
        "ArticleHighlight", back_populates="article"
    )


class ArticleHighlight(Base):
    __tablename__ = "article_highlights"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id")
    )
    start_index: Mapped[int] = mapped_column(Integer)
    end_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    highlight_type: Mapped[str] = mapped_column(String(20))
    explanation_uz: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    example: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    article = relationship("Article", back_populates="highlights")


class GrammarStructure(Base):
    __tablename__ = "grammar_structures"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50))
    band_level: Mapped[str] = mapped_column(String(5))
    structure: Mapped[str] = mapped_column(Text)
    explanation_uz: Mapped[str] = mapped_column(Text)
    example_1: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    example_2: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    task_type: Mapped[str] = mapped_column(
        String(20), default="task2"
    )
    is_premium: Mapped[bool] = mapped_column(Boolean, default=True)
    order_num: Mapped[int] = mapped_column(default=0)


class SpeakingQuestion(Base):
    __tablename__ = "speaking_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    part: Mapped[int] = mapped_column(Integer)
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id"), nullable=True
    )
    question: Mapped[str] = mapped_column(Text)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    order_num: Mapped[int] = mapped_column(default=0)

    answers = relationship(
        "SpeakingAnswer", back_populates="question"
    )


class SpeakingAnswer(Base):
    __tablename__ = "speaking_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("speaking_questions.id")
    )
    band_level: Mapped[str] = mapped_column(String(5))
    answer_text: Mapped[str] = mapped_column(Text)
    highlighted: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    vocab_list: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )
    tips: Mapped[list | None] = mapped_column(JSON, nullable=True)

    question = relationship(
        "SpeakingQuestion", back_populates="answers"
    )


class MockExam(Base):
    __tablename__ = "mock_exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_type: Mapped[str] = mapped_column(
        String(10), default="task2"
    )
    question: Mapped[str] = mapped_column(Text)
    user_text: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    ai_feedback: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    ai_band: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    time_limit_sec: Mapped[int] = mapped_column(default=2400)
    time_spent_sec: Mapped[int | None] = mapped_column(
        nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )
