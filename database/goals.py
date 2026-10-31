"""Kunlik o'quv maqsadlari."""

from __future__ import annotations

import aiosqlite

from database.db import get_connection
from time_utils import local_today, utc_now


async def get_today_goal(user_id: int) -> aiosqlite.Row:
    today = local_today()
    now = utc_now()
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO daily_goals (
                user_id, goal_date, target_lessons, target_quizzes,
                completed_lessons, completed_quizzes, created_at, updated_at
            )
            VALUES (?, ?, 1, 1, 0, 0, ?, ?)
            ON CONFLICT(user_id, goal_date) DO NOTHING
            """,
            (user_id, today, now, now),
        )
        cursor = await db.execute(
            """
            SELECT target_lessons, target_quizzes, completed_lessons,
                   completed_quizzes, goal_date
            FROM daily_goals
            WHERE user_id = ? AND goal_date = ?
            """,
            (user_id, today),
        )
        goal = await cursor.fetchone()

    if goal is None:
        raise RuntimeError("Kunlik maqsadni yaratib bo'lmadi.")
    return goal


async def set_goal_targets(
    user_id: int, target_lessons: int, target_quizzes: int
) -> None:
    if not 0 <= target_lessons <= 20 or not 0 <= target_quizzes <= 20:
        raise ValueError("Maqsad qiymatlari 0 dan 20 gacha bo'lishi kerak.")

    today = local_today()
    now = utc_now()
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO daily_goals (
                user_id, goal_date, target_lessons, target_quizzes,
                completed_lessons, completed_quizzes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 0, 0, ?, ?)
            ON CONFLICT(user_id, goal_date) DO UPDATE SET
                target_lessons = excluded.target_lessons,
                target_quizzes = excluded.target_quizzes,
                updated_at = excluded.updated_at
            """,
            (user_id, today, target_lessons, target_quizzes, now, now),
        )


async def increment_goal(
    user_id: int, *, lessons: int = 0, quizzes: int = 0
) -> bool:
    """Kunlik hisobni oshiradi; shu amaldan keyin maqsad bajarilgan bo'lsa True."""
    if lessons < 0 or quizzes < 0:
        raise ValueError("O'sish qiymati manfiy bo'lishi mumkin emas.")
    if lessons == 0 and quizzes == 0:
        return False

    today = local_today()
    now = utc_now()
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO daily_goals (
                user_id, goal_date, target_lessons, target_quizzes,
                completed_lessons, completed_quizzes, created_at, updated_at
            )
            VALUES (?, ?, 1, 1, ?, ?, ?, ?)
            ON CONFLICT(user_id, goal_date) DO UPDATE SET
                completed_lessons = completed_lessons + excluded.completed_lessons,
                completed_quizzes = completed_quizzes + excluded.completed_quizzes,
                updated_at = excluded.updated_at
            """,
            (user_id, today, lessons, quizzes, now, now),
        )
        cursor = await db.execute(
            """
            SELECT target_lessons, target_quizzes,
                   completed_lessons, completed_quizzes
            FROM daily_goals
            WHERE user_id = ? AND goal_date = ?
            """,
            (user_id, today),
        )
        goal = await cursor.fetchone()

    if goal is None:
        return False
    return (
        int(goal["target_lessons"]) + int(goal["target_quizzes"]) > 0
        and int(goal["completed_lessons"]) >= int(goal["target_lessons"])
        and int(goal["completed_quizzes"]) >= int(goal["target_quizzes"])
    )


async def get_pending_reminders(goal_date: str) -> list[aiosqlite.Row]:
    """Bugungi rejasi bajarilmagan va bildirishnoma yoqilgan foydalanuvchilar."""
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT dg.user_id, u.full_name,
                   dg.target_lessons, dg.target_quizzes,
                   dg.completed_lessons, dg.completed_quizzes
            FROM daily_goals AS dg
            JOIN users AS u ON u.telegram_id = dg.user_id
            WHERE dg.goal_date = ?
              AND u.notifications_enabled = 1
              AND (
                  dg.completed_lessons < dg.target_lessons
                  OR dg.completed_quizzes < dg.target_quizzes
              )
            ORDER BY dg.user_id
            """,
            (goal_date,),
        )
        return list(await cursor.fetchall())
