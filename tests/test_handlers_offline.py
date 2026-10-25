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
from datetime import UTC, datetime

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEMP_DIR = tempfile.TemporaryDirectory(prefix="ustozai_handlers_")
os.environ["DATABASE_PATH"] = str(pathlib.Path(TEMP_DIR.name) / "handlers.db")
os.environ["BOT_TOKEN"] = "123456789:TEST_TOKEN_FOR_HANDLER_TESTS"
os.environ["ADMIN_IDS"] = "999000001"
os.environ["AI_ENABLED"] = "false"
os.environ["AI_API_KEY"] = ""
os.environ["AI_MIN_INTERVAL"] = "0"

from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ChatType, ParseMode  # noqa: E402
from aiogram.fsm.storage.memory import MemoryStorage  # noqa: E402
from aiogram.methods import (  # noqa: E402
    EditMessageCaption,
    EditMessageText,
    SendMessage,
    SendPhoto,
)
from aiogram.types import (  # noqa: E402
    CallbackQuery,
    Chat,
    InlineKeyboardMarkup,
    Message,
    PhotoSize,
    ReplyKeyboardMarkup,
    Update,
    User,
)

from config import get_settings  # noqa: E402

get_settings.cache_clear()

from database.chat import get_history  # noqa: E402
from database.content import get_lesson, get_question  # noqa: E402
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
from services.lesson_media import get_lesson_image_path  # noqa: E402
from services.reminders import send_due_reminders  # noqa: E402
from time_utils import local_today  # noqa: E402

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


def sent_captions(session: FakeSession) -> list[str]:
    captions: list[str] = []
    for method in session.calls:
        if isinstance(method, (SendPhoto, EditMessageCaption)) and method.caption:
            captions.append(method.caption)
    return captions


def last_caption(session: FakeSession) -> str:
    captions = sent_captions(session)
    return captions[-1] if captions else ""


def last_inline_callbacks(session: FakeSession) -> list[str]:
    callbacks: list[str] = []
    for method in session.calls:
        if isinstance(
            method,
            (SendMessage, EditMessageText, SendPhoto, EditMessageCaption),
        ):
            markup = method.reply_markup
            if isinstance(markup, InlineKeyboardMarkup):
                callbacks = [
                    button.callback_data
                    for row in markup.inline_keyboard
                    for button in row
                    if button.callback_data
                ]
    return callbacks


def last_inline_markup(session: FakeSession) -> InlineKeyboardMarkup | None:
    for method in reversed(session.calls):
        if isinstance(
            method,
            (SendMessage, EditMessageText, SendPhoto, EditMessageCaption),
        ):
            markup = method.reply_markup
            if isinstance(markup, InlineKeyboardMarkup):
                return markup
    return None


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

    async with get_connection() as db:
        cursor = await db.execute("SELECT id FROM lessons WHERE is_active = 1")
        lesson_ids = [int(row["id"]) for row in await cursor.fetchall()]

    check(len(lesson_ids) == 20, "bazada 20 ta dars bor", errors)
    check(
        all(
            get_lesson_image_path(lesson_id) is not None
            for lesson_id in lesson_ids
        ),
        "har bir dars uchun rasm fayli mavjud",
        errors,
    )

    captions_fit = True
    for lesson_id in lesson_ids:
        lesson = await get_lesson(lesson_id)
        if lesson is None or any(
            len(lessons.build_lesson_card(lesson, completed=completed)) > 1024
            for completed in (False, True)
        ):
            captions_fit = False
            break
    check(
        captions_fit,
        "dars kartochkalari Telegram caption limitiga sig'adi",
        errors,
    )

    user = User(id=USER_ID, is_bot=False, first_name="Test")
    bot_user = User(id=BOT_ID, is_bot=True, first_name="UstozAI", username="ustoz_bot")
    chat = Chat(id=USER_ID, type=ChatType.PRIVATE)
    update_id = 0

    async def send_text(text: str) -> None:
        nonlocal update_id
        update_id += 1
        message = Message(
            message_id=update_id,
            date=datetime.now(UTC),
            chat=chat,
            from_user=user,
            text=text,
        ).as_(bot)
        await dispatcher.feed_update(
            bot, Update(update_id=update_id, message=message)
        )

    callback_message = Message(
        message_id=9000,
        date=datetime.now(UTC),
        chat=chat,
        from_user=bot_user,
        text="inline",
    ).as_(bot)

    photo_message = Message(
        message_id=9001,
        date=datetime.now(UTC),
        chat=chat,
        from_user=bot_user,
        photo=[
            PhotoSize(
                file_id="test-photo-id",
                file_unique_id="test-photo-unique",
                width=1280,
                height=720,
            )
        ],
        caption="Dars kartochkasi",
    ).as_(bot)

    async def send_callback(data: str, message: Message | None = None) -> None:
        nonlocal update_id
        update_id += 1
        callback = CallbackQuery(
            id=f"cb-{update_id}",
            from_user=user,
            chat_instance="test-chat-instance",
            message=message or callback_message,
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
    check(
        row is not None and row["level"] == "intermediate",
        "foydalanuvchi bazaga saqlandi",
        errors,
    )
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
    check("🖼️" in last_text(fake), "darslar bo'limi rasmli kartani tanishtirdi", errors)

    fake.calls.clear()
    await send_callback("lesson:subject:5")
    check("lesson:view:501" in last_inline_callbacks(fake), "Biologiya darslari chiqdi", errors)

    fake.calls.clear()
    await send_callback("lesson:view:501")
    check(
        "Hujayra tuzilishi" in last_caption(fake),
        "dars rasmli kartochka bilan ochildi",
        errors,
    )
    check(
        any(isinstance(method, SendPhoto) for method in fake.calls),
        "dars rasmi yuborildi",
        errors,
    )
    check(
        "Asosiy fikrlar" in last_caption(fake),
        "kartochkada asosiy fikrlar ko'rsatildi",
        errors,
    )
    card_callbacks = last_inline_callbacks(fake)
    check(
        "lesson:read:501" in card_callbacks
        and "lesson:ask:501" in card_callbacks,
        "batafsil o'qish va AI so'rash tugmalari bor",
        errors,
    )
    check(
        "lesson:view:502" in card_callbacks,
        "keyingi darsga o'tish tugmasi bor",
        errors,
    )

    fake.calls.clear()
    await send_callback("lesson:view:502", message=photo_message)
    check("Fotosintez" in last_caption(fake), "keyingi darsga o'tildi", errors)
    check(
        "lesson:view:501" in last_inline_callbacks(fake),
        "oldingi darsga qaytish tugmasi bor",
        errors,
    )

    fake.calls.clear()
    await send_callback("lesson:read:501", message=photo_message)
    details_text = last_text(fake)
    check(
        "Hujayra tuzilishi" in details_text
        and "Maqsad" in details_text
        and "Mini mashq" in details_text,
        "batafsil dars matni alohida ekranda ochildi",
        errors,
    )
    check(
        "lesson:view:501" in last_inline_callbacks(fake),
        "batafsil ekranda kartochkaga qaytish tugmasi bor",
        errors,
    )
    details_message = Message(
        message_id=9002,
        date=datetime.now(UTC),
        chat=chat,
        from_user=bot_user,
        text=details_text,
        reply_markup=last_inline_markup(fake),
    ).as_(bot)

    fake.calls.clear()
    await send_callback("lesson:complete:501", message=details_message)
    check(
        "Tugatilgan" in last_text(fake),
        "dars batafsil ekranda tugatilgan deb belgilandi",
        errors,
    )
    check(
        "lesson:complete:501" not in last_inline_callbacks(fake),
        "tugatish tugmasi olib tashlandi",
        errors,
    )
    goal = await get_today_goal(USER_ID)
    check(int(goal["completed_lessons"]) == 1, "kunlik reja darsni sanadi", errors)

    fake.calls.clear()
    await send_callback("lesson:view:501", message=details_message)
    check(
        "Hujayra tuzilishi" in last_caption(fake)
        and "Tugatilgan" in last_caption(fake),
        "batafsil ekrandan kartochkaga qaytildi",
        errors,
    )
    check(
        "lesson:complete:501" not in last_inline_callbacks(fake),
        "tugatilgan darsda tugatish tugmasi yo'q",
        errors,
    )

    fake.calls.clear()
    await send_callback("lesson:subject:5", message=photo_message)
    check(
        "BIOLOGIYA" in last_text(fake),
        "foto kartochkadan darslar ro'yxatiga qaytildi",
        errors,
    )

    # 2b. Dars qidiruvi
    fake.calls.clear()
    await send_text("/qidiruv fotosintez")
    check("Qidiruv natijalari" in last_text(fake), "qidiruv natijalari chiqdi", errors)
    check("Fotosintez" in last_text(fake), "qidiruvda fotosintez darsi topildi", errors)
    search_callbacks = [
        item
        for item in last_inline_callbacks(fake)
        if item.startswith("lesson:view:")
    ]
    check(bool(search_callbacks), "qidiruv natijasida dars tugmasi bor", errors)

    fake.calls.clear()
    await send_callback(search_callbacks[0])
    check(
        "Fotosintez" in last_caption(fake),
        "qidiruvdan dars rasmli ochildi",
        errors,
    )

    fake.calls.clear()
    await send_text("/qidiruv")
    check("Dars qidiruvi" in last_text(fake), "qidiruv bo'sh bo'lsa yo'riqnoma chiqdi", errors)

    fake.calls.clear()
    await send_text("/qidiruv zzzzz")
    check("topilmadi" in last_text(fake).lower(), "natijasiz qidiruv xabari chiqdi", errors)

    # 3. Test oqimi: birinchi savolga xato, qolganlariga to'g'ri javob beriladi
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
        option = correct if question_number > 1 else (correct + 1) % 4

        fake.calls.clear()
        await send_callback(f"quiz:answer:{question['id']}:{option}")

        if question_number < 5:
            check(
                f"savol {question_number + 1}/5" in last_text(fake),
                f"{question_number + 1}-savolga o'tildi",
                errors,
            )

    texts = sent_texts(fake)
    check(
        any("Test yakunlandi" in text for text in texts),
        "test yakunlandi xabari chiqdi",
        errors,
    )
    check(
        any("4/5" in text and "80%" in text for text in texts),
        "natija 4/5 va 80% hisoblandi",
        errors,
    )
    check(
        any("Xatolar tahlili" in text for text in texts),
        "xato javoblar tahlili yuborildi",
        errors,
    )
    review = next((text for text in texts if "Xatolar tahlili" in text), "")
    check(
        "To'g'ri javob" in review and "Siz tanladingiz" in review,
        "tahlilda tanlangan va to'g'ri javob ko'rsatildi",
        errors,
    )

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
    check(
        row is not None and int(row["notifications_enabled"]) == 0,
        "sozlama bazada saqlandi",
        errors,
    )

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

    # 5b. Darsdagi AI Ustoz konteksti
    fake.calls.clear()
    await send_callback("lesson:ask:501", message=callback_message)
    check(
        "dars bo'yicha" in last_text(fake).lower(),
        "dars bo'yicha AI rejimi ochildi",
        errors,
    )
    check(
        "Hujayra tuzilishi" in last_text(fake),
        "AI rejimida dars nomi ko'rsatildi",
        errors,
    )
    check(
        "⬅️ Chiqish" in last_reply_keyboard(fake),
        "dars AI rejimida chiqish tugmasi bor",
        errors,
    )

    fake.calls.clear()
    await send_text("Hujayra nima?")
    check(
        "Shu darsdan tushuntirish" in last_text(fake),
        "AI dars konteksti bilan javob berdi",
        errors,
    )
    check(
        "hujayra" in last_text(fake).lower(),
        "javob shu dars mazmunidan olindi",
        errors,
    )

    fake.calls.clear()
    await send_text("⬅️ Chiqish")
    check(
        "📚 Darslar" in last_reply_keyboard(fake),
        "dars AI rejimidan chiqildi",
        errors,
    )

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
    check("80</b> savol" in last_text(fake), "statistikada savollar soni bor", errors)

    fake.calls.clear()
    await send_callback("admin:broadcast")
    check("Xabar yuborish" in last_text(fake), "xabar yuborish rejimi ochildi", errors)

    fake.calls.clear()
    await send_text("Sinov e'loni")
    check("Xabar ko'rinishi" in last_text(fake), "xabar ko'rinishi ko'rsatildi", errors)
    check(
        "admin:broadcast_confirm" in last_inline_callbacks(fake),
        "tasdiqlash tugmasi bor",
        errors,
    )

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

    # 7. Kunlik eslatma (reja 2/2, bajarilgan 1 dars + 1 test)
    fake.calls.clear()
    sent, failed = await send_due_reminders(bot, goal_date=local_today())
    check(
        sent == 1 and failed == 0,
        "kunlik eslatma bitta foydalanuvchiga yuborildi",
        errors,
    )
    check(
        any(
            isinstance(method, SendMessage)
            and method.chat_id == USER_ID
            and "Kunlik eslatma" in (method.text or "")
            and "1/2" in (method.text or "")
            for method in fake.calls
        ),
        "eslatma matni foydalanuvchiga yetib bordi",
        errors,
    )

    print("\nHANDLER_FLOW_OK")
    await bot.session.close()


def run() -> None:
    try:
        asyncio.run(main())
    finally:
        TEMP_DIR.cleanup()


if __name__ == "__main__":
    run()
