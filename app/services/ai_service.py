import json
from groq import Groq
import anthropic

from app.core.config import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY)
claude_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def groq_complete(prompt: str, system: str = "", max_tokens: int = 2000) -> str:
    """Groq - tez va arzon"""
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq xato: {e}")
        return None


def claude_complete(prompt: str, system: str = "", max_tokens: int = 2000) -> str:
    """Claude - kuchli va aniq"""
    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system if system else "You are an expert IELTS examiner.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude xato: {e}")
        return None


def ai_complete(prompt: str, system: str = "", use_claude: bool = False, max_tokens: int = 2000) -> str:
    """
    Smart router:
    - use_claude=True  → Claude (band scoring, chuqur tahlil)
    - use_claude=False → Groq (grammar check, highlights, idea gen)
    Groq ishlamasa → Claude ga fallback
    """
    if use_claude:
        result = claude_complete(prompt, system, max_tokens)
        if not result:
            result = groq_complete(prompt, system, max_tokens)
    else:
        result = groq_complete(prompt, system, max_tokens)
        if not result:
            result = claude_complete(prompt, system, max_tokens)
    return result


def _parse_json_response(result: str | None, fallback):
    if not result:
        return fallback
    try:
        clean = result.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return fallback


# ─── ESSAY TAHLIL (Claude) ────────────────────────────────
def analyze_essay(essay_text: str) -> dict:
    system = """Sen professional IELTS examiner sifatida ishlaysan.
Faqat JSON formatida javob ber, boshqa hech narsa yozma."""

    prompt = f"""Quyidagi IELTS Writing Task 2 essayni tahlil qil:

{essay_text}

JSON formatida qaytargin:
{{
  "overall_band": 7.5,
  "task_achievement": 7.0,
  "coherence_cohesion": 8.0,
  "lexical_resource": 7.5,
  "grammatical_range": 7.5,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "suggestions": ["...", "..."],
  "c1_c2_words": ["unprecedented", "exacerbate"],
  "collocations": ["take a toll on"],
  "idioms": ["give a voice to"]
}}"""

    result = ai_complete(prompt, system, use_claude=True, max_tokens=1500)
    return _parse_json_response(result, {"overall_band": 0, "error": "Tahlil qilishda xato"})


# ─── GRAMMAR CHECK (Groq) ─────────────────────────────────
def check_grammar(text: str) -> list:
    system = """Sen IELTS grammatika tekshiruvchisisina.
Faqat JSON array formatida javob ber."""

    prompt = f"""Quyidagi matnda grammatika xatolarini top:

{text}

JSON array formatida qaytargin:
[
  {{
    "wrong": "have became",
    "correct": "has become",
    "explanation_uz": "Present perfect: has/have + V3",
    "start": 45,
    "end": 56
  }}
]

Xato yo'q bo'lsa: []"""

    result = ai_complete(prompt, system, use_claude=False, max_tokens=1000)
    return _parse_json_response(result, [])


# ─── IDEA GENERATOR (Groq) ────────────────────────────────
def generate_ideas(topic: str) -> dict:
    system = """Sen IELTS Writing Task 2 mutaxassisisina.
Faqat JSON formatida javob ber."""

    prompt = f"""IELTS Writing Task 2 mavzusi: "{topic}"

JSON formatida idea generation qil:
{{
  "pro_arguments": [
    {{"argument": "...", "example": "...", "vocabulary": ["..."]}}
  ],
  "con_arguments": [
    {{"argument": "...", "example": "...", "vocabulary": ["..."]}}
  ],
  "key_vocabulary": [
    {{"word": "...", "translation": "...", "level": "C1"}}
  ],
  "thesis_statement": "...",
  "outline": {{
    "introduction": "...",
    "body_1": "...",
    "body_2": "...",
    "conclusion": "..."
  }}
}}"""

    result = ai_complete(prompt, system, use_claude=False, max_tokens=2000)
    return _parse_json_response(result, {"error": "Idea generatsiyada xato"})


# ─── HIGHLIGHT DETECTOR (Groq) ────────────────────────────
def detect_highlights(text: str) -> list:
    system = """Sen IELTS vocabulary mutaxassisisina.
Faqat JSON array formatida javob ber."""

    prompt = f"""Quyidagi matndan IELTS uchun foydali narsalarni ajrat:

{text[:2000]}

JSON array:
[
  {{
    "text": "exacerbate",
    "type": "c1_vocab",
    "start": 45,
    "end": 55,
    "explanation_uz": "yomonlashtirmoq",
    "how_to_use": "exacerbate + noun"
  }}
]

type qiymatlari: collocation | idiom | c1_vocab | c2_vocab"""

    result = ai_complete(prompt, system, use_claude=False, max_tokens=1500)
    return _parse_json_response(result, [])


# ─── WRITING FEEDBACK (Claude) ────────────────────────────
def get_writing_feedback(essay: str, task_question: str = "") -> dict:
    system = "Sen professional IELTS examiner sifatida ishlaysan. JSON formatida javob ber."

    prompt = f"""IELTS Writing Task 2 essayga feedback ber:

Savol: {task_question if task_question else 'Berilmagan'}

Essay:
{essay}

JSON:
{{
  "band": 7.0,
  "feedback_uz": "Umumiy baholash o'zbek tilida...",
  "task_achievement_uz": "...",
  "grammar_issues": ["...", "..."],
  "good_phrases": ["...", "..."],
  "improve_suggestions": ["...", "..."]
}}"""

    result = ai_complete(prompt, system, use_claude=True, max_tokens=1500)
    return _parse_json_response(result, {"band": 0, "error": "Feedback olishda xato"})


# ─── SPEAKING: AUDIO TRANSKRIPSIYA (Groq Whisper) ─────────
def transcribe_audio(file_bytes: bytes, filename: str = "audio.webm") -> str | None:
    """Ovoz faylini matnga o'giradi. Groq'ning hosted Whisper modelidan foydalanadi —
    alohida API kalit yoki qo'shimcha kutubxona kerak emas (groq SDK ichida bor)."""
    try:
        result = groq_client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model="whisper-large-v3-turbo",
            language="en",
            response_format="json",
        )
        text = (result.text or "").strip()
        return text if text else None
    except Exception as e:
        print(f"Whisper transkripsiya xato: {e}")
        return None


# ─── SPEAKING: AI BAHOLASH (Claude) ───────────────────────
def evaluate_speaking(
    transcript: str, question: str, part: int = 2, duration_sec: int | None = None
) -> dict:
    """Transkript asosida IELTS Speaking javobini baholaydi.
    Diqqat: audio faylning o'zi emas, faqat matnga o'girilgan versiyasi tahlil qilinadi —
    shuning uchun talaffuz (pronunciation) alohida band sifatida berilmaydi;
    foydalanuvchi buni o'z yozuvini eshitib o'zi baholashi tavsiya etiladi."""

    word_count = len(transcript.split())
    wpm_line = ""
    if duration_sec and duration_sec > 0:
        wpm = round(word_count / (duration_sec / 60))
        wpm_line = f"\nGapirish tezligi: ~{wpm} so'z/daqiqa (davomiylik: {duration_sec} soniya)."

    part_context = {
        1: "Part 1 — oddiy shaxsiy savollarga qisqa, tabiiy javob kutiladi.",
        2: "Part 2 — 1-2 daqiqalik uzluksiz monolog (cue card asosida) kutiladi.",
        3: "Part 3 — mavzu bo'yicha chuqurroq, fikr-mulohazali muhokama kutiladi.",
    }.get(part, "Speaking javobi.")

    system = """Sen professional IELTS Speaking examinerisan.
Faqat JSON formatida javob ber, boshqa hech narsa yozma.
Baholashda faqat berilgan transkriptga tayan — talaffuz haqida hukm chiqarma,
chunki senga audio emas, faqat matn berilgan."""

    prompt = f"""{part_context}

Savol: {question}

Nomzodning javobi (ovozdan avtomatik matnga o'girilgan, shuning uchun "um", "uh" kabi
so'zlar yoki notekis jumlalar bo'lishi mumkin — bularni fluency belgisi sifatida hisobga ol):

\"\"\"{transcript}\"\"\"
{wpm_line}
So'zlar soni: {word_count}

Quyidagi JSON formatida baho ber (band'lar 0-9 oralig'ida, 0.5 qadam bilan):
{{
  "band": 6.5,
  "fluency_coherence": 6.5,
  "lexical_resource": 6.0,
  "grammatical_range": 7.0,
  "feedback_uz": "Umumiy baholash o'zbek tilida, 2-3 jumla",
  "strengths": ["...", "..."],
  "improve_suggestions": ["...", "..."],
  "filler_words": ["um", "like"],
  "good_phrases": ["...", "..."],
  "grammar_issues": ["...", "..."]
}}"""

    result = ai_complete(prompt, system, use_claude=True, max_tokens=1200)
    data = _parse_json_response(
        result, {"band": 0, "error": "Baholashda xato yuz berdi"}
    )
    if isinstance(data, dict) and "error" not in data:
        data["word_count"] = word_count
        if duration_sec:
            data["duration_sec"] = duration_sec
    return data


def highlight_sample(text: str) -> list:
    """Sample collector uchun — tashqi matndan highlights ajratish"""
    system = "Sen IELTS vocabulary va collocation mutaxassisisina. Faqat JSON array formatida javob ber."
    prompt = f"""Quyidagi matndan IELTS Writing uchun eng foydali:
1. High-level collocations
2. Idiomatic expressions
3. C1/C2 vocabulary

Ajrat va JSON array qaytargin:
[
  {{
    "text": "a growing body of evidence",
    "type": "collocation",
    "explanation_uz": "ko'payib borayotgan dalillar",
    "how_to_use": "a growing body of + noun (evidence, research, literature)"
  }}
]

Matn:
{text[:3000]}

type: collocation | idiom | c1_vocab | c2_vocab"""
    result = ai_complete(prompt, system, use_claude=False, max_tokens=2000)
    return _parse_json_response(result, [])
