"""Foydalanuvchi sozlamalari."""

from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import get_settings
from database.users import (
    get_user,
    update_level,
    update_notifications,
)
from handlers.common import require_user, require_user_callback, safe_edit
from keyboards.inline_buttons import LEVELS, get_settings_keyboard
from keyboards.main_menu import BTN_SETTINGS

router = Router(name="user_settings")


def _build_settings_text(user) -> str:
    level_label = LEVELS.get(user["level"], user["level"])
    notifications = bool(user["notifications_enabled"])
    notification_label = "Yoqilgan ✅" if notifications else "O'chirilgan 🔕"

    settings = get_settings()
    if settings.ai_configured:
        ai_status = f"Ulangan ({html.escape(settings.ai_model)})"
    else:
        ai_status = "Mahalliy dars bazasi (AI kaliti sozlanmagan)"

    return (
        "⚙️ <b>Sozlamalar</b>\n\n"
        f"👤 Ism: <b>{html.escape(user['full_name'])}</b>\n"
        f"🎯 Daraja: <b>{level_label}</b>\n"
        f"🔔 Bildirishnomalar: <b>{notification_label}</b>\n"
        f"🌐 Til: <b>O'zbekcha</b>\n"
        f"🧠 AI Ustoz: <b>{ai_status}</b>\n\n"
        "Darajani o'zgartirsangiz, AI javoblari shunga moslashadi.\n"
        "Bildirishnomalar o'chirilganda admin e'lonlari yuborilmaydi."
    )


@router.message(F.text == BTN_SETTINGS)
async def settings_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return

    await message.answer(
        _build_settings_text(user),
        reply_markup=get_settings_keyboard(
            user["level"], bool(user["notifications_enabled"])
        ),
    )


@router.callback_query(F.data.startswith("settings:level:"))
async def change_level(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    level = callback.data.rsplit(":", 1)[-1]
    if level not in LEVELS:
        await callback.answer("Noto'g'ri daraja.", show_alert=True)
        return

    await update_level(user["telegram_id"], level)
    refreshed = await get_user(user["telegram_id"])
    if refreshed is None:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    await safe_edit(
        callback,
        _build_settings_text(refreshed),
        get_settings_keyboard(
            refreshed["level"], bool(refreshed["notifications_enabled"])
        ),
    )
    await callback.answer(f"Daraja yangilandi: {LEVELS[level]} ✅")


@router.callback_query(F.data == "settings:notify")
async def toggle_notifications(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    new_value = not bool(user["notifications_enabled"])
    await update_notifications(user["telegram_id"], new_value)
    refreshed = await get_user(user["telegram_id"])
    if refreshed is None:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    await safe_edit(
        callback,
        _build_settings_text(refreshed),
        get_settings_keyboard(
            refreshed["level"], bool(refreshed["notifications_enabled"])
        ),
    )
    await callback.answer(
        "Bildirishnomalar yoqildi ✅" if new_value else "Bildirishnomalar o'chirildi 🔕"
    )
