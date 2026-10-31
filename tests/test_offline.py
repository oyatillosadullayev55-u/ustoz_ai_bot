"""Telegramga ulanmasdan ma'lumotlar qatlami va AI zaxirasini tekshirish.

Ishga tushirish:
    .venv\\Scripts\\python.exe tests\\test_offline.py
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import socket
import sys
import tempfile
from datetime import datetime

import aiohttp
import aiosqlite

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEMP_DIR = tempfile.TemporaryDirectory(prefix="ustozai_test_")
os.environ["DATABASE_PATH"] = str(pathlib.Path(TEMP_DIR.name) / "test.db")
os.environ["BACKUP_DIR"] = str(pathlib.Path(TEMP_DIR.name) / "backups")
os.environ["BOT_TOKEN"] = "123456789:TEST_TOKEN_FOR_OFFLINE_TESTS"
os.environ["ADMIN_IDS"] = "999000001"
os.environ["AI_ENABLED"] = "false"
os.environ["AI_API_KEY"] = ""

from config import ConfigError, get_settings  # noqa: E402

get_settings.cache_clear()

from database.admin import get_admin_stats, get_all_user_ids  # noqa: E402
from database.chat import add_message, get_ai_usage, get_history  # noqa: E402
from database.content import (  # noqa: E402
    get_lesson,
    get_lessons,
    get_questions_by_ids,
    get_quiz_questions,
    get_subjects_with_counts,
    get_subjects_with_progress,
    search_lessons,
)
from database.db import (  # noqa: E402
    _ensure_lesson_columns,
    get_connection,
    init_db,
)
from database.favorites import (  # noqa: E402
    count_favorites,
    get_favorite_lessons,
    is_favorite,
    toggle_favorite,
)
from database.gamification import (  # noqa: E402
    award_xp,
    get_total_xp,
    get_weekly_xp,
)
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
from database.quizzes import (  # noqa: E402
    get_subject_best_score,
    save_quiz_result,
)
from database.users import (  # noqa: E402
    create_user,
    get_user,
    update_notifications,
)
from services.ai_service import ask_tutor  # noqa: E402
from services.backup import (  # noqa: E402
    create_backup_copy,
    create_export_csv,
)
from services.gamification import (  # noqa: E402
    ACHIEVEMENTS,
    XP_LESSON,
    get_achievements_with_state,
    get_leaderboard,
    get_profile,
    reward,
)
from services.health_server import (  # noqa: E402
    start_health_server,
    stop_health_server,
)
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


def check_config_cleaning() -> None:
    valid_token = "123456789:TEST_TOKEN_FOR_OFFLINE_TESTS"

    os.environ["BOT_TOKEN"] = f'"{valid_token}"'
    os.environ["ADMIN_IDS"] = '"999000001"'
    get_settings.cache_clear()
    settings = get_settings()
    check(settings.bot_token == valid_token, "BOT_TOKEN qo'shtirnoqlardan tozalandi")
    check(
        settings.admin_ids == frozenset({999000001}),
        "ADMIN_IDS qo'shtirnoqlardan tozalandi",
    )

    os.environ["BOT_TOKEN"] = f"BOT_TOKEN={valid_token}"
    get_settings.cache_clear()
    check(get_settings().bot_token == valid_token, "BOT_TOKEN= prefiksi tozalandi")

    os.environ["BOT_TOKEN"] = "not-a-token"
    get_settings.cache_clear()
    rejected = False
    try:
        get_settings()
    except ConfigError:
        rejected = True
    check(rejected, "noto'g'ri formatdagi BOT_TOKEN rad etildi")

    os.environ["BOT_TOKEN"] = valid_token
    os.environ["ADMIN_IDS"] = "999000001"
    get_settings.cache_clear()


async def run_tests() -> None:
    await init_db()
    await init_db()  # idempotent bo'lishi kerak

    subjects = await get_subjects_with_counts()
    check(len(subjects) == 8, "8 ta fan yuklandi")
    total_questions = sum(int(item["question_count"]) for item in subjects)
    check(total_questions == 140, "140 ta savol yuklandi")

    all_lessons = []
    for subject in subjects:
        all_lessons.extend(await get_lessons(int(subject["id"])))
    check(len(all_lessons) == 35, "35 ta dars yuklandi")

    content_ok = True
    for item in all_lessons:
        lesson = await get_lesson(int(item["id"]))
        points = json.loads(lesson["key_points"]) if lesson else []
        if not (
            lesson
            and len(str(lesson["summary"])) >= 80
            and isinstance(points, list)
            and len(points) == 3
            and all(str(point).strip() for point in points)
            and lesson["level"] in {"beginner", "intermediate", "advanced"}
            and 1 <= int(lesson["duration_min"]) <= 120
            and len(str(lesson["content"])) >= 900
        ):
            content_ok = False
            break
    check(
        content_ok,
        "har bir darsda mazmun, 3 asosiy fikr, daraja va davomiylik bor",
    )

    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT lesson_id, COUNT(*) AS total
            FROM questions
            GROUP BY lesson_id
            """
        )
        per_lesson = list(await cursor.fetchall())
    check(
        len(per_lesson) == 35
        and all(int(row["total"]) == 4 for row in per_lesson),
        "har bir darsda 4 tadan savol bor",
    )

    legacy_path = pathlib.Path(TEMP_DIR.name) / "legacy.db"
    async with aiosqlite.connect(legacy_path) as legacy:
        legacy.row_factory = aiosqlite.Row
        await legacy.execute(
            """
            CREATE TABLE lessons (
                id INTEGER PRIMARY KEY,
                subject_id INTEGER,
                title TEXT,
                content TEXT,
                order_index INTEGER,
                is_active INTEGER,
                created_at TEXT
            )
            """
        )
        await _ensure_lesson_columns(legacy)
        await legacy.commit()
        cursor = await legacy.execute("PRAGMA table_info(lessons)")
        legacy_columns = {str(row["name"]) for row in await cursor.fetchall()}
    check(
        {"summary", "key_points", "level", "duration_min"} <= legacy_columns,
        "eski baza yangi dars ustunlari bilan yangilandi",
    )

    os.environ.pop("PORT", None)
    check(
        await start_health_server() is None,
        "PORT bo'lmasa health server ochilmaydi",
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        free_port = int(sock.getsockname()[1])
    os.environ["PORT"] = str(free_port)
    health_runner = await start_health_server()
    check(health_runner is not None, "PORT berilganda health server ishga tushdi")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://127.0.0.1:{free_port}/health"
            ) as response:
                payload = await response.json()
        check(
            response.status == 200 and payload["status"] == "ok",
            "health server /health manzilida 200 qaytardi",
        )
    finally:
        await stop_health_server(health_runner)
        os.environ.pop("PORT", None)

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
    check(
        await get_subject_best_score(USER_ID, 5) == 80,
        "fan bo'yicha eng yaxshi natija saqlandi",
    )
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

    check(await get_total_xp(USER_ID) == 0, "yangi foydalanuvchining XP balansi 0")
    lesson_reward = await reward(
        USER_ID, XP_LESSON, "lesson", once_key="lesson:101"
    )
    check(lesson_reward.xp_gained >= XP_LESSON, "dars uchun XP qo'shildi")
    check(
        any(item.code == "first_lesson" for item in lesson_reward.achievements),
        "birinchi dars yutug'i ochildi",
    )
    check(
        lesson_reward.xp == await get_total_xp(USER_ID),
        "XP balansi bazada saqlandi",
    )
    check(
        await award_xp(USER_ID, XP_LESSON, "lesson", once_key="lesson:101")
        is None,
        "bir marta beriladigan XP qayta qo'shilmadi",
    )

    profile = await get_profile(USER_ID)
    check(
        profile["rank"].name == "Yangi boshlovchi"
        and int(profile["xp"]) == lesson_reward.xp
        and int(profile["total_achievements"]) == len(ACHIEVEMENTS),
        "profil daraja va yutuqlar sonini ko'rsatdi",
    )
    check(
        await get_weekly_xp(USER_ID) == lesson_reward.xp,
        "haftalik XP hisoblandi",
    )

    achievement_states = {
        item.code: state
        for item, state in await get_achievements_with_state(USER_ID)
    }
    check(
        achievement_states["first_lesson"] is True,
        "birinchi dars yutug'i holati saqlandi",
    )
    check(
        achievement_states["five_lessons"] is False,
        "ochilmagan yutuq yopiq holatda",
    )

    board = await get_leaderboard(USER_ID)
    check(
        len(board["rows"]) == 1
        and int(board["rows"][0]["week_xp"]) == lesson_reward.xp
        and board["user_rank"] == 1,
        "haftalik reyting foydalanuvchini ko'rsatdi",
    )

    check(await toggle_favorite(USER_ID, 501), "dars sevimlilarga qo'shildi")
    check(await is_favorite(USER_ID, 501), "sevimli holati bazada saqlandi")
    favorites = await get_favorite_lessons(USER_ID)
    check(
        len(favorites) == 1 and int(favorites[0]["id"]) == 501,
        "sevimli darslar ro'yxati ishladi",
    )
    check(
        await toggle_favorite(USER_ID, 501) is False,
        "sevimli darslardan olib tashlandi",
    )
    for favorite_id in (101, 102, 201, 301, 501):
        await toggle_favorite(USER_ID, favorite_id)
    check(await count_favorites(USER_ID) == 5, "5 ta sevimli dars saqlandi")
    favorite_reward = await reward(USER_ID, 0, "favorite")
    check(
        any(item.code == "favorite_5" for item in favorite_reward.achievements),
        "sevimlilar yutug'i ochildi",
    )

    subjects_with_progress = await get_subjects_with_progress(USER_ID)
    english = next(
        item for item in subjects_with_progress if int(item["id"]) == 1
    )
    check(
        int(english["completed_count"]) == 1
        and int(english["lesson_count"]) == 2,
        "fan progressi tugatilgan darsni sanadi",
    )

    backup_path = await create_backup_copy()
    check(
        backup_path.exists() and backup_path.stat().st_size > 0,
        "baza zaxira nusxasi yaratildi",
    )
    backup_path.unlink()

    csv_path, csv_rows = await create_export_csv()
    try:
        csv_text = csv_path.read_text(encoding="utf-8-sig")
    finally:
        csv_path.unlink()
    check(
        csv_rows == 1
        and "Test O'quvchi" in csv_text
        and csv_text.splitlines()[0].startswith("telegram_id"),
        "CSV eksport foydalanuvchini o'z ichiga oldi",
    )

    await add_message(USER_ID, "user", "Fotosintez nima?")
    await add_message(USER_ID, "assistant", "Fotosintez - yorug'lik yordamida...")
    usage_count, last_at = await get_ai_usage(USER_ID)
    check(usage_count == 1 and last_at is not None, "AI foydalanish limiti sanaldi")
    history = await get_history(USER_ID, 10)
    check(
        [item["role"] for item in history] == ["user", "assistant"],
        "suhbat tarixi to'g'ri tartibda",
    )

    answer, source, related = await ask_tutor(
        "fotosintez nima?",
        [{"role": item["role"], "content": item["message"]} for item in history],
        "beginner",
    )
    check(source == "lessons", "AI o'chirilganda dars bazasi ishlatildi")
    check("Fotosintez" in answer, "zaxira javobda fotosintez darsi bor")
    check("AI kaliti" in answer, "foydalanuvchiga AI sozlamasi holati aytildi")
    check(
        any(lesson_id == 501 for lesson_id, _ in related),
        "zaxira javob aloqador darsni qaytardi",
    )

    lesson_501 = await get_lesson(501)
    check(lesson_501 is not None, "dars konteksti uchun 501-dars topildi")
    context_answer, context_source, context_related = await ask_tutor(
        "hujayra nima?",
        [],
        "beginner",
        {
            "lesson_id": 501,
            "subject": f"{lesson_501['subject_emoji']} {lesson_501['subject_name']}",
            "title": lesson_501["title"],
            "summary": lesson_501["summary"],
            "content": lesson_501["content"],
        },
    )
    check(
        context_related == [(501, str(lesson_501["title"]))],
        "dars konteksti aloqador darsni qaytardi",
    )
    check(
        context_source == "lessons"
        and "Shu darsdan tushuntirish" in context_answer
        and "hujayra" in context_answer.lower(),
        "dars konteksti bilan zaxira javob shu darsdan olindi",
    )

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
    check(int(admin_stats["questions"]) == 140, "admin statistikasi 140 savolni ko'rsatdi")
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
        check_config_cleaning()
        asyncio.run(run_tests())
    finally:
        TEMP_DIR.cleanup()


if __name__ == "__main__":
    main()
