"""AI Ustoz rejimi: savol-javob, limitlar va suhbat tarixi."""

from __future__ import annotations

import html
import logging
import math
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import get_settings
from database.chat import add_message, get_ai_usage, get_history
from handlers.common import require_user
from keyboards.main_menu import (
    BTN_AI_EXIT,
    BTN_AI_TUTOR,
    MAIN_MENU_TEXTS,
    get_ai_mode_keyboard,
    get_main_menu_keyboard,
)
from services.ai_service import ask_tutor

router = Router(name="ai_tutor")
logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 1000
MAX_REPLY_LENGTH = 3900


class AITutorStates(StatesGroup):
    chatting = State()


def _truncate(text: str, limit: int = MAX_REPLY_LENGTH) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space > limit - 300:
        cut = cut[:space]
    return cut + "\n\n… (javob qisqartirildi)"


def _prepare_reply(text: str, source: str) -> str:
    if source == "ai":
        text = html.escape(text)
    return _truncate(text)


async def _leave_ai_mode(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "AI Ustoz rejimidan chiqdingiz. 🏠\n"
        "Kerakli bo'limni pastdagi menyudan tanlang.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(F.text == BTN_AI_TUTOR)
async def enter_ai_mode(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return

    settings = get_settings()
    if settings.ai_configured:
        mode_note = (
            "🧠 Savolingizga AI yordamida javob beraman. "
            "Savolni aniq va qisqa yozing."
        )
    else:
        mode_note = (
            "📚 Hozircha AI kaliti sozlanmagan. Savolingizga mavjud darslar "
            "asosida javob beraman."
        )

    await state.set_state(AITutorStates.chatting)
    await message.answer(
        "🧠 <b>AI Ustoz</b>\n\n"
        f"{mode_note}\n\n"
        f"⏱ Kunlik limit: <b>{settings.ai_daily_limit}</b> savol.\n"
        f"⏳ Savollar orasida kamida {settings.ai_min_interval} soniya.\n\n"
        "Chiqish uchun «⬅️ Chiqish» tugmasini bosing.",
        reply_markup=get_ai_mode_keyboard(),
    )


@router.message(AITutorStates.chatting, F.text, ~F.text.startswith("/"))
async def ai_chat(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return

    text = (message.text or "").strip()

    if text == BTN_AI_EXIT:
        await _leave_ai_mode(message, state)
        return

    if text in MAIN_MENU_TEXTS:
        await state.clear()
        await message.answer(
            "AI rejimidan chiqdingiz. Kerakli bo'limni qayta tanlang.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    user = await require_user(message)
    if user is None:
        await state.clear()
        return

    if len(text) < 2:
        await message.answer(
            "Savolingizni to'liqroq yozing — mavzu yoki masalani aniq ayting.",
            reply_markup=get_ai_mode_keyboard(),
        )
        return

    if len(text) > MAX_QUESTION_LENGTH:
        await message.answer(
            f"Savol juda uzun. Iltimos, {MAX_QUESTION_LENGTH} belgidan oshirmasdan "
            "qisqartirib yozing.",
            reply_markup=get_ai_mode_keyboard(),
        )
        return

    settings = get_settings()
    user_id = user["telegram_id"]
    usage_count, last_at = await get_ai_usage(user_id)

    if usage_count >= settings.ai_daily_limit:
        await message.answer(
            f"⏳ Kunlik AI limiti tugadi ({settings.ai_daily_limit} savol).\n"
            "Ertaga qayta urinib ko'ring yoki hozir «📚 Darslar» bo'limidan "
            "foydalaning.",
            reply_markup=get_ai_mode_keyboard(),
        )
        return

    if last_at and settings.ai_min_interval > 0:
        seconds_left = 0.0
        try:
            last_time = datetime.fromisoformat(last_at)
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - last_time).total_seconds()
            seconds_left = settings.ai_min_interval - elapsed
        except ValueError:
            seconds_left = 0.0

        if seconds_left > 0:
            await message.answer(
                f"⏳ Iltimos, {math.ceil(seconds_left)} soniya kutib, "
                "savolingizni qayta yozing.",
                reply_markup=get_ai_mode_keyboard(),
            )
            return

    history_rows = await get_history(user_id, settings.ai_history_limit)
    history = [
        {"role": row["role"], "content": row["message"]}
        for row in history_rows
    ]

    await add_message(user_id, "user", text)

    if message.bot is not None:
        try:
            await message.bot.send_chat_action(
                chat_id=message.chat.id, action=ChatAction.TYPING
            )
        except Exception:
            logger.debug("Typing xabarini yuborib bo'lmadi.", exc_info=True)

    try:
        answer, source = await ask_tutor(text, history, user["level"])
        await add_message(user_id, "assistant", answer[:4000])
    except Exception:
        logger.exception("AI Ustoz javobini olishda xatolik")
        answer = (
            "⚠️ Hozir javob bera olmadim. Iltimos, birozdan so'ng qayta "
            "urinib ko'ring."
        )
        source = "plain"

    await message.answer(
        _prepare_reply(answer, source),
        reply_markup=get_ai_mode_keyboard(),
    )
