"""Dars jarayoni va foydalanuvchi statistikasi."""

from __future__ import annotations

import aiosqlite

from database.db import get_connection
from time_utils import calculate_streak, utc_now


async def mark_lesson_started(user_id: int, lesson_id: int) -> None:
    now = utc_now()
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO study_progress (user_id, lesson_id, status, completed_at, updated_at)
            VALUES (?, ?, 'started', NULL, ?)
            ON CONFLICT(user_id, lesson_id) DO UPDATE SET
                updated_at = excluded.updated_at
            """,
            (user_id, lesson_id, now),
        )


async def complete_lesson(user_id: int, lesson_id: int) -> bool:
    """Darsni tugatilgan deb belgilaydi. Birinchi marta bo'lsa True qaytaradi."""
    now = utc_now()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT status FROM study_progress
            WHERE user_id = ? AND lesson_id = ?
            """,
            (user_id, lesson_id),
        )
        row = await cursor.fetchone()
        if row is not None and row["status"] == "completed":
            return False

        await db.execute(
            """
            INSERT INTO study_progress (user_id, lesson_id, status, completed_at, updated_at)
            VALUES (?, ?, 'completed', ?, ?)
            ON CONFLICT(user_id, lesson_id) DO UPDATE SET
                status = 'completed',
                completed_at = excluded.completed_at,
                updated_at = excluded.updated_at
            """,
            (user_id, lesson_id, now, now),
        )
        return True


async def get_completed_lesson_ids(user_id: int, subject_id: int) -> set[int]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT sp.lesson_id
            FROM study_progress AS sp
            JOIN lessons AS l ON l.id = sp.lesson_id
            WHERE sp.user_id = ? AND sp.status = 'completed' AND l.subject_id = ?
            """,
            (user_id, subject_id),
        )
        return {row["lesson_id"] for row in await cursor.fetchall()}


async def get_user_stats(user_id: int) -> dict[str, int | float]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total,
                   COALESCE(AVG(score_percent), 0) AS average,
                   COALESCE(MAX(score_percent), 0) AS best
            FROM quiz_results
            WHERE user_id = ?
            """,
            (user_id,),
        )
        quiz_row = await cursor.fetchone()

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total
            FROM study_progress
            WHERE user_id = ? AND status = 'completed'
            """,
            (user_id,),
        )
        lessons_row = await cursor.fetchone()

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total
            FROM chat_history
            WHERE user_id = ? AND role = 'user'
            """,
            (user_id,),
        )
        ai_row = await cursor.fetchone()

    return {
        "quizzes": int(quiz_row["total"]),
        "average": float(quiz_row["average"]),
        "best": int(quiz_row["best"]),
        "lessons": int(lessons_row["total"]),
        "ai_messages": int(ai_row["total"]),
    }


async def get_recent_results(user_id: int, limit: int = 5) -> list[aiosqlite.Row]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT qr.total_questions, qr.correct_answers, qr.score_percent,
                   qr.created_at, s.name AS subject_name, s.emoji AS subject_emoji
            FROM quiz_results AS qr
            JOIN subjects AS s ON s.id = qr.subject_id
            WHERE qr.user_id = ?
            ORDER BY qr.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return list(await cursor.fetchall())


async def get_activity_stats(user_id: int) -> dict[str, int]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT DISTINCT date(created_at, '+5 hours') AS day
            FROM quiz_results
            WHERE user_id = ?
            UNION
            SELECT DISTINCT date(completed_at, '+5 hours') AS day
            FROM study_progress
            WHERE user_id = ? AND status = 'completed' AND completed_at IS NOT NULL
            UNION
            SELECT DISTINCT date(created_at, '+5 hours') AS day
            FROM chat_history
            WHERE user_id = ? AND role = 'user'
            """,
            (user_id, user_id, user_id),
        )
        days = {row["day"] for row in await cursor.fetchall() if row["day"]}

    return {
        "streak": calculate_streak(days),
        "active_days": len(days),
    }
