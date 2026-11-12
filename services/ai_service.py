"""AI Ustoz xizmati: OpenAI-mos provayder va lokal dars bazasi zaxirasi."""

from __future__ import annotations

import html
import logging
import time
from dataclasses import dataclass

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


PROVIDER_FAILURE_LIMIT = 3
PROVIDER_COOLDOWN_SECONDS = 120.0

_session: aiohttp.ClientSession | None = None


@dataclass(slots=True)
class ProviderGuard:
    """Ketma-ket xatolardan keyin provayderni vaqtincha chetlab o'tadi.

    Provayder ishlamay qolganda har bir savol timeout kutish o'rniga darhol
    dars bazasidan javob beriladi.
    """

    failure_limit: int = PROVIDER_FAILURE_LIMIT
    cooldown_seconds: float = PROVIDER_COOLDOWN_SECONDS
    failures: int = 0
    blocked_until: float = 0.0

    def available(self, now: float | None = None) -> bool:
        return (time.monotonic() if now is None else now) >= self.blocked_until

    def record_failure(self, now: float | None = None) -> None:
        self.failures += 1
        if self.failures >= self.failure_limit:
            current = time.monotonic() if now is None else now
            self.blocked_until = current + self.cooldown_seconds

    def record_success(self) -> None:
        self.failures = 0
        self.blocked_until = 0.0


_provider_guard = ProviderGuard()


def _get_session() -> aiohttp.ClientSession:
    """Bitta HTTP sessiyasini qayta ishlatadi (TLS handshake tejaladi)."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
        )
    return _session


async def close_ai_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
    _session = None


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


async def _fallback_reply(
    question: str,
    note: str,
    lesson_context: dict[str, str] | None = None,
) -> tuple[str, list[tuple[int, str]]]:
    tokens = extract_tokens(question)

    if lesson_context:
        title = lesson_context.get("title", "")
        subject = lesson_context.get("subject", "")
        content = lesson_context.get("content", "") or lesson_context.get(
            "summary", ""
        )
        excerpt = _excerpt(content, tokens, length=900)
        lesson_id = lesson_context.get("lesson_id")
        related = (
            [(int(lesson_id), str(title))]
            if isinstance(lesson_id, int) and lesson_id > 0
            else []
        )
        text = (
            "📚 <b>Shu darsdan tushuntirish</b>\n\n"
            f"{html.escape(subject)} — "
            f"<b>{html.escape(title)}</b>\n\n"
            f"{html.escape(excerpt)}\n\n"
            "💡 Savolingizni darsdagi tushunarsiz joyga qaratib yozsangiz, "
            "yanada aniqroq yordam beraman.\n\n"
            f"{note}"
        )
        return text, related

    lessons = await search_lessons(question, limit=2)

    if not lessons:
        subjects = await get_subjects_with_counts()
        subject_names = ", ".join(
            f"{subject['emoji']} {subject['name']}" for subject in subjects
        )
        text = (
            "📚 <b>Dars bazasidan aniq javob topa olmadim.</b>\n\n"
            "Savolni aniqroq yozing yoki «📚 Darslar» bo'limidan kerakli "
            "mavzuni tanlang.\n\n"
            f"Mavjud fanlar: {html.escape(subject_names)}\n\n"
            f"{note}"
        )
        return text, []

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
    related = [(int(lesson["id"]), str(lesson["title"])) for lesson in lessons]
    return "\n".join(parts), related


LESSON_CONTEXT_PROMPT = (
    "Foydalanuvchi hozir quyidagi darsni o'qimoqda:\n"
    "Fan: {subject}\n"
    "Dars: {title}\n"
    "Qisqa mazmun: {summary}\n\n"
    "Dars matni (qisqartirilgan):\n{content}\n\n"
    "Javobni shu darsga bog'lab bering: tushunarsiz joyni sodda tilda qayta "
    "tushuntiring, hayotiy misol keltiring va kerak bo'lsa qisqa mini mashq "
    "bering. Darsda yo'q ma'lumot kerak bo'lsa, uni alohida ta'kidlang. "
    "Javob 1200 belgidan oshmasin."
)


async def _call_provider(
    question: str,
    history: list[dict[str, str]],
    level: str,
    lesson_context: dict[str, str] | None = None,
) -> str:
    settings = get_settings()
    level_name = LEVEL_NAMES.get(level, "boshlang'ich")
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(level=level_name),
        }
    ]
    if lesson_context:
        messages.append(
            {
                "role": "system",
                "content": LESSON_CONTEXT_PROMPT.format(
                    subject=lesson_context.get("subject", ""),
                    title=lesson_context.get("title", ""),
                    summary=lesson_context.get("summary", ""),
                    content=lesson_context.get("content", "")[:2500],
                ),
            }
        )
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
        async with _get_session().post(
            f"{settings.ai_base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
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
    question: str,
    history: list[dict[str, str]],
    level: str,
    lesson_context: dict[str, str] | None = None,
) -> tuple[str, str, list[tuple[int, str]]]:
    """(javob matni, manba, aloqador darslar) qaytaradi."""
    settings = get_settings()

    related: list[tuple[int, str]] = []
    if lesson_context:
        lesson_id = lesson_context.get("lesson_id")
        if isinstance(lesson_id, int) and lesson_id > 0:
            related = [(lesson_id, str(lesson_context.get("title", "")))]

    if settings.ai_configured:
        if not _provider_guard.available():
            logger.info(
                "AI provayderi cooldown rejimida; dars bazasi ishlatiladi."
            )
            text, related = await _fallback_reply(
                question, FALLBACK_NOTE_ERROR, lesson_context
            )
            return text, "lessons", related

        try:
            answer = await _call_provider(
                question, history, level, lesson_context
            )
        except AIServiceError:
            _provider_guard.record_failure()
            logger.warning("AI javob bera olmadi; dars bazasi ishlatiladi.")
            text, related = await _fallback_reply(
                question, FALLBACK_NOTE_ERROR, lesson_context
            )
            return text, "lessons", related

        _provider_guard.record_success()
        return answer, "ai", related

    text, related = await _fallback_reply(
        question, FALLBACK_NOTE_DISABLED, lesson_context
    )
    return text, "lessons", related
