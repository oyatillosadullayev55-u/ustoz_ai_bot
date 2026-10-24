"""AI suhbat tarixi va kunlik foydalanish cheklovi."""

from __future__ import annotations

import aiosqlite

from database.db import get_connection
from time_utils import local_today, utc_now


async def add_message(user_id: int, role: str, message: str) -> None:
    if role not in {"user", "assistant"}:
        raise ValueError(f"Noma'lum rol: {role}")

    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO chat_history (user_id, role, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, role, message, utc_now()),
        )


async def get_history(user_id: int, limit: int) -> list[aiosqlite.Row]:
    if limit <= 0:
        return []

    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT role, message
            FROM chat_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = list(await cursor.fetchall())

    rows.reverse()
    return rows


async def get_ai_usage(user_id: int) -> tuple[int, str | None]:
    today = local_today()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*) AS total, MAX(created_at) AS last_at
            FROM chat_history
            WHERE user_id = ? AND role = 'user'
              AND date(created_at, '+5 hours') = ?
            """,
            (user_id, today),
        )
        row = await cursor.fetchone()

    if row is None:
        return 0, None
    return int(row["total"]), row["last_at"]
