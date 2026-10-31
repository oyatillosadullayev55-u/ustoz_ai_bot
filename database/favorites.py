"""Sevimli darslar bilan ishlash."""

from __future__ import annotations

import aiosqlite

from database.db import get_connection
from time_utils import utc_now


async def is_favorite(user_id: int, lesson_id: int) -> bool:
    async with get_connection() as db:
        cursor = await db.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND lesson_id = ?",
            (user_id, lesson_id),
        )
        return await cursor.fetchone() is not None


async def toggle_favorite(user_id: int, lesson_id: int) -> bool:
    """Sevimlilar holatini almashtiradi va yangi holatni qaytaradi."""
    async with get_connection() as db:
        cursor = await db.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND lesson_id = ?",
            (user_id, lesson_id),
        )
        exists = await cursor.fetchone() is not None
        if exists:
            await db.execute(
                "DELETE FROM favorites WHERE user_id = ? AND lesson_id = ?",
                (user_id, lesson_id),
            )
            return False

        await db.execute(
            """
            INSERT INTO favorites (user_id, lesson_id, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, lesson_id) DO NOTHING
            """,
            (user_id, lesson_id, utc_now()),
        )
        return True


async def get_favorite_lessons(
    user_id: int, limit: int = 20
) -> list[aiosqlite.Row]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT l.id, l.title, l.subject_id, l.order_index,
                   s.name AS subject_name, s.emoji AS subject_emoji
            FROM favorites AS f
            JOIN lessons AS l ON l.id = f.lesson_id
            JOIN subjects AS s ON s.id = l.subject_id
            WHERE f.user_id = ? AND l.is_active = 1 AND s.is_active = 1
            ORDER BY f.created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return list(await cursor.fetchall())


async def count_favorites(user_id: int) -> int:
    async with get_connection() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) AS total FROM favorites WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
    return int(row["total"]) if row is not None else 0
