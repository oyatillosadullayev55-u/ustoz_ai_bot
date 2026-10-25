"""UstozAI Telegram botining kirish nuqtasi."""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import suppress
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat, ErrorEvent

from config import BASE_DIR, ConfigError, Settings, get_settings
from database.db import init_db
from handlers import (
    admin,
    ai_tutor,
    daily_plan,
    lessons,
    menu,
    progress,
    quizzes,
    start,
)
from handlers import settings as user_settings
from services.health_server import start_health_server, stop_health_server
from services.reminders import run_daily_reminders

logger = logging.getLogger(__name__)

LOG_DIR = BASE_DIR / "logs"


def setup_logging(level: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_DIR / "bot.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Har bir xabarni logga yozadigan aiogram loggerini jim qilamiz.
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


async def set_bot_commands(bot: Bot, settings: Settings) -> None:
    base_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="menu", description="Bosh menyuni ochish"),
        BotCommand(command="qidiruv", description="Darslardan qidirish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="id", description="Telegram ID raqamingiz"),
    ]
    await bot.set_my_commands(base_commands)

    for admin_id in settings.admin_ids:
        try:
            await bot.set_my_commands(
                [
                    *base_commands,
                    BotCommand(command="admin", description="Admin panel"),
                ],
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except TelegramBadRequest:
            logger.warning(
                "Admin buyruqlarini o'rnatib bo'lmadi (admin botni hali "
                "ishga tushirmagan bo'lishi mumkin): %s",
                admin_id,
            )


async def on_error(event: ErrorEvent) -> None:
    logger.error("Kutilmagan xatolik yuz berdi", exc_info=event.exception)

    update = event.update
    try:
        if update.message is not None:
            await update.message.answer(
                "❌ Kutilmagan xatolik yuz berdi. Iltimos, /start buyrug'ini "
                "qayta yuboring."
            )
        elif update.callback_query is not None:
            await update.callback_query.answer(
                "Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
                show_alert=True,
            )
    except Exception:
        logger.exception("Foydalanuvchiga xatolik haqida xabar yuborib bo'lmadi")


async def run_bot(settings: Settings) -> None:
    health_runner = await start_health_server()
    bot: Bot | None = None
    reminder_task: asyncio.Task[None] | None = None

    try:
        await init_db()

        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        dispatcher = Dispatcher(storage=MemoryStorage())
        dispatcher.errors.register(on_error)
        dispatcher.include_router(start.router)
        dispatcher.include_router(ai_tutor.router)
        dispatcher.include_router(lessons.router)
        dispatcher.include_router(quizzes.router)
        dispatcher.include_router(progress.router)
        dispatcher.include_router(daily_plan.router)
        dispatcher.include_router(user_settings.router)
        dispatcher.include_router(admin.router)
        dispatcher.include_router(menu.router)

        bot_info = await bot.get_me()
        logger.info("UstozAI ishga tushdi: @%s", bot_info.username)

        await set_bot_commands(bot, settings)
        await bot.delete_webhook(drop_pending_updates=False)

        if settings.daily_reminders_enabled:
            reminder_task = asyncio.create_task(run_daily_reminders(bot))
            logger.info(
                "Kunlik eslatmalar yoqilgan: har kuni %02d:00 (UTC+5)",
                settings.daily_reminder_hour,
            )

        await dispatcher.start_polling(bot)
    finally:
        if reminder_task is not None:
            reminder_task.cancel()
            with suppress(asyncio.CancelledError):
                await reminder_task
        if bot is not None:
            await bot.session.close()
        await stop_health_server(health_runner)


def main() -> None:
    try:
        settings = get_settings()
    except ConfigError as exc:
        print(f"[XATO] {exc}")
        raise SystemExit(1) from None

    setup_logging(settings.log_level)

    if not settings.admin_ids:
        logger.warning(
            "ADMIN_IDS bo'sh. Admin panel uchun /id orqali ID oling va "
            "ADMIN_IDS ga qo'shib, botni qayta ishga tushiring."
        )

    if settings.ai_configured:
        logger.info("AI Ustoz provayderi ulangan: %s", settings.ai_model)
    elif settings.ai_enabled and not settings.ai_api_key:
        logger.warning(
            "AI_ENABLED=true, lekin AI_API_KEY bo'sh. AI Ustoz dars bazasidan "
            "javob beradi."
        )
    else:
        logger.info("AI o'chirilgan. AI Ustoz dars bazasidan javob beradi.")

    try:
        asyncio.run(run_bot(settings))
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
    except Exception:
        logger.exception("Bot xatolik bilan to'xtadi.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
