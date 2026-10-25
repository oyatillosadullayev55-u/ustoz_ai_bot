"""Kunlik reja bo'yicha eslatmalar."""

from __future__ import annotations

import asyncio
import html
import logging
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter

from config import get_settings
from database.goals import get_pending_reminders
from keyboards.main_menu import get_main_menu_keyboard
from time_utils import local_now, local_today, seconds_until_local_time

logger = logging.getLogger(__name__)

SEND_DELAY_SECONDS = 0.05


def format_reminder(
    full_name: str,
    target_lessons: int,
    target_quizzes: int,
    completed_lessons: int,
    completed_quizzes: int,
) -> str:
    lines = [
        "🌙 <b>Kunlik eslatma</b>",
        "",
        f"Salom, <b>{html.escape(full_name)}</b>!",
        "Bugungi maqsadingiz hali bajarilmagan:",
        "",
    ]

    if target_lessons > 0:
        lines.append(
            f"📚 Darslar: <b>{completed_lessons}/{target_lessons}</b>"
        )
    if target_quizzes > 0:
        lines.append(
            f"📝 Testlar: <b>{completed_quizzes}/{target_quizzes}</b>"
        )

    remaining_lessons = max(target_lessons - completed_lessons, 0)
    remaining_quizzes = max(target_quizzes - completed_quizzes, 0)
    remaining_parts: list[str] = []
    if remaining_lessons:
        remaining_parts.append(f"{remaining_lessons} dars")
    if remaining_quizzes:
        remaining_parts.append(f"{remaining_quizzes} test")

    lines.append("")
    if remaining_parts:
        lines.append(f"Qoldi: <b>{', '.join(remaining_parts)}</b>.")
    lines.append(
        "Davom etish uchun «📅 Kunlik reja» bo'limini oching."
    )
    return "\n".join(lines)


async def _send_reminder(bot: Bot, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=get_main_menu_keyboard(),
        )
    except TelegramRetryAfter as exc:
        await asyncio.sleep(exc.retry_after)
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=get_main_menu_keyboard(),
        )


async def send_due_reminders(
    bot: Bot, *, goal_date: str | None = None
) -> tuple[int, int]:
    """Bugungi rejasi bajarilmagan foydalanuvchilarga eslatma yuboradi."""
    rows = await get_pending_reminders(goal_date or local_today())
    sent = 0
    failed = 0

    for row in rows:
        text = format_reminder(
            str(row["full_name"]),
            int(row["target_lessons"]),
            int(row["target_quizzes"]),
            int(row["completed_lessons"]),
            int(row["completed_quizzes"]),
        )
        try:
            await _send_reminder(bot, int(row["user_id"]), text)
            sent += 1
        except TelegramAPIError:
            failed += 1
            logger.warning(
                "Kunlik eslatma yuborilmadi: user=%s", row["user_id"]
            )
        await asyncio.sleep(SEND_DELAY_SECONDS)

    logger.info(
        "Kunlik eslatmalar yakunlandi: yuborildi=%s, xato=%s", sent, failed
    )
    return sent, failed


async def run_daily_reminders(bot: Bot) -> None:
    """Har kuni belgilangan mahalliy vaqtda eslatmalarni yuboradi."""
    settings = get_settings()
    hour = settings.daily_reminder_hour

    while True:
        delay = seconds_until_local_time(hour)
        logger.info(
            "Keyingi kunlik eslatma: %s (UTC+5)",
            (local_now() + timedelta(seconds=delay)).strftime("%d.%m.%Y %H:%M"),
        )
        await asyncio.sleep(delay)

        try:
            await send_due_reminders(bot)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Kunlik eslatmalarni yuborishda xatolik")
