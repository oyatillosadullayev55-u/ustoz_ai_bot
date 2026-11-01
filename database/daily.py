"""Kunlik sovg'a, kunlik savol va haftalik missiyalar uchun so'rovlar."""

from __future__ import annotations

import zlib
from datetime import UTC, date, datetime, timedelta

import aiosqlite

from database.db import get_connection
from time_utils import LOCAL_TZ, local_now, utc_now

DAILY_CORRECT_XP = 10
DAILY_WRONG_XP = 2


async def get_daily_question(day: str) -> aiosqlite.Row | None:
    """Kun uchun savolni barqaror tanlaydi; barcha foydalanuvchilar bir xil ko'radi."""
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total
            FROM questions AS q
            JOIN lessons AS l ON l.id = q.lesson_id
            JOIN subjects AS s ON s.id = l.subject_id
            WHERE l.is_active = 1 AND s.is_active = 1
            """
        )
        count_row = await cursor.fetchone()
        total = int(count_row["total"]) if count_row is not None else 0
        if total == 0:
            return None

        offset = zlib.crc32(day.encode("utf-8")) % total
        cursor = await db.execute(
            """
            SELECT q.id, q.lesson_id, q.question_text, q.option_a, q.option_b,
                   q.option_c, q.option_d, q.correct_option, q.explanation,
                   l.title AS lesson_title, s.name AS subject_name,
                   s.emoji AS subject_emoji
            FROM questions AS q
            JOIN lessons AS l ON l.id = q.lesson_id
            JOIN subjects AS s ON s.id = l.subject_id
            WHERE l.is_active = 1 AND s.is_active = 1
            ORDER BY q.id
            LIMIT 1 OFFSET ?
            """,
            (offset,),
        )
        return await cursor.fetchone()


async def get_daily_answer(user_id: int, day: str) -> aiosqlite.Row | None:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT question_id, selected_option, is_correct, answered_at
            FROM daily_answers
            WHERE user_id = ? AND answer_date = ?
            """,
            (user_id, day),
        )
        return await cursor.fetchone()


async def save_daily_answer(
    user_id: int,
    day: str,
    question_id: int,
    selected_option: int,
    is_correct: bool,
) -> bool:
    """Javobni yozadi; bugun allaqachon javob berilgan bo'lsa False."""
    async with get_connection() as db:
        cursor = await db.execute(
            """
            INSERT INTO daily_answers (
                user_id, answer_date, question_id, selected_option,
                is_correct, answered_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, answer_date) DO NOTHING
            """,
            (user_id, day, question_id, selected_option, int(is_correct), utc_now()),
        )
    return cursor.rowcount > 0


async def get_daily_answer_days(user_id: int) -> set[str]:
    async with get_connection() as db:
        cursor = await db.execute(
            "SELECT answer_date FROM daily_answers WHERE user_id = ?",
            (user_id,),
        )
        return {str(row["answer_date"]) for row in await cursor.fetchall()}


async def has_daily_gift(user_id: int, day: str) -> bool:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT 1 FROM xp_log
            WHERE user_id = ? AND reason = 'gift' AND once_key = ?
            """,
            (user_id, f"gift:{day}"),
        )
        return await cursor.fetchone() is not None


async def get_gift_days(user_id: int) -> set[str]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT once_key FROM xp_log
            WHERE user_id = ? AND reason = 'gift' AND once_key IS NOT NULL
            """,
            (user_id,),
        )
        days: set[str] = set()
        for row in await cursor.fetchall():
            key = str(row["once_key"])
            if ":" in key:
                days.add(key.split(":", 1)[1])
        return days


def week_start_date() -> date:
    today = local_now().date()
    return today - timedelta(days=today.weekday())


def current_week_key() -> str:
    year, week, _ = local_now().isocalendar()
    return f"{year}-W{week:02d}"


def _week_start_utc() -> str:
    start = datetime.combine(
        week_start_date(), datetime.min.time(), tzinfo=LOCAL_TZ
    )
    return start.astimezone(UTC).isoformat(timespec="seconds")


async def get_weekly_activity(user_id: int) -> dict[str, int]:
    """Shu haftadagi dars, test va AI savollari soni."""
    cutoff = _week_start_utc()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM study_progress
                 WHERE user_id = ? AND status = 'completed'
                   AND completed_at >= ?) AS lessons,
                (SELECT COUNT(*) FROM quiz_results
                 WHERE user_id = ? AND created_at >= ?) AS quizzes,
                (SELECT COUNT(*) FROM chat_history
                 WHERE user_id = ? AND role = 'user'
                   AND created_at >= ?) AS ai_messages
            """,
            (user_id, cutoff, user_id, cutoff, user_id, cutoff),
        )
        row = await cursor.fetchone()

    if row is None:
        return {"lessons": 0, "quizzes": 0, "ai_messages": 0}
    return {
        "lessons": int(row["lessons"]),
        "quizzes": int(row["quizzes"]),
        "ai_messages": int(row["ai_messages"]),
    }


async def get_claimed_missions(user_id: int) -> set[str]:
    """Shu haftada olingan missiya kodlari."""
    week = current_week_key()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT once_key FROM xp_log
            WHERE user_id = ? AND reason = 'mission' AND once_key LIKE ?
            """,
            (user_id, f"mission:%:{week}"),
        )
        codes: set[str] = set()
        for row in await cursor.fetchall():
            parts = str(row["once_key"]).split(":")
            if len(parts) >= 3:
                codes.add(parts[1])
        return codes
