import asyncio
import httpx
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://develop-uz-api.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Asosiy menyu
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Essays"),
            KeyboardButton(text="🧠 Vocabulary"),
        ],
        [
            KeyboardButton(text="🃏 Flashcard"),
            KeyboardButton(text="📊 Statistika"),
        ],
        [
            KeyboardButton(text="🌐 Saytga o'tish"),
            KeyboardButton(text="💎 Premium"),
        ],
    ],
    resize_keyboard=True
)

# Ebbinghaus Forgetting Curve intervallari (daqiqada)
FORGETTING_CURVE = [
    20,           # 20 daqiqa
    60,           # 1 soat
    9 * 60,       # 9 soat
    24 * 60,      # 1 kun
    2 * 24 * 60,  # 2 kun
    6 * 24 * 60,  # 6 kun
    31 * 24 * 60  # 31 kun
]

# Foydalanuvchi so'z eslatma jadvalini saqlash (xotirada)
# Production da Redis ga ko'chirish kerak
user_reminders: dict = {}  # {telegram_id: [{word, interval_idx, next_remind_at}]}


def schedule_word_reminder(telegram_id: int, word: str, translation: str):
    """So'zni Ebbinghaus jadvaliga qo'shish"""
    if telegram_id not in user_reminders:
        user_reminders[telegram_id] = []

    # Eski eslatmani o'chirish (agar mavjud bo'lsa)
    user_reminders[telegram_id] = [
        r for r in user_reminders[telegram_id] if r['word'] != word
    ]

    # Yangi eslatma qo'shish
    user_reminders[telegram_id].append({
        'word': word,
        'translation': translation,
        'interval_idx': 0,
        'next_remind_at': datetime.now() + timedelta(minutes=FORGETTING_CURVE[0])
    })


async def send_reminder(telegram_id: int, word: str, translation: str, interval_idx: int):
    """Eslatma xabar yuborish"""
    intervals = ['20 daqiqa', '1 soat', '9 soat', '1 kun', '2 kun', '6 kun', '31 kun']
    current = intervals[interval_idx] if interval_idx < len(intervals) else '31 kun'
    remaining = len(intervals) - interval_idx - 1

    text = (
        f"🔔 *Takrorlash vaqti!*\n\n"
        f"📌 *{word}*\n"
        f"🇺🇿 {translation}\n\n"
        f"⏱ Bu *{current}* ichidagi takrorlash\n"
        f"📊 Yana {remaining} ta takrorlash qoldi\n\n"
        f"So'zni esladingizmi?"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"✅ Ha, esladim - {word}"),
                KeyboardButton(text=f"❌ Yo'q, unutdim - {word}"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    try:
        await bot.send_message(
            telegram_id,
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Eslatma yuborishda xato: {e}")


async def reminder_loop():
    """Har daqiqada eslatmalarni tekshirish"""
    while True:
        now = datetime.now()
        for telegram_id, reminders in list(user_reminders.items()):
            for reminder in list(reminders):
                if now >= reminder['next_remind_at']:
                    await send_reminder(
                        telegram_id,
                        reminder['word'],
                        reminder['translation'],
                        reminder['interval_idx']
                    )
                    # Keyingi intervalga o'tish
                    next_idx = reminder['interval_idx'] + 1
                    if next_idx < len(FORGETTING_CURVE):
                        reminder['interval_idx'] = next_idx
                        reminder['next_remind_at'] = now + timedelta(
                            minutes=FORGETTING_CURVE[next_idx]
                        )
                    else:
                        # Barcha intervallar tugadi — o'chirish
                        reminders.remove(reminder)

        await asyncio.sleep(60)  # Har 60 soniyada tekshir


# ─── HANDLERS ─────────────────────────────────────────────

@dp.message(CommandStart())
async def start(message: types.Message):
    user = message.from_user

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{API_URL}/users/",
                json={
                    "telegram_id": user.id,
                    "name": user.full_name,
                    "username": user.username,
                    "band_level": "B2"
                },
                timeout=5.0
            )
        except Exception as e:
            print(f"API xato: {e}")

    await message.answer(
        f"🎯 *Xush kelibsiz, {user.first_name}!*\n\n"
        f"*Develop UZ* — IELTS Writing va Vocabulary uchun yagona platforma\n\n"
        f"✅ 1000+ Band 6-9 essay\n"
        f"✅ 10,000+ CEFR Vocabulary\n"
        f"✅ AI Essay Tahlil\n"
        f"✅ Ebbinghaus Forgetting Curve eslatmalar\n\n"
        f"Quyidagi menyudan boshlang! 👇",
        reply_markup=MAIN_MENU,
        parse_mode="Markdown"
    )


@dp.message(Command("stats"))
@dp.message(F.text == "📊 Statistika")
async def stats(message: types.Message):
    user = message.from_user

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"{API_URL}/users/{user.id}/stats",
                timeout=5.0
            )
            data = res.json()
        except Exception:
            await message.answer("❌ Server bilan bog'lanishda xato")
            return

    reminders_count = len(user_reminders.get(user.id, []))

    await message.answer(
        f"📊 *Sizning statistikangiz:*\n\n"
        f"👤 Ism: {data.get('name', '—')}\n"
        f"⭐ XP: {data.get('xp_points', 0)}\n"
        f"🔥 Streak: {data.get('streak_days', 0)} kun\n"
        f"📈 Daraja: {data.get('band_level', 'B2')}\n"
        f"💎 Obuna: {data.get('subscription_type', 'free')}\n"
        f"🔔 Kutilayotgan eslatmalar: {reminders_count} ta so'z",
        parse_mode="Markdown"
    )


@dp.message(F.text == "📝 Essays")
async def essays(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/essays/?limit=5", timeout=5.0)
            data = res.json()
            essays_list = data.get('essays', [])
        except Exception:
            await message.answer("❌ Server bilan bog'lanishda xato")
            return

    if not essays_list:
        await message.answer("📝 Hozircha essay yo'q")
        return

    text = "📝 *So'nggi essaylar:*\n\n"
    for essay in essays_list:
        text += (
            f"• *{essay['title'][:50]}...*\n"
            f"  Band: {essay['band_score']} | {essay['question_type']} | {essay['word_count']} so'z\n"
            f"  👉 /essay_{essay['id']}\n\n"
        )
    text += "🌐 To'liq ko'rish uchun saytga o'ting"

    await message.answer(text, parse_mode="Markdown")


@dp.message(F.text == "🧠 Vocabulary")
async def vocabulary(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/vocabulary/?limit=5", timeout=5.0)
            data = res.json()
            words = data.get('words', [])
        except Exception:
            await message.answer("❌ Server bilan bog'lanishda xato")
            return

    if not words:
        await message.answer("🧠 Hozircha so'z yo'q")
        return

    text = "🧠 *Bugungi vocabulary:*\n\n"
    for word in words:
        text += (
            f"📌 *{word['word']}* — {word['cefr_level']}\n"
            f"🇺🇿 {word['translation_uz']}\n"
        )
        if word.get('example_1'):
            text += f"💬 _{word['example_1'][:80]}..._\n"
        text += "\n"

    await message.answer(text, parse_mode="Markdown")


@dp.message(F.text == "🃏 Flashcard")
async def flashcard(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/vocabulary/?limit=1", timeout=5.0)
            data = res.json()
            words = data.get('words', [])
        except Exception:
            await message.answer("❌ Server bilan bog'lanishda xato")
            return

    if not words:
        await message.answer("🧠 So'z topilmadi")
        return

    word = words[0]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Bildim"),
                KeyboardButton(text="❌ Bilmadim"),
            ],
            [KeyboardButton(text="🏠 Bosh menyu")],
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"🃏 *Flashcard*\n\n"
        f"📌 So'z: *{word['word']}*\n"
        f"📊 Daraja: {word['cefr_level']}\n\n"
        f"Tarjimasini bilasizmi?\n\n"
        f"||🇺🇿 {word['translation_uz']}||\n"
        f"_{word.get('example_1', '')}_",
        reply_markup=keyboard,
        parse_mode="MarkdownV2"
    )

    # Ebbinghaus eslatmasiga qo'shish
    schedule_word_reminder(
        message.from_user.id,
        word['word'],
        word['translation_uz']
    )


@dp.message(F.text == "✅ Bildim")
async def correct(message: types.Message):
    await message.answer(
        "🎉 Zo'r! +10 XP\n\n"
        "🔔 Bu so'z Ebbinghaus jadvaliga qo'shildi.\n"
        "20 daqiqadan keyin takrorlash eslatmasi keladi.",
        reply_markup=MAIN_MENU
    )


@dp.message(F.text == "❌ Bilmadim")
async def wrong(message: types.Message):
    await message.answer(
        "💪 Xavotir olma! Takrorlash yordam beradi.\n\n"
        "🔔 Bu so'z eslatma jadvaliga qo'shildi.",
        reply_markup=MAIN_MENU
    )


@dp.message(F.text == "🌐 Saytga o'tish")
async def website(message: types.Message):
    await message.answer(
        "🌐 *Develop UZ — To'liq platforma*\n\n"
        "Saytda quyidagilar mavjud:\n"
        "✅ 1000+ essay (3 oynali ko'rinish)\n"
        "✅ 10,000+ vocabulary (word family bilan)\n"
        "✅ Speaking Part 1, 2, 3\n"
        "✅ AI Essay Tahlil\n"
        "✅ Mock Imtihon\n"
        "✅ Grammar Strukturalar\n\n"
        "👉 developuz.com",
        parse_mode="Markdown"
    )


@dp.message(F.text == "💎 Premium")
async def premium(message: types.Message):
    await message.answer(
        "💎 *Premium rejalar:*\n\n"
        "🥈 *Pro* — $8/oy\n"
        "• 500+ essay\n"
        "• 5,000+ vocabulary\n"
        "• Speaking barchasi\n"
        "• Grammar asoslari\n\n"
        "🥇 *Premium* — $15/oy\n"
        "• Hammasi + AI Tahlil\n"
        "• Mock Imtihon\n"
        "• Idea Generator\n"
        "• Sample Collector\n"
        "• 10,000+ vocabulary\n\n"
        "Tez orada to'lov tizimi ulanadi! 🔜",
        parse_mode="Markdown"
    )


@dp.message(F.text == "🏠 Bosh menyu")
async def home(message: types.Message):
    await message.answer(
        "🏠 Bosh menyu",
        reply_markup=MAIN_MENU
    )


@dp.message(lambda m: m.text and m.text.startswith("/essay_"))
async def show_essay(message: types.Message):
    essay_id = message.text.replace("/essay_", "")

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/essays/{essay_id}", timeout=5.0)
            essay = res.json()
        except Exception:
            await message.answer("❌ Essay topilmadi")
            return

    text = (
        f"📝 *{essay['title']}*\n\n"
        f"🎯 Band: {essay['band_score']}\n"
        f"📌 Tur: {essay['question_type']}\n"
        f"📖 So'zlar: {essay['word_count']}\n\n"
    )

    content = essay.get('content', '')
    if len(content) > 3000:
        text += content[:3000] + "...\n\n_[To'liq essay saytda mavjud]_"
    else:
        text += content

    await message.answer(text, parse_mode="Markdown")


@dp.message(Command("remind"))
async def show_reminders(message: types.Message):
    reminders = user_reminders.get(message.from_user.id, [])

    if not reminders:
        await message.answer(
            "🔔 Hozircha eslatma yo'q.\n\n"
            "Flashcard o'ynab so'z o'rganing — "
            "avtomatik eslatma jadvaliga qo'shiladi!"
        )
        return

    text = f"🔔 *Sizning eslatmalaringiz ({len(reminders)} ta):*\n\n"
    for r in reminders:
        diff = r['next_remind_at'] - datetime.now()
        mins = int(diff.total_seconds() / 60)
        if mins < 0:
            time_str = "hozir"
        elif mins < 60:
            time_str = f"{mins} daqiqada"
        elif mins < 1440:
            time_str = f"{mins // 60} soatda"
        else:
            time_str = f"{mins // 1440} kunda"

        intervals = ['20 daq', '1 soat', '9 soat', '1 kun', '2 kun', '6 kun', '31 kun']
        current = intervals[r['interval_idx']] if r['interval_idx'] < len(intervals) else '31 kun'

        text += (
            f"📌 *{r['word']}* — {r['translation']}\n"
            f"   ⏱ {time_str} | {current} intervali\n\n"
        )

    await message.answer(text, parse_mode="Markdown")


async def main():
    print("🤖 Develop UZ Bot ishga tushdi!")
    print(f"📡 API: {API_URL}")

    # Forgetting Curve loop ni parallel ishga tushirish
    asyncio.create_task(reminder_loop())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())