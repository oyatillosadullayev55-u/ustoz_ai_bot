"""Umumiy buyruqlar, bosh menyu va zaxira handlerlar."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.users import get_user
from handlers.common import require_user_callback
from keyboards.main_menu import get_main_menu_keyboard

router = Router(name="menu")
logger = logging.getLogger(__name__)


@router.message(Command("menu"))
async def menu_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        return

    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Avval ro'yxatdan o'ting: /start buyrug'ini yuboring.")
        return

    await message.answer(
        "🏠 <b>Bosh menyu</b>\nKerakli bo'limni tanlang:",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(Command("help"))
async def help_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        return

    user = await get_user(message.from_user.id)
    text = (
        "ℹ️ <b>Yordam</b>\n\n"
        "/start — botni ishga tushirish va ro'yxatdan o'tish\n"
        "/menu — bosh menyuni ochish\n"
        "/qidiruv — darslardan mavzu bo'yicha qidirish\n"
        "/help — ushbu yordam xabari\n"
        "/id — Telegram ID raqamingiz\n\n"
        "<b>Bo'limlar:</b>\n"
        "🧠 AI Ustoz — savol berish va tushuntirish olish\n"
        "📚 Darslar — fanlar va mavzular\n"
        "📝 Testlar — 4 variantli testlar\n"
        "📊 Mening natijalarim — statistika\n"
        "📅 Kunlik reja — kunlik maqsadlar\n"
        "⚙️ Sozlamalar — daraja va bildirishnomalar\n\n"
        "Bo'limlarni pastdagi tugmalar orqali tanlang."
    )

    if user is None:
        text += "\n\nBoshlash uchun /start buyrug'ini yuboring."
        await message.answer(text)
        return

    await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.message(Command("id"))
async def id_command(message: Message) -> None:
    if message.from_user is None:
        return

    await message.answer(
        "🆔 Sizning Telegram ID raqamingiz:\n"
        f"<code>{message.from_user.id}</code>\n\n"
        "Bot egasi bu raqamni <code>ADMIN_IDS</code> sozlamasiga qo'shishi mumkin."
    )


@router.callback_query(F.data == "menu:home")
async def go_home(callback: CallbackQuery, state: FSMContext) -> None:
    if await require_user_callback(callback) is None:
        return

    await state.clear()

    if isinstance(callback.message, Message):
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        await callback.message.answer(
            "🏠 <b>Bosh menyu</b>\nKerakli bo'limni tanlang:",
            reply_markup=get_main_menu_keyboard(),
        )
    elif callback.bot is not None and callback.from_user is not None:
        await callback.bot.send_message(
            callback.from_user.id,
            "🏠 <b>Bosh menyu</b>\nKerakli bo'limni tanlang:",
            reply_markup=get_main_menu_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data.startswith("level:"))
async def stale_level_callback(callback: CallbackQuery) -> None:
    await callback.answer(
        "Siz allaqachon ro'yxatdan o'tgansiz. Bosh menyudan foydalaning.",
        show_alert=True,
    )


@router.callback_query()
async def stale_callback(callback: CallbackQuery) -> None:
    await callback.answer(
        "Bu amal eskirgan. Iltimos, menyudan qayta tanlang.",
    )


@router.message(F.text)
async def handle_unknown_text(message: Message) -> None:
    if message.from_user is None:
        return

    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Avval ro'yxatdan o'ting: /start buyrug'ini yuboring.")
        return

    await message.answer(
        "Savolingizni tushunmadim. 🧠 «AI Ustoz» tugmasi orqali savol bering "
        "yoki pastdagi menyudan kerakli bo'limni tanlang.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message()
async def handle_unsupported_content(message: Message) -> None:
    await message.answer(
        "Men faqat matnli xabarlarni qabul qilaman. "
        "Iltimos, menyu tugmalaridan foydalaning yoki /start ni yuboring.",
        reply_markup=get_main_menu_keyboard(),
    )
