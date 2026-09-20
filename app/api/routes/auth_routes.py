"""
Web autentifikatsiya — email/parol.

Telegram Mini App/bot userlari uchun autentifikatsiya `app/core/security.py`
dagi `X-Telegram-Init-Data` imzosi orqali ishlaydi (o'zgarishsiz qoladi).
Bu fayl esa Telegram'siz, oddiy brauzerdan keladigan foydalanuvchilar uchun.

Web orqali ro'yxatdan o'tgan userga ham "telegram_id" beriladi (lekin haqiqiy
Telegram ID emas — email'dan deterministik hosil qilingan, 900 mlrd+ oraliqdagi
sinthetik qiymat). Shu tufayli /essays/{id}/notes, /vocabulary/user/* kabi
mavjud endpointlarning birortasini o'zgartirish shart bo'lmadi — ular hamon
"telegram_id" bilan ishlaydi, faqat endi bu ID web user ham bo'lishi mumkin.
"""
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_web_user_id,
    hash_password,
    verify_password,
)
from app.models.models import User

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# Haqiqiy Telegram user ID'lari hozircha bundan ancha past (~10 xonagacha).
# Web userlarga shu oraliqdan tashqarida, lekin BigInteger'ga sig'adigan
# qiymat berish — ikki turdagi userning to'qnashib qolishining oldini oladi.
SYNTHETIC_ID_BASE = 900_000_000_000
SYNTHETIC_ID_RANGE = 100_000_000_000


def _synthetic_telegram_id(email: str) -> int:
    digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()
    return SYNTHETIC_ID_BASE + (int(digest, 16) % SYNTHETIC_ID_RANGE)


class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    telegram_id: int
    name: str
    email: str


@auth_router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    email = data.email.strip().lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu email bilan hisob allaqachon mavjud")

    user = User(
        telegram_id=_synthetic_telegram_id(email),
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password),
        auth_provider="web",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Amalda deyarli bo'lmaydi (sinthetik ID hash-asosli) — lekin
        # unique constraint to'qnashsa, foydalanuvchiga tushunarli xato beramiz.
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Ro'yxatdan o'tishda xato yuz berdi, qayta urinib ko'ring",
        )
    db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.telegram_id),
        telegram_id=user.telegram_id,
        name=user.name,
        email=user.email,
    )


@auth_router.post("/login", response_model=AuthResponse)
def login(data: LoginInput, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    # Vaqt hujumidan himoya: user topilmasa ham verify_password chaqiramiz
    # (aks holda "user yo'q" va "parol xato" javoblari orasidagi vaqt farqidan
    # email mavjudligini bilib olish mumkin bo'lardi).
    dummy_hash = "0" * 32 + "$" + "0" * 64
    password_ok = verify_password(data.password, user.password_hash if user else dummy_hash)

    if not user or not password_ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email yoki parol noto'g'ri")

    return AuthResponse(
        access_token=create_access_token(user.telegram_id),
        telegram_id=user.telegram_id,
        name=user.name,
        email=user.email,
    )


@auth_router.get("/me", response_model=AuthResponse)
def get_me(telegram_id: int = Depends(get_current_web_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foydalanuvchi topilmadi")

    return AuthResponse(
        access_token=create_access_token(user.telegram_id),
        telegram_id=user.telegram_id,
        name=user.name,
        email=user.email or "",
    )
