"""XP, yutuqlar va haftalik reyting uchun so'rovlar."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta

from database.db import get_connection
from time_utils import utc_now


async def award_xp(
    user_id: int,
    amount: int,
    reason: str,
    *,
    once_key: str | None = None,
) -> int | None:
    """XP qo'shadi va yangi umumiy qiymatni qaytaradi.

    `once_key` berilgan bo'lsa va avval ishlatilgan bo'lsa, XP qo'shilmaydi
    va `None` qaytariladi.
    """
    if amount <= 0:
        return await get_total_xp(user_id)

    now = utc_now()
    async with get_connection() as db:
        try:
            await db.execute(
                """
                INSERT INTO xp_log (user_id, amount, reason, once_key, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, amount, reason, once_key, now),
            )
        except sqlite3.IntegrityError:
            return None

        await db.execute(
            "UPDATE users SET xp = xp + ?, updated_at = ? WHERE telegram_id = ?",
            (amount, now, user_id),
        )
        cursor = await db.execute(
            "SELECT xp FROM users WHERE telegram_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

    return int(row["xp"]) if row is not None else 0


async def get_total_xp(user_id: int) -> int:
    async with get_connection() as db:
        cursor = await db.execute(
            "SELECT xp FROM users WHERE telegram_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
    return int(row["xp"]) if row is not None else 0


async def get_weekly_xp(user_id: int) -> int:
    cutoff = _week_cutoff()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM xp_log
            WHERE user_id = ? AND created_at >= ?
            """,
            (user_id, cutoff),
        )
        row = await cursor.fetchone()
    return int(row["total"]) if row is not None else 0


async def get_achievement_codes(user_id: int) -> set[str]:
    async with get_connection() as db:
        cursor = await db.execute(
            "SELECT code FROM achievements WHERE user_id = ?", (user_id,)
        )
        return {str(row["code"]) for row in await cursor.fetchall()}


async def unlock_achievements(user_id: int, codes: list[str]) -> list[str]:
    """Yangi yutuqlarni yozadi va haqiqatan qo'shilganlarini qaytaradi."""
    if not codes:
        return []

    now = utc_now()
    inserted: list[str] = []
    async with get_connection() as db:
        for code in codes:
            cursor = await db.execute(
                """
                INSERT INTO achievements (user_id, code, unlocked_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, code) DO NOTHING
                """,
                (user_id, code, now),
            )
            if cursor.rowcount > 0:
                inserted.append(code)
    return inserted


async def get_achievement_stats(user_id: int) -> dict[str, int]:
    """Yutuq shartlari uchun yig'ma ko'rsatkichlar."""
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM study_progress
                 WHERE user_id = ? AND status = 'completed') AS lessons,
                (SELECT COUNT(*) FROM quiz_results
                 WHERE user_id = ?) AS quizzes,
                (SELECT COUNT(*) FROM quiz_results
                 WHERE user_id = ? AND score_percent = 100) AS perfect,
                (SELECT COALESCE(MAX(score_percent), 0) FROM quiz_results
                 WHERE user_id = ?) AS best,
                (SELECT COUNT(*) FROM favorites
                 WHERE user_id = ?) AS favorites,
                (SELECT COUNT(*) FROM chat_history
                 WHERE user_id = ? AND role = 'user') AS ai_messages,
                (SELECT COUNT(*) FROM daily_goals
                 WHERE user_id = ?
                   AND target_lessons + target_quizzes > 0
                   AND completed_lessons >= target_lessons
                   AND completed_quizzes >= target_quizzes) AS goal_days
            """,
            (user_id,) * 7,
        )
        row = await cursor.fetchone()

    if row is None:
        return {
            "lessons": 0,
            "quizzes": 0,
            "perfect": 0,
            "best": 0,
            "favorites": 0,
            "ai_messages": 0,
            "goal_days": 0,
        }
    return {
        key: int(row[key])
        for key in (
            "lessons",
            "quizzes",
            "perfect",
            "best",
            "favorites",
            "ai_messages",
            "goal_days",
        )
    }


async def get_weekly_leaderboard(
    user_id: int, limit: int = 10
) -> dict[str, object]:
    """So'nggi 7 kundagi XP bo'yicha reyting va foydalanuvchi o'rni."""
    cutoff = _week_cutoff()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT u.telegram_id, u.full_name, SUM(x.amount) AS week_xp,
                   u.xp AS total_xp
            FROM xp_log AS x
            JOIN users AS u ON u.telegram_id = x.user_id
            WHERE x.created_at >= ?
            GROUP BY x.user_id
            HAVING week_xp > 0
            ORDER BY week_xp DESC, u.telegram_id ASC
            LIMIT ?
            """,
            (cutoff, limit),
        )
        rows = list(await cursor.fetchall())

        cursor = await db.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM xp_log
            WHERE user_id = ? AND created_at >= ?
            """,
            (user_id, cutoff),
        )
        user_row = await cursor.fetchone()
        user_week_xp = int(user_row["total"]) if user_row is not None else 0

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS ahead FROM (
                SELECT user_id, SUM(amount) AS total
                FROM xp_log
                WHERE created_at >= ?
                GROUP BY user_id
                HAVING total > ?
            )
            """,
            (cutoff, user_week_xp),
        )
        ahead_row = await cursor.fetchone()

        cursor = await db.execute(
            """
            SELECT COUNT(DISTINCT user_id) AS total FROM xp_log
            WHERE created_at >= ?
            """,
            (cutoff,),
        )
        total_row = await cursor.fetchone()

    ahead = int(ahead_row["ahead"]) if ahead_row is not None else 0
    return {
        "rows": rows,
        "user_week_xp": user_week_xp,
        "user_rank": ahead + 1 if user_week_xp > 0 else None,
        "total_players": int(total_row["total"]) if total_row is not None else 0,
    }


def _week_cutoff() -> str:
    return (datetime.now(UTC) - timedelta(days=7)).isoformat(timespec="seconds")

