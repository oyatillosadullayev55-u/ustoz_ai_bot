"""Handlerlar uchun umumiy yordamchilar."""

from __future__ import annotations

import logging

import aiosqlite
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, ReactionTypeEmoji

from database.users import get_user
from keyboards.main_menu import get_main_menu_keyboard
from services.gamification import RewardResult

logger = logging.getLogger(__name__)


async def react(message: Message | None, emoji: str) -> None:
    """Xabarga emoji reaksiya qo'yadi — jonli ko'rinish effekti."""
    if not isinstance(message, Message) or message.bot is None:
        return
    try:
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
        )
    except TelegramAPIError:
        logger.debug("Reaksiya qo'yib bo'lmadi: %s", emoji, exc_info=True)


async def send_action(message: Message | None, action: ChatAction) -> None:
    """«Yozmoqda»/«Rasm yuklanmoqda» holatini ko'rsatadi."""
    if not isinstance(message, Message) or message.bot is None:
        return
    try:
        await message.bot.send_chat_action(
            chat_id=message.chat.id, action=action
        )
    except TelegramAPIError:
        logger.debug("Chat action yuborib bo'lmadi: %s", action, exc_info=True)


async def require_user(message: Message) -> aiosqlite.Row | None:
    if message.from_user is None:
        return None
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer(
            "Avval ro'yxatdan o'ting. /start buyrug'ini yuboring.",
            reply_markup=get_main_menu_keyboard(),
        )
    return user


async def require_user_callback(callback: CallbackQuery) -> aiosqlite.Row | None:
    if callback.from_user is None:
        await callback.answer("Xatolik yuz berdi.", show_alert=True)
        return None
    user = await get_user(callback.from_user.id)
    if user is None:
        await callback.answer(
            "Avval ro'yxatdan o'ting: /start buyrug'ini yuboring.",
            show_alert=True,
        )
    return user


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Xabarni tahrirlaydi; foto yoki eskirgan xabarda yangisini yuboradi."""
    if not isinstance(callback.message, Message):
        return

    message = callback.message
    if message.photo:
        try:
            await message.delete()
        except TelegramBadRequest:
            pass
        await message.answer(text, reply_markup=reply_markup)
        return

    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=reply_markup)


def progress_bar(done: int, target: int, width: int = 8) -> str:
    if target <= 0:
        return "░" * width
    ratio = min(done / target, 1.0)
    filled = round(ratio * width)
    return "▓" * filled + "░" * (width - filled)


def reward_notice(result: RewardResult) -> str:
    """Yangi daraja va yutuqlar haqidagi xabar matni."""
    lines: list[str] = []
    if result.rank_up:
        lines.append(
            f"🎉 Yangi daraja: {result.rank.emoji} <b>{result.rank.name}</b>!"
        )
    for item in result.achievements:
        lines.append(
            f"{item.emoji} <b>Yangi yutuq:</b> {item.title} — {item.description}"
        )
    if not lines:
        return ""
    lines.append(f"⭐ +{result.xp_gained} XP · Jami: <b>{result.xp} XP</b>")
    return "\n".join(lines)


async def notify_rewards(message: Message | None, result: RewardResult) -> None:
    text = reward_notice(result)
    if not text or not isinstance(message, Message):
        return
    try:
        await message.answer(text)
    except TelegramAPIError:
        logger.debug("Mukofot xabarini yuborib bo'lmadi", exc_info=True)
