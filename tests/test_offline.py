"""Telegramga ulanmasdan ma'lumotlar qatlami va AI zaxirasini tekshirish.

Ishga tushirish:
    .venv\\Scripts\\python.exe tests\\test_offline.py
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import tempfile
from datetime import datetime

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEMP_DIR = tempfile.TemporaryDirectory(prefix="ustozai_test_")
os.environ["DATABASE_PATH"] = str(pathlib.Path(TEMP_DIR.name) / "test.db")
os.environ["BOT_TOKEN"] = "123456789:TEST_TOKEN_FOR_OFFLINE_TESTS"
os.environ["ADMIN_IDS"] = "999000001"
os.environ["AI_ENABLED"] = "false"
os.environ["AI_API_KEY"] = ""

from config import get_settings  # noqa: E402

get_settings.cache_clear()

from database.admin import get_admin_stats, get_all_user_ids  # noqa: E402
from database.chat import add_message, get_ai_usage, get_history  # noqa: E402
from database.content import (  # noqa: E402
    get_questions_by_ids,
    get_quiz_questions,
    get_subjects_with_counts,
    search_lessons,
)
from database.db import get_connection, init_db  # noqa: E402
from database.goals import (  # noqa: E402
    get_pending_reminders,
    get_today_goal,
    increment_goal,
    set_goal_targets,
)
from database.progress import (  # noqa: E402
    complete_lesson,
    get_activity_stats,
    get_completed_lesson_ids,
    get_recent_results,
    get_user_stats,
    mark_lesson_started,
)
from database.quizzes import save_quiz_result  # noqa: E402
from database.users import (  # noqa: E402
    create_user,
    get_user,
    update_notifications,
)
from services.ai_service import ask_tutor  # noqa: E402
from services.reminders import format_reminder  # noqa: E402
from time_utils import (  # noqa: E402
    LOCAL_TZ,
    local_today,
    seconds_until_local_time,
)

USER_ID = 999000001


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"OK - {message}")


async def run_tests() -> None:
    await init_db()
    await init_db()  # idempotent bo'lishi kerak

    subjects = await get_subjects_with_counts()
    check(len(subjects) == 10, "10 ta fan yuklandi")
    check(
        sum(int(item["question_count"]) for item in subjects) == 60,
        "60 ta savol yuklandi",
    )

    questions = await get_quiz_questions(5, 5)
    check(len(questions) == 5, "test uchun 5 ta savol tanlandi")
    check(
        all(
            all(
                question[field]
                for field in ("option_a", "option_b", "option_c", "option_d")
            )
            for question in questions
        ),
        "har bir savolda 4 ta variant bor",
    )
    check(
        all(0 <= int(question["correct_option"]) <= 3 for question in questions),
        "to'g'ri javoblar 0-3 oralig'ida",
    )

    question_map = await get_questions_by_ids(
        [questions[0]["id"], questions[1]["id"]]
    )
    check(len(question_map) == 2, "savollar ID bo'yicha bitta so'rovda olindi")
    check(
        question_map[questions[0]["id"]]["question_text"]
        == questions[0]["question_text"],
        "ID bo'yicha olingan savol matni mos keldi",
    )
    check(await get_questions_by_ids([]) == {}, "bo'sh ro'yxat uchun lug'at bo'sh")

    noon = datetime(2026, 10, 25, 12, 0, tzinfo=LOCAL_TZ)
    check(
        seconds_until_local_time(19, now=noon) == 7 * 3600,
        "keyingi eslatmagacha vaqt to'g'ri hisoblandi",
    )
    check(
        seconds_until_local_time(9, now=noon) == 21 * 3600,
        "o'tib ketgan vaqt ertangi kunga surildi",
    )

    hits = await search_lessons("fotosintez nima")
    check(bool(hits), "dars bazasidan qidiruv natija qaytardi")
    check(
        any("Fotosintez" in hit["title"] for hit in hits),
        "fotosintez mavzusi topildi",
    )

    await create_user(
        telegram_id=USER_ID,
        full_name="Test O'quvchi",
        username="test_user",
        language="uz",
        level="beginner",
    )
    await create_user(
        telegram_id=USER_ID,
        full_name="Dublikat",
        username=None,
        language="uz",
        level="advanced",
    )
    user = await get_user(USER_ID)
    check(user is not None and user["full_name"] == "Test O'quvchi",
          "takroriy ro'yxatdan o'tish dublikat yaratmadi")

    goal = await get_today_goal(USER_ID)
    check(
        int(goal["target_lessons"]) == 1
        and int(goal["target_quizzes"]) == 1
        and int(goal["completed_lessons"]) == 0,
        "kunlik maqsad standart qiymatlar bilan yaratildi",
    )

    await mark_lesson_started(USER_ID, 101)
    completed_first = await complete_lesson(USER_ID, 101)
    completed_second = await complete_lesson(USER_ID, 101)
    check(completed_first is True, "dars birinchi marta tugatildi")
    check(completed_second is False, "dars takroran tugatilmaydi")
    await increment_goal(USER_ID, lessons=1)

    completed_ids = await get_completed_lesson_ids(USER_ID, 1)
    check(101 in completed_ids, "tugatilgan darslar ro'yxatida 101 bor")

    goal = await get_today_goal(USER_ID)
    check(int(goal["completed_lessons"]) == 1, "kunlik reja dars hisobini oshirdi")

    await set_goal_targets(USER_ID, 2, 2)
    goal = await get_today_goal(USER_ID)
    check(
        int(goal["target_lessons"]) == 2 and int(goal["target_quizzes"]) == 2,
        "kunlik maqsad yangilandi",
    )

    percent = await save_quiz_result(
        user_id=USER_ID,
        subject_id=5,
        total_questions=5,
        correct_answers=4,
    )
    check(percent == 80, "test natijasi 80% hisoblandi")
    await increment_goal(USER_ID, quizzes=1)

    pending = await get_pending_reminders(local_today())
    check(
        len(pending) == 1 and int(pending[0]["user_id"]) == USER_ID,
        "bajarilmagan reja uchun eslatma ro'yxati topildi",
    )
    reminder_text = format_reminder(str(pending[0]["full_name"]), 2, 2, 1, 1)
    check(
        "Kunlik eslatma" in reminder_text and reminder_text.count("1/2") == 2,
        "eslatma matni to'g'ri shakllandi",
    )

    stats = await get_user_stats(USER_ID)
    check(int(stats["quizzes"]) == 1, "statistikada 1 test bor")
    check(round(float(stats["average"])) == 80, "o'rtacha natija 80%")
    check(int(stats["best"]) == 80, "eng yuqori natija 80%")
    check(int(stats["lessons"]) == 1, "statistikada 1 dars bor")

    recent = await get_recent_results(USER_ID)
    check(
        len(recent) == 1 and recent[0]["subject_name"] == "Biologiya",
        "so'nggi natijada Biologiya ko'rsatildi",
    )

    activity = await get_activity_stats(USER_ID)
    check(int(activity["streak"]) == 1, "streak 1 kunga teng")
    check(int(activity["active_days"]) == 1, "bitta faol kun qayd etildi")

    await add_message(USER_ID, "user", "Fotosintez nima?")
    await add_message(USER_ID, "assistant", "Fotosintez - yorug'lik yordamida...")
    usage_count, last_at = await get_ai_usage(USER_ID)
    check(usage_count == 1 and last_at is not None, "AI foydalanish limiti sanaldi")
    history = await get_history(USER_ID, 10)
    check(
        [item["role"] for item in history] == ["user", "assistant"],
        "suhbat tarixi to'g'ri tartibda",
    )

    answer, source = await ask_tutor(
        "fotosintez nima?",
        [{"role": item["role"], "content": item["message"]} for item in history],
        "beginner",
    )
    check(source == "lessons", "AI o'chirilganda dars bazasi ishlatildi")
    check("Fotosintez" in answer, "zaxira javobda fotosintez darsi bor")
    check("AI kaliti" in answer, "foydalanuvchiga AI sozlamasi holati aytildi")

    check(await update_notifications(USER_ID, False), "bildirishnoma o'chirildi")
    user = await get_user(USER_ID)
    check(int(user["notifications_enabled"]) == 0, "sozlama bazada saqlandi")
    check(
        await get_pending_reminders(local_today()) == [],
        "bildirishnoma o'chirilganda eslatma ro'yxati bo'sh",
    )
    check(await update_notifications(USER_ID, True), "bildirishnoma yoqildi")

    ids = await get_all_user_ids(notifications_only=True)
    check(ids == [USER_ID], "xabar qabul qiluvchilar ro'yxati to'g'ri")

    admin_stats = await get_admin_stats()
    check(int(admin_stats["total_users"]) == 1, "admin statistikasi foydalanuvchini ko'rsatdi")
    check(int(admin_stats["quizzes"]) == 1, "admin statistikasi testni ko'rsatdi")
    check(int(admin_stats["questions"]) == 60, "admin statistikasi 60 savolni ko'rsatdi")
    check(
        round(float(admin_stats["average_score"])) == 80,
        "admin statistikasi o'rtachani ko'rsatdi",
    )

    async with get_connection() as db:
        cursor = await db.execute("SELECT COUNT(*) AS total FROM users")
        total = int((await cursor.fetchone())["total"])
    check(total == 1, "bazada faqat bitta test foydalanuvchisi bor")

    print("\nOFFLINE_TESTS_OK")


def main() -> None:
    try:
        asyncio.run(run_tests())
    finally:
        TEMP_DIR.cleanup()


if __name__ == "__main__":
    main()
