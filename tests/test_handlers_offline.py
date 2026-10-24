"""Router, FSM va callback oqimlarini Telegramga ulanmasdan tekshirish.

Ishga tushirish:
    .venv\\Scripts\\python.exe tests\\test_handlers_offline.py
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import tempfile
from datetime import datetime, timezone

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEMP_DIR = tempfile.TemporaryDirectory(prefix="ustozai_handlers_")
os.environ["DATABASE_PATH"] = str(pathlib.Path(TEMP_DIR.name) / "handlers.db")
os.environ["BOT_TOKEN"] = "123456789:TEST_TOKEN_FOR_HANDLER_TESTS"
os.environ["ADMIN_IDS"] = "999000001"
os.environ["AI_ENABLED"] = "false"
os.environ["AI_API_KEY"] = ""

from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ChatType, ParseMode  # noqa: E402
from aiogram.fsm.storage.memory import MemoryStorage  # noqa: E402
from aiogram.methods import (  # noqa: E402
    EditMessageText,
    SendMessage,
)
from aiogram.types import (  # noqa: E402
    CallbackQuery,
    Chat,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    Update,
    User,
)

from config import get_settings  # noqa: E402

get_settings.cache_clear()

from database.chat import get_history  # noqa: E402
from database.content import get_question  # noqa: E402
from database.db import get_connection, init_db  # noqa: E402
from database.goals import get_today_goal  # noqa: E402
from database.users import get_user  # noqa: E402
from handlers import (  # noqa: E402
    admin,
    ai_tutor,
    daily_plan,
    lessons,
    menu,
    progress,
    quizzes,
    start,
)
from handlers import settings as user_settings  # noqa: E402

USER_ID = 999000001
BOT_ID = 123456789


class FakeSession:
    """Tarmoqqa chiqmasdan so'rovlarni yozib oluvchi sessiya."""

    def __init__(self) -> None:
        self.calls: list[object] = []

    async def __call__(self, bot, method, timeout=None):  # noqa: ANN001
        self.calls.append(method)
        return True

    async def close(self) -> None:
        return None


def check(condition: bool, message: str, errors: list[BaseException]) -> None:
    if errors:
        raise AssertionError(f"Handler xatosi: {errors!r}")
    if not condition:
        raise AssertionError(message)
    print(f"OK - {message}")


def sent_texts(session: FakeSession) -> list[str]:
    texts: list[str] = []
    for method in session.calls:
        if isinstance(method, (SendMessage, EditMessageText)) and method.text:
            texts.append(method.text)
    return texts


def last_text(session: FakeSession) -> str:
    texts = sent_texts(session)
    return texts[-1] if texts else ""


def last_inline_callbacks(session: FakeSession) -> list[str]:
    callbacks: list[str] = []
    for method in session.calls:
        if isinstance(method, (SendMessage, EditMessageText)):
            markup = method.reply_markup
            if isinstance(markup, InlineKeyboardMarkup):
                callbacks = [
                    button.callback_data
                    for row in markup.inline_keyboard
                    for button in row
                    if button.callback_data
                ]
    return callbacks


def last_reply_keyboard(session: FakeSession) -> list[str]:
    for method in reversed(session.calls):
        if isinstance(method, (SendMessage, EditMessageText)):
            markup = method.reply_markup
            if isinstance(markup, ReplyKeyboardMarkup):
                return [button.text for row in markup.keyboard for button in row]
    return []


async def main() -> None:
    await init_db()

    fake = FakeSession()
    bot = Bot(
        token=f"{BOT_ID}:TEST_TOKEN",
        session=fake,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())
    errors: list[BaseException] = []

    async def record_error(event) -> None:  # noqa: ANN001
        errors.append(event.exception)
        print(f"HANDLER_ERROR: {event.exception!r}")

    dispatcher.errors.register(record_error)
    dispatcher.include_router(start.router)
    dispatcher.include_router(ai_tutor.router)
    dispatcher.include_router(lessons.router)
    dispatcher.include_router(quizzes.router)
    dispatcher.include_router(progress.router)
    dispatcher.include_router(daily_plan.router)
    dispatcher.include_router(user_settings.router)
    dispatcher.include_router(admin.router)
    dispatcher.include_router(menu.router)

    user = User(id=USER_ID, is_bot=False, first_name="Test")
    bot_user = User(id=BOT_ID, is_bot=True, first_name="UstozAI", username="ustoz_bot")
    chat = Chat(id=USER_ID, type=ChatType.PRIVATE)
    update_id = 0

    async def send_text(text: str) -> None:
        nonlocal update_id
        update_id += 1
        message = Message(
            message_id=update_id,
            date=datetime.now(timezone.utc),
            chat=chat,
            from_user=user,
            text=text,
        ).as_(bot)
        await dispatcher.feed_update(
            bot, Update(update_id=update_id, message=message)
        )

    callback_message = Message(
        message_id=9000,
        date=datetime.now(timezone.utc),
        chat=chat,
        from_user=bot_user,
        text="inline",
    ).as_(bot)

    async def send_callback(data: str) -> None:
        nonlocal update_id
        update_id += 1
        callback = CallbackQuery(
            id=f"cb-{update_id}",
            from_user=user,
            chat_instance="test-chat-instance",
            message=callback_message,
            data=data,
        ).as_(bot)
        await dispatcher.feed_update(
            bot, Update(update_id=update_id, callback_query=callback)
        )

    # 1. Ro'yxatdan o'tish
    fake.calls.clear()
    await send_text("/start")
    check("ismingizni" in last_text(fake).lower(), "ism so'rash xabari yuborildi", errors)

    fake.calls.clear()
    await send_text("Ali")
    check("darajangizni" in last_text(fake).lower(), "daraja tanlash so'raldi", errors)
    check("level:intermediate" in last_inline_callbacks(fake), "daraja tugmalari chiqdi", errors)

    fake.calls.clear()
    await send_callback("level:intermediate")
    row = await get_user(USER_ID)
    check(row is not None and row["level"] == "intermediate", "foydalanuvchi bazaga saqlandi", errors)
    check(
        any("Ro'yxatdan o'tish yakunlandi" in text for text in sent_texts(fake)),
        "ro'yxatdan o'tish tasdiqlandi",
        errors,
    )
    check(
        "📚 Darslar" in last_reply_keyboard(fake),
        "bosh menyu klaviaturasi yuborildi",
        errors,
    )

    fake.calls.clear()
    await send_text("/start")
    check("Xush kelibsiz" in last_text(fake), "qayta /start dublikat yaratmadi", errors)

    # 2. Darslar oqimi
    fake.calls.clear()
    await send_text("📚 Darslar")
    check("lesson:subject:5" in last_inline_callbacks(fake), "fanlar ro'yxati chiqdi", errors)

    fake.calls.clear()
    await send_callback("lesson:subject:5")
    check("lesson:view:501" in last_inline_callbacks(fake), "Biologiya darslari chiqdi", errors)

    fake.calls.clear()
    await send_callback("lesson:view:501")
    check("Hujayra tuzilishi" in last_text(fake), "dars matni ochildi", errors)
    check("lesson:complete:501" in last_inline_callbacks(fake), "darsni tugatish tugmasi bor", errors)

    fake.calls.clear()
    await send_callback("lesson:complete:501")
    check("Bu dars tugatilgan" in last_text(fake), "dars tugatilgan deb belgilandi", errors)
    check("lesson:complete:501" not in last_inline_callbacks(fake), "tugatish tugmasi olib tashlandi", errors)
    goal = await get_today_goal(USER_ID)
    check(int(goal["completed_lessons"]) == 1, "kunlik reja darsni sanadi", errors)

    # 3. Test oqimi: har bir savolga to'g'ri javob beriladi
    fake.calls.clear()
    await send_text("📝 Testlar")
    check("quiz:subject:5" in last_inline_callbacks(fake), "test fanlari ro'yxati chiqdi", errors)

    fake.calls.clear()
    await send_callback("quiz:subject:5")
    check("savol 1/5" in last_text(fake), "test birinchi savoldan boshlandi", errors)

    for question_number in range(1, 6):
        callbacks = last_inline_callbacks(fake)
        answer_callbacks = [item for item in callbacks if item.startswith("quiz:answer:")]
        check(len(answer_callbacks) == 4, f"{question_number}-savolda 4 ta variant bor", errors)

        _, _, question_raw, _ = answer_callbacks[0].split(":")
        question = await get_question(int(question_raw))
        assert question is not None
        correct = int(question["correct_option"])

        fake.calls.clear()
        await send_callback(f"quiz:answer:{question['id']}:{correct}")

        if question_number < 5:
            check(
                f"savol {question_number + 1}/5" in last_text(fake),
                f"{question_number + 1}-savolga o'tildi",
                errors,
            )

    check("Test yakunlandi" in last_text(fake), "test yakunlandi xabari chiqdi", errors)
    check("5/5" in last_text(fake) and "100%" in last_text(fake), "natija 100% hisoblandi", errors)

    async with get_connection() as db:
        cursor = await db.execute("SELECT COUNT(*) AS total FROM quiz_results")
        quiz_count = int((await cursor.fetchone())["total"])
    check(quiz_count == 1, "test natijasi bazaga yozildi", errors)

    goal = await get_today_goal(USER_ID)
    check(int(goal["completed_quizzes"]) == 1, "kunlik reja testni sanadi", errors)

    # 4. Natijalar, reja, sozlamalar
    fake.calls.clear()
    await send_text("📊 Mening natijalarim")
    check("Yechilgan testlar: <b>1</b>" in last_text(fake), "statistika testni ko'rsatdi", errors)
    check("Biologiya" in last_text(fake), "so'nggi natijada fan nomi bor", errors)

    fake.calls.clear()
    await send_text("📅 Kunlik reja")
    check("Bugungi maqsad bajarildi" in last_text(fake), "kunlik maqsad bajarildi", errors)

    fake.calls.clear()
    await send_callback("goal:set:2:2")
    check("1/2" in last_text(fake), "kunlik maqsad 2/2 ga o'zgardi", errors)

    fake.calls.clear()
    await send_text("⚙️ Sozlamalar")
    check("O'rta" in last_text(fake), "sozlamalarda daraja ko'rsatildi", errors)

    fake.calls.clear()
    await send_callback("settings:notify")
    check("O'chirilgan" in last_text(fake), "bildirishnoma o'chirildi", errors)
    row = await get_user(USER_ID)
    check(row is not None and int(row["notifications_enabled"]) == 0, "sozlama bazada saqlandi", errors)

    fake.calls.clear()
    await send_callback("settings:notify")
    check("Yoqilgan" in last_text(fake), "bildirishnoma qayta yoqildi", errors)

    fake.calls.clear()
    await send_callback("settings:level:advanced")
    check("Yuqori" in last_text(fake), "daraja yuqori darajaga o'zgardi", errors)

    # 5. AI Ustoz (AI o'chirilgan, dars bazasi javobi)
    fake.calls.clear()
    await send_text("🧠 AI Ustoz")
    check("AI Ustoz" in last_text(fake), "AI rejimi ochildi", errors)
    check("⬅️ Chiqish" in last_reply_keyboard(fake), "chiqish tugmasi chiqdi", errors)

    fake.calls.clear()
    await send_text("Fotosintez nima?")
    check("Darslarimizdan mos javob" in last_text(fake), "AI dars bazasidan javob berdi", errors)
    check("Fotosintez" in last_text(fake), "javobda fotosintez mavzusi bor", errors)
    history = await get_history(USER_ID, 10)
    check(len(history) == 2, "suhbat tarixi bazaga yozildi", errors)

    fake.calls.clear()
    await send_text("⬅️ Chiqish")
    check("📚 Darslar" in last_reply_keyboard(fake), "AI rejimidan chiqildi", errors)

    fake.calls.clear()
    await send_text("tushunarsiz matn")
    check("tushunmadim" in last_text(fake).lower(), "noma'lum matnga javob berildi", errors)

    fake.calls.clear()
    await send_text("/id")
    check(str(USER_ID) in last_text(fake), "/id o'z ID raqamini qaytardi", errors)

    # 6. Admin panel va xabar yuborish
    fake.calls.clear()
    await send_text("/admin")
    check("Admin panel" in last_text(fake), "admin panel ochildi", errors)

    fake.calls.clear()
    await send_callback("admin:stats")
    check("Bot statistikasi" in last_text(fake), "admin statistikasi chiqdi", errors)
    check("60</b> savol" in last_text(fake), "statistikada savollar soni bor", errors)

    fake.calls.clear()
    await send_callback("admin:broadcast")
    check("Xabar yuborish" in last_text(fake), "xabar yuborish rejimi ochildi", errors)

    fake.calls.clear()
    await send_text("Sinov e'loni")
    check("Xabar ko'rinishi" in last_text(fake), "xabar ko'rinishi ko'rsatildi", errors)
    check("admin:broadcast_confirm" in last_inline_callbacks(fake), "tasdiqlash tugmasi bor", errors)

    fake.calls.clear()
    await send_callback("admin:broadcast_confirm")
    check("Yuborildi: <b>1</b>" in last_text(fake), "xabar bitta foydalanuvchiga yuborildi", errors)
    check(
        any(
            isinstance(method, SendMessage)
            and method.chat_id == USER_ID
            and method.text == "Sinov e'loni"
            for method in fake.calls
        ),
        "foydalanuvchiga aynan yuborilgan xabar yetib bordi",
        errors,
    )

    check(not errors, "barcha handlerlar xatosiz ishladi", errors)
    print("\nHANDLER_FLOW_OK")
    await bot.session.close()


def run() -> None:
    try:
        asyncio.run(main())
    finally:
        TEMP_DIR.cleanup()


if __name__ == "__main__":
    run()
