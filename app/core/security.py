"""
Telegram Mini App autentifikatsiyasi.

Frontend Telegram WebApp SDK orqali `window.Telegram.WebApp.initData` qatorini
oladi va har bir so'rovda `X-Telegram-Init-Data` header'i orqali backendga yuboradi.
Backend shu qatorni bot tokeni yordamida HMAC-SHA256 bilan tekshiradi — soxta
telegram_id yuborib bo'lmaydi, chunki imzo faqat Telegram serveri tomonidan
to'g'ri generatsiya qilinadi.

Hujjat: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

import jwt
from fastapi import Header, HTTPException, status

from app.core.config import settings

# initData necha soniya "yashaydi" (soxtalashtirib qayta yuborishning oldini olish)
MAX_INIT_DATA_AGE_SECONDS = 24 * 60 * 60  # 24 soat


def _check_telegram_signature(init_data: str) -> dict:
    """initData qatorini tekshiradi va ichidagi user ma'lumotini qaytaradi."""
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "init_data noto'g'ri formatda")

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "hash topilmadi")

    # auth_date muddati o'tganmi tekshirish
    auth_date = parsed.get("auth_date")
    if auth_date and (time.time() - int(auth_date)) > MAX_INIT_DATA_AGE_SECONDS:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessiya muddati tugagan")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=settings.BOT_TOKEN.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Imzo mos kelmadi")

    user_raw = parsed.get("user")
    if not user_raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user ma'lumoti topilmadi")

    return json.loads(user_raw)


async def get_current_telegram_id(
    x_telegram_init_data: str | None = Header(default=None),
) -> int:
    """
    FastAPI dependency: joriy foydalanuvchining tasdiqlangan telegram_id'sini qaytaradi.
    Development muhitida header bo'lmasa, xato bermaydi (localhost'da test qilish oson bo'lishi uchun),
    lekin productionda header MAJBURIY.
    """
    if not x_telegram_init_data:
        if settings.is_production:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "X-Telegram-Init-Data header talab qilinadi",
            )
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "X-Telegram-Init-Data header yo'q (dev muhitida ham majburiy qildik, "
            "frontend Telegram.WebApp.initData ni yuborishi kerak)",
        )

    user = _check_telegram_signature(x_telegram_init_data)
    return int(user["id"])


def ensure_owner(path_telegram_id: int, authenticated_telegram_id: int) -> None:
    """URL'dagi telegram_id bilan tasdiqlangan foydalanuvchi bir xilligini tekshiradi."""
    if path_telegram_id != authenticated_telegram_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Boshqa foydalanuvchining ma'lumotiga ruxsat yo'q",
        )


def is_trusted_bot(x_bot_secret: str | None) -> bool:
    """
    Telegram bot (aiogram) backend'ga server-to-server so'rov yuborganda
    Mini App initData'ga ega bo'lmaydi (u foydalanuvchi brauzerida ishlamaydi).
    Shuning uchun bot BOT_TOKEN'ni maxfiy header sifatida yuboradi -
    faqat bizning botimiz shu qiymatni biladi.
    """
    return bool(x_bot_secret) and hmac.compare_digest(x_bot_secret, settings.BOT_TOKEN)


def verify_owner_or_bot(
    path_telegram_id: int,
    x_telegram_init_data: str | None,
    x_bot_secret: str | None,
    authorization: str | None = None,
) -> None:
    """
    Uchta ishonchli manbadan birini talab qiladi:
    1) Bot o'zining maxfiy tokeni bilan chaqirsa (X-Bot-Secret), YOKI
    2) Telegram Mini App foydalanuvchisi o'zining haqiqiy initData'si bilan
       chaqirsa va path'dagi telegram_id unga tegishli bo'lsa, YOKI
    3) Web foydalanuvchi JWT bilan chaqirsa (Authorization: Bearer <token>)
       va token ichidagi telegram_id path'dagiga mos kelsa.
    Uchtasi ham yo'q/mos kelmasa -> 401/403.
    """
    if is_trusted_bot(x_bot_secret):
        return

    jwt_telegram_id = get_bearer_telegram_id(authorization)
    if jwt_telegram_id is not None:
        ensure_owner(path_telegram_id, jwt_telegram_id)
        return

    if not x_telegram_init_data:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Autentifikatsiya kerak: Authorization, X-Telegram-Init-Data yoki X-Bot-Secret header'i yo'q",
        )

    user = _check_telegram_signature(x_telegram_init_data)
    ensure_owner(path_telegram_id, int(user["id"]))


# ─── WEB AUTH (email/parol + JWT) ──────────────────────────
# Bot va Mini App uchun yuqoridagi Telegram-signature usuli qoladi.
# Web (brauzer, Telegram'siz) foydalanuvchilar uchun esa oddiy email/parol +
# JWT token ishlatiladi. Token ichida shu userning (sinthetik) telegram_id'si
# saqlanadi, shu tufayli qolgan barcha endpointlar o'zgarishsiz ishlaydi.
ACCESS_TOKEN_EXPIRE_DAYS = 30
PBKDF2_ITERATIONS = 260_000  # OWASP 2023+ tavsiyasi


def hash_password(password: str) -> str:
    """PBKDF2-HMAC-SHA256 bilan parolni xeshlaydi. Saqlash formati: 'salt$hash' (hex)."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Parolni saqlangan xesh bilan doim bir xil vaqtda solishtiradi (timing-attack'dan himoya)."""
    try:
        salt, hex_digest = password_hash.split("$", 1)
    except (ValueError, AttributeError):
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(digest.hex(), hex_digest)


def create_access_token(telegram_id: int) -> str:
    payload = {
        "telegram_id": telegram_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> int | None:
    """Token yaroqli bo'lsa ichidagi telegram_id'ni, aks holda None qaytaradi."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return int(payload["telegram_id"])
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        return None


def get_bearer_telegram_id(authorization: str | None) -> int | None:
    """'Authorization: Bearer <token>' headerini tahlil qiladi. Yo'q/yaroqsiz -> None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return decode_access_token(authorization[len("Bearer "):])


async def get_current_web_user_id(
    authorization: str | None = Header(default=None),
) -> int:
    """FastAPI dependency — /auth/me kabi faqat-JWT endpointlar uchun. Token
    yo'q/yaroqsiz bo'lsa 401 qaytaradi (boshqa auth usullarisiz)."""
    telegram_id = get_bearer_telegram_id(authorization)
    if telegram_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tizimga kirish talab qilinadi")
    return telegram_id
