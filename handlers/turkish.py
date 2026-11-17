"""Turk tili darslari: ovozli talaffuz mashqlari."""

from __future__ import annotations

import asyncio
import html
import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from database.content import get_lesson
from database.turkish import get_turkish_phrases
from handlers.common import (
    react,
    require_user_callback,
    safe_edit,
    send_action,
)
from keyboards.inline_buttons import get_turkish_audio_keyboard
from services.turkish_audio import (
    get_audio_source,
    remember_audio_file_id,
)

router = Router(name="turkish")
logger = logging.getLogger(__name__)

PLAYBACK_GAP_SECONDS = 0.5
_locks: dict[int, asyncio.Lock] = {}


def _lock_for(user_id: int) -> asyncio.Lock:
    lock = _locks.get(user_id)
    if lock is None:
        lock = asyncio.Lock()
        _locks[user_id] = lock
    return lock


def _audio_text(lesson, phrases) -> str:
    lines = [
        "🎧 <b>Ovozli talaffuz</b>",
        f"🇹🇷 Turk tili · {lesson['order_index']}-dars",
        "━━━━━━━━━━━━━━",
        "",
        f"📖 <b>{html.escape(str(lesson['title']))}</b>",
        "",
    ]
    for phrase in phrases:
        lines.append(
            f"{phrase['phrase_index']}. "
            f"<b>{html.escape(str(phrase['phrase_tr']))}</b>"
        )
        lines.append(f"   🇺🇿 {html.escape(str(phrase['phrase_uz']))}")
        hint = str(phrase["hint"]).strip()
        if hint:
            lines.append(f"   💡 {html.escape(hint)}")
        lines.append("")

    lines.append(
        "🎙️ Gapni tanlang — bot uni ovozli o'qib beradi. "
        "Eshitganingizdan keyin ovoz chiqarib takrorlang."
    )
    return "\n".join(lines)


def _voice_caption(phrase, position: int, total: int) -> str:
    lines = [
        f"🔊 {position}/{total} · "
        f"<b>{html.escape(str(phrase['phrase_tr']))}</b>",
        f"🇺🇿 {html.escape(str(phrase['phrase_uz']))}",
    ]
    hint = str(phrase["hint"]).strip()
    if hint:
        lines.append(f"💡 {html.escape(hint)}")
    return "\n".join(lines)


async def _send_phrase_voice(
    bot,
    chat_id: int,
    lesson_id: int,
    phrase,
    position: int,
    total: int,
) -> bool:
    index = int(phrase["phrase_index"])
    source = get_audio_source(lesson_id, index)
    if source is None:
        logger.warning(
            "Talaffuz ovozi topilmadi: dars=%s, gap=%s", lesson_id, index
        )
        return False

    try:
        sent = await bot.send_voice(
            chat_id=chat_id,
            voice=source,
            caption=_voice_caption(phrase, position, total),
        )
    except TelegramBadRequest:
        logger.warning(
            "Talaffuz ovozini yuborib bo'lmadi: dars=%s, gap=%s",
            lesson_id,
            index,
            exc_info=True,
        )
        return False

    if isinstance(sent, Message) and sent.voice:
        remember_audio_file_id(lesson_id, index, sent.voice.file_id)
    return True


async def _load_turkish_lesson(callback: CallbackQuery, lesson_id: int):
    lesson = await get_lesson(lesson_id)
    if lesson is None:
        await callback.answer("Dars topilmadi.", show_alert=True)
        return None
    if lesson["subject_code"] != "turkish":
        await callback.answer(
            "Ovozli talaffuz faqat turk tili darslarida mavjud.",
            show_alert=True,
        )
        return None
    return lesson


@router.callback_query(F.data.startswith("turk:audio:"))
async def show_audio_screen(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        lesson_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    lesson = await _load_turkish_lesson(callback, lesson_id)
    if lesson is None:
        return

    phrases = await get_turkish_phrases(lesson_id)
    if not phrases:
        await callback.answer(
            "Bu darsda hali gaplar yo'q.", show_alert=True
        )
        return

    await safe_edit(
        callback,
        _audio_text(lesson, phrases),
        get_turkish_audio_keyboard(lesson_id, phrases),
    )
    await react(callback.message, "🎧")
    await callback.answer()


@router.callback_query(F.data.startswith("turk:say:"))
async def say_phrase(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        _, _, lesson_raw, index_raw = callback.data.split(":")
        lesson_id = int(lesson_raw)
        index = int(index_raw)
    except ValueError:
        await callback.answer("Gap topilmadi.", show_alert=True)
        return

    lesson = await _load_turkish_lesson(callback, lesson_id)
    if lesson is None:
        return

    phrases = await get_turkish_phrases(lesson_id)
    phrase = next(
        (item for item in phrases if int(item["phrase_index"]) == index), None
    )
    if phrase is None:
        await callback.answer("Gap topilmadi.", show_alert=True)
        return

    if not isinstance(callback.message, Message):
        await callback.answer("Xabar topilmadi.", show_alert=True)
        return

    await send_action(callback.message, ChatAction.RECORD_VOICE)
    sent = await _send_phrase_voice(
        callback.bot,
        callback.message.chat.id,
        lesson_id,
        phrase,
        phrase["phrase_index"],
        len(phrases),
    )
    if not sent:
        await callback.answer(
            "Ovoz fayli topilmadi. Keyinroq qayta urinib ko'ring.",
            show_alert=True,
        )
        return
    await callback.answer("🔊 Tinglang va takrorlang")


@router.callback_query(F.data.startswith("turk:all:"))
async def say_all_phrases(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        lesson_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    lesson = await _load_turkish_lesson(callback, lesson_id)
    if lesson is None:
        return

    phrases = await get_turkish_phrases(lesson_id)
    if not phrases:
        await callback.answer("Bu darsda hali gaplar yo'q.", show_alert=True)
        return

    if not isinstance(callback.message, Message):
        await callback.answer("Xabar topilmadi.", show_alert=True)
        return

    user_id = int(user["telegram_id"])
    lock = _lock_for(user_id)
    if lock.locked():
        await callback.answer(
            "Avvalgi tinglash tugashini kuting.", show_alert=True
        )
        return

    await callback.answer(f"🔊 {len(phrases)} ta gap yuborilmoqda…")
    chat_id = callback.message.chat.id

    async with lock:
        await send_action(callback.message, ChatAction.RECORD_VOICE)
        sent_count = 0
        for position, phrase in enumerate(phrases, start=1):
            sent = await _send_phrase_voice(
                callback.bot,
                chat_id,
                lesson_id,
                phrase,
                position,
                len(phrases),
            )
            if sent:
                sent_count += 1
            if position < len(phrases):
                await asyncio.sleep(PLAYBACK_GAP_SECONDS)

    if sent_count == 0:
        await callback.message.answer(
            "Ovoz fayllari vaqtincha mavjud emas. Keyinroq urinib ko'ring."
        )
    else:
        logger.info(
            "Talaffuz tinglandi: user=%s, dars=%s, gaplar=%s",
            user_id,
            lesson_id,
            sent_count,
        )
