"""Admin panel: statistika va foydalanuvchilarga xabar yuborish."""

from __future__ import annotations

import asyncio
import contextlib
import html
import logging
import sqlite3

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import get_settings
from database.admin import get_admin_stats, get_all_user_ids
from handlers.common import safe_edit
from keyboards.inline_buttons import (
    get_admin_keyboard,
    get_broadcast_cancel_keyboard,
    get_broadcast_confirm_keyboard,
)
from keyboards.main_menu import get_main_menu_keyboard
from services.backup import (
    cleanup_old_backups,
    create_backup_copy,
    create_export_csv,
)

router = Router(name="admin")
logger = logging.getLogger(__name__)

MAX_BROADCAST_LENGTH = 3000


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return bool(
            event.from_user is not None
            and get_settings().is_admin(event.from_user.id)
        )


class AdminStates(StatesGroup):
    waiting_broadcast = State()
    confirm_broadcast = State()


def _stats_text(stats: dict) -> str:
    return (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🆕 Bugun qo'shildi: <b>{stats['new_today']}</b>\n"
        f"🟢 Bugun faol: <b>{stats['active_today']}</b>\n\n"
        f"📝 Yechilgan testlar: <b>{stats['quizzes']}</b> "
        f"(o'rtacha <b>{round(stats['average_score'])}%</b>)\n"
        f"📚 Tugatilgan darslar: <b>{stats['lessons_completed']}</b>\n"
        f"🤖 Bugungi AI savollar: <b>{stats['ai_today']}</b>\n\n"
        f"📚 Kontent: <b>{stats['subjects']}</b> fan · "
        f"<b>{stats['lessons']}</b> dars · "
        f"<b>{stats['questions']}</b> savol"
    )


@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🛠 <b>Admin panel</b>\n\n"
        "Quyidagi amallardan birini tanlang:",
        reply_markup=get_admin_keyboard(),
    )


@router.message(Command("admin"))
async def admin_denied(message: Message) -> None:
    if message.from_user is None:
        return

    await message.answer(
        "⛔ Bu buyruq faqat bot adminlari uchun.\n\n"
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\n\n"
        "Agar siz bot egasi bo'lsangiz, shu ID ni <code>.env</code> faylidagi "
        "<code>ADMIN_IDS</code> qatoriga qo'shib, botni qayta ishga tushiring.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "admin:stats", IsAdmin())
async def admin_stats(callback: CallbackQuery) -> None:
    stats = await get_admin_stats()
    await safe_edit(callback, _stats_text(stats), get_admin_keyboard())
    await callback.answer("Yangilandi ✅")


async def _send_backup(message: Message) -> None:
    try:
        path = await create_backup_copy()
    except (OSError, sqlite3.Error):
        logger.exception("Baza zaxirasini yaratib bo'lmadi")
        await message.answer("❌ Zaxira nusxasini yaratib bo'lmadi.")
        return

    size_kb = max(1, round(path.stat().st_size / 1024))
    await message.answer_document(
        FSInputFile(path, filename=path.name),
        caption=(
            "💾 <b>Baza zaxirasi</b>\n\n"
            f"📦 Hajmi: <b>{size_kb} KB</b>\n"
            "Faylni saqlab qo'ying. Tiklash uchun uni serverdagi baza fayli "
            "(<code>DATABASE_PATH</code>) o'rniga qo'ying."
        ),
    )
    cleanup_old_backups()


async def _send_export(message: Message) -> None:
    try:
        path, total = await create_export_csv()
    except (OSError, sqlite3.Error):
        logger.exception("CSV eksport faylini yaratib bo'lmadi")
        await message.answer("❌ CSV faylni yaratib bo'lmadi.")
        return

    try:
        await message.answer_document(
            FSInputFile(path, filename=path.name),
            caption=(
                "📤 <b>CSV eksport</b>\n\n"
                f"👥 Foydalanuvchilar: <b>{total}</b>\n"
                "Jadvalda XP, tugatilgan darslar, testlar va o'rtacha "
                "natijalar bor. Fayl Excel yoki Google Sheets'da ochiladi."
            ),
        )
    finally:
        with contextlib.suppress(OSError):
            path.unlink()


@router.callback_query(F.data == "admin:backup", IsAdmin())
async def backup_from_panel(callback: CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Xabar topilmadi.", show_alert=True)
        return
    await callback.answer("Zaxira tayyorlanmoqda...")
    await _send_backup(callback.message)


@router.callback_query(F.data == "admin:export", IsAdmin())
async def export_from_panel(callback: CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Xabar topilmadi.", show_alert=True)
        return
    await callback.answer("CSV tayyorlanmoqda...")
    await _send_export(callback.message)


@router.message(Command("backup"), IsAdmin())
async def backup_command(message: Message) -> None:
    await _send_backup(message)


@router.message(Command("export"), IsAdmin())
async def export_command(message: Message) -> None:
    await _send_export(message)


@router.callback_query(F.data == "admin:broadcast", IsAdmin())
async def start_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AdminStates.waiting_broadcast)
    await safe_edit(
        callback,
        "📢 <b>Xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabar matnini yozing.\n"
        f"Maksimum {MAX_BROADCAST_LENGTH} belgi.\n\n"
        "Xabar oddiy matn sifatida yuboriladi.\n"
        "Bekor qilish uchun «❌ Bekor qilish» tugmasini bosing yoki /cancel "
        "buyrug'ini yuboring.",
        get_broadcast_cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast, IsAdmin(), Command("cancel"))
@router.message(AdminStates.confirm_broadcast, IsAdmin(), Command("cancel"))
async def cancel_by_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Xabar yuborish bekor qilindi.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "admin:broadcast_cancel", IsAdmin())
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit(
        callback,
        "❌ Xabar yuborish bekor qilindi.",
        get_admin_keyboard(),
    )
    await callback.answer()


@router.message(
    AdminStates.waiting_broadcast, IsAdmin(), F.text, ~F.text.startswith("/")
)
async def receive_broadcast(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Xabar bo'sh bo'lmasligi kerak.")
        return
    if len(text) > MAX_BROADCAST_LENGTH:
        await message.answer(
            f"Xabar juda uzun. {MAX_BROADCAST_LENGTH} belgidan oshirmang."
        )
        return

    recipients = await get_all_user_ids(notifications_only=True)
    await state.update_data(broadcast_text=text)
    await state.set_state(AdminStates.confirm_broadcast)

    await message.answer(
        "📢 <b>Xabar ko'rinishi</b>\n\n"
        f"<blockquote>{html.escape(text)}</blockquote>\n\n"
        f"👥 Qabul qiluvchilar: <b>{len(recipients)}</b> ta "
        "(bildirishnomalarni yoqqanlar)\n\n"
        "Yuborilsinmi?",
        reply_markup=get_broadcast_confirm_keyboard(),
    )


@router.callback_query(F.data == "admin:broadcast_confirm", IsAdmin())
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.bot is None:
        await callback.answer("Bot sessiyasi topilmadi.", show_alert=True)
        return

    data = await state.get_data()
    text = str(data.get("broadcast_text", "")).strip()
    if not text:
        await callback.answer(
            "Xabar topilmadi. Qaytadan boshlang.", show_alert=True
        )
        return

    await state.clear()
    await callback.answer("Yuborilmoqda...")

    recipients = await get_all_user_ids(notifications_only=True)
    sent = 0
    failed = 0

    if isinstance(callback.message, Message):
        try:
            await callback.message.edit_text(
                f"📤 Xabar {len(recipients)} ta foydalanuvchiga yuborilmoqda..."
            )
        except TelegramAPIError:
            pass

    for telegram_id in recipients:
        try:
            await callback.bot.send_message(
                chat_id=telegram_id, text=text, parse_mode=None
            )
            sent += 1
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
            try:
                await callback.bot.send_message(
                    chat_id=telegram_id, text=text, parse_mode=None
                )
                sent += 1
            except TelegramAPIError:
                failed += 1
        except TelegramAPIError:
            failed += 1
        except Exception:
            logger.exception("Xabar yuborishda kutilmagan xatolik")
            failed += 1
        await asyncio.sleep(0.05)

    report = (
        "✅ <b>Xabar yuborish yakunlandi</b>\n\n"
        f"Yuborildi: <b>{sent}</b>\n"
        f"Yetkazilmadi: <b>{failed}</b>"
    )
    await safe_edit(callback, report, get_admin_keyboard())
    logger.info(
        "Admin xabar yubordi: yuborildi=%s, xato=%s", sent, failed
    )
