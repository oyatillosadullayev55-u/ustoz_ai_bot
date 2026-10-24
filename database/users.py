"""Foydalanuvchilar jadvali bilan ishlash."""

from __future__ import annotations

import aiosqlite

from database.db import get_connection
from time_utils import utc_now

LEVELS = ("beginner", "intermediate", "advanced")


async def get_user(telegram_id: int) -> aiosqlite.Row | None:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT telegram_id, full_name, username, language, level,
                   notifications_enabled, created_at, updated_at, last_seen_at
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )
        return await cursor.fetchone()


async def create_user(
    *,
    telegram_id: int,
    full_name: str,
    username: str | None,
    language: str,
    level: str,
) -> None:
    """Yangi foydalanuvchini saqlaydi. Takroriy chaqiruv dublikat yaratmaydi."""
    if level not in LEVELS:
        raise ValueError(f"Noma'lum daraja: {level}")

    now = utc_now()
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO users (
                telegram_id, full_name, username, language, level,
                notifications_enabled, created_at, updated_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            ON CONFLICT(telegram_id) DO NOTHING
            """,
            (telegram_id, full_name, username, language, level, now, now, now),
        )


async def update_level(telegram_id: int, level: str) -> bool:
    if level not in LEVELS:
        raise ValueError(f"Noma'lum daraja: {level}")

    async with get_connection() as db:
        cursor = await db.execute(
            "UPDATE users SET level = ?, updated_at = ? WHERE telegram_id = ?",
            (level, utc_now(), telegram_id),
        )
        return cursor.rowcount > 0


async def update_last_seen(telegram_id: int) -> None:
    async with get_connection() as db:
        await db.execute(
            "UPDATE users SET last_seen_at = ? WHERE telegram_id = ?",
            (utc_now(), telegram_id),
        )


async def update_notifications(telegram_id: int, enabled: bool) -> bool:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            UPDATE users
            SET notifications_enabled = ?, updated_at = ?
            WHERE telegram_id = ?
            """,
            (int(enabled), utc_now(), telegram_id),
        )
        return cursor.rowcount > 0
