"""Handlerlar uchun umumiy yordamchilar."""

from __future__ import annotations

import aiosqlite
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from database.users import get_user
from keyboards.main_menu import get_main_menu_keyboard


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
    """Xabarni tahrirlaydi; xabar eskirgan bo'lsa yangi xabar yuboradi."""
    if callback.message is None:
        return
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=reply_markup)


def progress_bar(done: int, target: int, width: int = 8) -> str:
    if target <= 0:
        return "░" * width
    ratio = min(done / target, 1.0)
    filled = round(ratio * width)
    return "▓" * filled + "░" * (width - filled)
