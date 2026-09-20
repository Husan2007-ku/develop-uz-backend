import json
from groq import Groq
import anthropic
from openai import OpenAI
from google import genai
from google.genai import types as genai_types

from app.core.config import settings

# Har bir provider uchun client faqat kalit mavjud bo'lsa yaratiladi.
# Kalit bo'sh bo'lsa client None qoladi — mos _complete funksiya buni
# ko'rib, darhol None qaytaradi va zanjir keyingi providerga o'tadi.
# Shu tufayli OPENAI_API_KEY yoki GEMINI_API_KEY sozlanmagan bo'lsa ham
# ilova xatosiz ishga tushadi (config.py'da ular ixtiyoriy).
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
claude_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None


def groq_complete(prompt: str, system: str = "", max_tokens: int = 2000) -> str | None:
    """Groq - tez va arzon"""
    if not groq_client:
        return None
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


def claude_complete(prompt: str, system: str = "", max_tokens: int = 2000) -> str | None:
    """Claude - kuchli va aniq"""
    if not claude_client:
        return None
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


def openai_complete(prompt: str, system: str = "", max_tokens: int = 2000, model: str = "gpt-4o-mini") -> str | None:
    """OpenAI - fallback provider"""
    if not openai_client:
        return None
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI xato: {e}")
        return None


def gemini_complete(prompt: str, system: str = "", max_tokens: int = 2000, model: str = "gemini-1.5-flash") -> str | None:
    """Gemini - fallback provider"""
    if not gemini_client:
        return None
    try:
        response = gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system if system else None,
                max_output_tokens=max_tokens,
                temperature=0.3,
            ),
        )
        return response.text
    except Exception as e:
        print(f"Gemini xato: {e}")
        return None


# ─── 4 PROVIDERLI FALLBACK ZANJIRI ─────────────────────────
# "smart" tier (band scoring, chuqur tahlil) — eng aniq javob birinchi:
#   Claude → OpenAI (gpt-4o) → Gemini (pro) → Groq
# "fast" tier (grammar, idea gen, highlight) — eng tez/arzon birinchi:
#   Groq → OpenAI (mini) → Gemini (flash) → Claude
# Kalit sozlanmagan yoki chaqiruv xato bergan provider avtomatik
# o'tkazib yuboriladi — barchasi ishlamasa None qaytadi.
def _try_chain(chain: list, prompt: str, system: str, max_tokens: int) -> str | None:
    for complete_fn in chain:
        result = complete_fn(prompt, system, max_tokens)
        if result:
            return result
    return None


def ai_complete(prompt: str, system: str = "", use_claude: bool = False, max_tokens: int = 2000) -> str | None:
    """
    Smart router:
    - use_claude=True  → "smart" zanjir (Claude birinchi)
    - use_claude=False → "fast" zanjir (Groq birinchi)
    """
    if use_claude:
        chain = [
            claude_complete,
            lambda p, s, m: openai_complete(p, s, m, model="gpt-4o"),
            lambda p, s, m: gemini_complete(p, s, m, model="gemini-1.5-pro"),
            groq_complete,
        ]
    else:
        chain = [
            groq_complete,
            lambda p, s, m: openai_complete(p, s, m, model="gpt-4o-mini"),
            lambda p, s, m: gemini_complete(p, s, m, model="gemini-1.5-flash"),
            claude_complete,
        ]
    return _try_chain(chain, prompt, system, max_tokens)


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
