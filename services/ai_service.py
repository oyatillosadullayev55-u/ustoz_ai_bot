"""AI Ustoz xizmati: OpenAI-mos provayder va lokal dars bazasi zaxirasi."""

from __future__ import annotations

import html
import logging

import aiohttp

from config import get_settings
from database.content import (
    extract_tokens,
    get_subjects_with_counts,
    search_lessons,
)

logger = logging.getLogger(__name__)

LEVEL_NAMES = {
    "beginner": "boshlang'ich",
    "intermediate": "o'rta",
    "advanced": "yuqori",
}

SYSTEM_PROMPT = (
    "Siz UstozAI — o'zbek o'quvchilariga bilim beruvchi mehribon onlayn ustozsiz.\n"
    "Foydalanuvchining bilim darajasi: {level}.\n\n"
    "Javob qoidalari:\n"
    "- Har doim o'zbek tilida yozing.\n"
    "- Sodda, aniq va qisqa tushuntiring; odatda 1200 belgidan oshmang.\n"
    "- Mavzuni bosqichma-bosqich tushuntiring, kerak bo'lsa misol keltiring.\n"
    "- Kod kerak bo'lsa, qisqa va to'g'ri namuna bering.\n"
    "- HTML va Markdown belgilaridan foydalanmang, oddiy matn yozing.\n"
    "- Savol noaniq bo'lsa, aniqlashtiruvchi savol bering.\n"
    "- O'zingizni sun'iy intellekt modeli deb tanishtirmang; siz UstozAIsiz.\n"
    "- Xavfli yoki foydalanuvchini xafa qiluvchi kontent bermang."
)

FALLBACK_NOTE_DISABLED = (
    "ℹ️ AI kaliti hali sozlanmagan, shuning uchun javob dars bazasidan olindi."
)
FALLBACK_NOTE_ERROR = (
    "⚠️ AI xizmatida vaqtincha muammo bor, shuning uchun javob dars bazasidan olindi."
)


class AIServiceError(RuntimeError):
    """AI provayderi javob bera olmaganida ko'tariladi."""


def _excerpt(content: str, tokens: list[str], length: int = 600) -> str:
    lowered = content.lower()
    position = -1
    for token in tokens:
        position = lowered.find(token)
        if position >= 0:
            break

    if position < 0:
        snippet = content[:length]
    else:
        start = max(position - 150, 0)
        snippet = content[start : start + length]
        if start > 0:
            snippet = "..." + snippet
        if start + length < len(content):
            snippet += "..."

    return " ".join(snippet.split())


async def _fallback_reply(question: str, note: str) -> str:
    tokens = extract_tokens(question)
    lessons = await search_lessons(question, limit=2)

    if not lessons:
        subjects = await get_subjects_with_counts()
        subject_names = ", ".join(
            f"{subject['emoji']} {subject['name']}" for subject in subjects
        )
        return (
            "📚 <b>Dars bazasidan aniq javob topa olmadim.</b>\n\n"
            "Savolni aniqroq yozing yoki «📚 Darslar» bo'limidan kerakli "
            "mavzuni tanlang.\n\n"
            f"Mavjud fanlar: {html.escape(subject_names)}\n\n"
            f"{note}"
        )

    parts = ["📚 <b>Darslarimizdan mos javob</b>", ""]
    for lesson in lessons:
        parts.append(
            f"<b>{lesson['subject_emoji']} "
            f"{html.escape(lesson['subject_name'])} — "
            f"{html.escape(lesson['title'])}</b>"
        )
        parts.append(html.escape(_excerpt(lesson["content"], tokens)))
        parts.append("")

    parts.append("To'liq darsni «📚 Darslar» bo'limida o'qishingiz mumkin.")
    parts.append("")
    parts.append(note)
    return "\n".join(parts)


async def _call_provider(
    question: str, history: list[dict[str, str]], level: str
) -> str:
    settings = get_settings()
    level_name = LEVEL_NAMES.get(level, "boshlang'ich")
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(level=level_name),
        }
    ]
    for item in history:
        content = str(item.get("content", "")).strip()
        if not content:
            continue
        messages.append(
            {
                "role": "user" if item.get("role") == "user" else "assistant",
                "content": content[:1200],
            }
        )
    messages.append({"role": "user", "content": question})

    timeout = aiohttp.ClientTimeout(total=settings.ai_timeout)
    headers = {
        "Authorization": f"Bearer {settings.ai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.ai_model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": settings.ai_max_tokens,
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{settings.ai_base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                if response.status != 200:
                    logger.error(
                        "AI provayderi HTTP %s qaytardi.", response.status
                    )
                    raise AIServiceError(
                        f"AI provayderi HTTP {response.status} qaytardi."
                    )
                data = await response.json()
    except TimeoutError:
        logger.warning("AI provayderi javobi timeout bilan tugadi.")
        raise AIServiceError("AI provayderi javob bermadi.") from None
    except aiohttp.ClientError:
        logger.warning("AI provayderiga ulanib bo'lmadi.")
        raise AIServiceError("AI provayderiga ulanib bo'lmadi.") from None
    except ValueError:
        logger.warning("AI provayderi noto'g'ri JSON qaytardi.")
        raise AIServiceError("AI javobi o'qib bo'lmadi.") from None

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        logger.warning("AI provayderi javobi kutilgan formatda emas.")
        raise AIServiceError("AI javobi kutilgan formatda emas.") from None

    if not isinstance(content, str) or not content.strip():
        raise AIServiceError("AI bo'sh javob qaytardi.")

    return content.strip()


async def ask_tutor(
    question: str, history: list[dict[str, str]], level: str
) -> tuple[str, str]:
    """(javob matni, manba) qaytaradi. Manba: ai, lessons yoki plain."""
    settings = get_settings()

    if settings.ai_configured:
        try:
            answer = await _call_provider(question, history, level)
            return answer, "ai"
        except AIServiceError:
            logger.warning("AI javob bera olmadi; dars bazasi ishlatiladi.")
            return await _fallback_reply(question, FALLBACK_NOTE_ERROR), "lessons"

    return await _fallback_reply(question, FALLBACK_NOTE_DISABLED), "lessons"
