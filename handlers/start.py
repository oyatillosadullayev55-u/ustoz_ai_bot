"""/start buyrug'i va foydalanuvchini ro'yxatdan o'tkazish."""

from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import get_settings
from database.users import (
    create_user,
    get_user,
    update_last_seen,
    update_level,
)
from handlers.common import react
from keyboards.inline_buttons import LEVELS, get_levels_keyboard
from keyboards.main_menu import MAIN_MENU_TEXTS, get_main_menu_keyboard

router = Router(name="start")
logger = logging.getLogger(__name__)

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50


class RegistrationStates(StatesGroup):
    waiting_name = State()
    waiting_level = State()


def _is_valid_name(full_name: str) -> bool:
    if not MIN_NAME_LENGTH <= len(full_name) <= MAX_NAME_LENGTH:
        return False
    if full_name.startswith("/"):
        return False
    if full_name in MAIN_MENU_TEXTS:
        return False
    return True


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    tg_user = message.from_user
    if tg_user is None:
        return

    await react(message, "👋")
    user = await get_user(tg_user.id)
    if user is not None:
        await update_last_seen(tg_user.id)
        await message.answer(
            f"Xush kelibsiz, <b>{html.escape(user['full_name'])}</b>! 👋\n\n"
            "Bosh menyudan kerakli bo'limni tanlang.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Men <b>UstozAI</b> — o'zbek tilida bilim olishingizga yordam "
        "beruvchi botman.\n"
        "Shiorimiz: <i>“Bilim olish endi oson!”</i>\n\n"
        "Boshlashdan oldin sizni tanishtirib olaylik. Ismingizni yozing:"
    )
    await state.set_state(RegistrationStates.waiting_name)


@router.message(RegistrationStates.waiting_name)
async def process_name(message: Message, state: FSMContext) -> None:
    full_name = " ".join((message.text or "").split())

    if not _is_valid_name(full_name):
        await message.answer(
            "Iltimos, ismingizni 2–50 belgidan iborat oddiy matn ko'rinishida "
            "yozing."
        )
        return

    await state.update_data(full_name=full_name)
    await message.answer(
        f"Rahmat, <b>{html.escape(full_name)}</b>!\n\n"
        "Bilim darajangizni tanlang. Bu keyingi darslar va AI javoblarini "
        "sizga moslashtirishda yordam beradi:",
        reply_markup=get_levels_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_level)


@router.callback_query(RegistrationStates.waiting_level, F.data.startswith("level:"))
async def process_level(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or callback.message is None or not callback.data:
        await callback.answer(
            "Xatolik yuz berdi. Iltimos, /start buyrug'ini qayta yuboring.",
            show_alert=True,
        )
        return

    level_code = callback.data.removeprefix("level:")
    if level_code not in LEVELS:
        await callback.answer("Noto'g'ri daraja tanlandi.", show_alert=True)
        return

    data = await state.get_data()
    full_name = str(data.get("full_name", "")).strip()
    if not full_name:
        await state.clear()
        await callback.answer()
        await callback.message.answer(
            "Ro'yxatdan o'tish ma'lumotlari topilmadi. /start buyrug'ini "
            "qayta yuboring."
        )
        return

    tg_user = callback.from_user
    existing_user = await get_user(tg_user.id)
    if existing_user is None:
        await create_user(
            telegram_id=tg_user.id,
            full_name=full_name,
            username=tg_user.username,
            language=get_settings().default_language,
            level=level_code,
        )
    elif existing_user["level"] != level_code:
        await update_level(tg_user.id, level_code)

    await update_last_seen(tg_user.id)
    await state.clear()

    level_label = LEVELS[level_code]
    await callback.answer("Daraja saqlandi ✅")

    try:
        await callback.message.edit_text(
            "✅ <b>Ro'yxatdan o'tish yakunlandi!</b>\n\n"
            f"👤 Ism: <b>{html.escape(full_name)}</b>\n"
            f"📚 Daraja: <b>{level_label}</b>\n\n"
            "Endi bosh menyudan kerakli bo'limni tanlang."
        )
    except TelegramBadRequest:
        # Foydalanuvchi tugmani ikki marta tez bosganda xabar allaqachon
        # tahrirlangan bo'lishi mumkin. Bu holat xato hisoblanmaydi.
        logger.debug("Darajani tanlash xabari avval tahrirlangan.")

    await callback.message.answer(
        "🏠 <b>Bosh menyu</b>\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=get_main_menu_keyboard(),
    )
    logger.info("Foydalanuvchi ro'yxatdan o'tdi: id=%s", tg_user.id)
