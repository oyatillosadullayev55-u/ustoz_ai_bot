"""Admin panel uchun umumiy statistika."""

from __future__ import annotations

from database.db import get_connection
from time_utils import local_today


async def get_admin_stats() -> dict[str, int | float]:
    today = local_today()
    async with get_connection() as db:
        cursor = await db.execute("SELECT COUNT(*) AS total FROM users")
        total_users = int((await cursor.fetchone())["total"])

        cursor = await db.execute(
            "SELECT COUNT(*) AS total FROM users"
            " WHERE date(created_at, '+5 hours') = ?",
            (today,),
        )
        new_today = int((await cursor.fetchone())["total"])

        cursor = await db.execute(
            "SELECT COUNT(*) AS total FROM users"
            " WHERE date(last_seen_at, '+5 hours') = ?",
            (today,),
        )
        active_today = int((await cursor.fetchone())["total"])

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total, COALESCE(AVG(score_percent), 0) AS average
            FROM quiz_results
            """
        )
        quiz_row = await cursor.fetchone()

        cursor = await db.execute(
            "SELECT COUNT(*) AS total FROM study_progress WHERE status = 'completed'"
        )
        lessons_completed = int((await cursor.fetchone())["total"])

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total FROM chat_history
            WHERE role = 'user' AND date(created_at, '+5 hours') = ?
            """,
            (today,),
        )
        ai_today = int((await cursor.fetchone())["total"])

        cursor = await db.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM subjects WHERE is_active = 1) AS subjects,
                (SELECT COUNT(*) FROM lessons WHERE is_active = 1) AS lessons,
                (SELECT COUNT(*) FROM questions) AS questions
            """
        )
        content = await cursor.fetchone()

    return {
        "total_users": total_users,
        "new_today": new_today,
        "active_today": active_today,
        "quizzes": int(quiz_row["total"]),
        "average_score": float(quiz_row["average"]),
        "lessons_completed": lessons_completed,
        "ai_today": ai_today,
        "subjects": int(content["subjects"]),
        "lessons": int(content["lessons"]),
        "questions": int(content["questions"]),
    }


async def get_all_user_ids(notifications_only: bool = False) -> list[int]:
    query = "SELECT telegram_id FROM users"
    if notifications_only:
        query += " WHERE notifications_enabled = 1"
    query += " ORDER BY telegram_id"

    async with get_connection() as db:
        cursor = await db.execute(query)
        return [int(row["telegram_id"]) for row in await cursor.fetchall()]
