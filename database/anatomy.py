"""Anatomiya test banki: yuklash va savollarni tanlash."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiosqlite

from config import BASE_DIR
from database.db import get_connection

logger = logging.getLogger(__name__)

ANATOMY_SUBJECT_ID = 900
ANATOMY_DATA_PATH = BASE_DIR / "content" / "anatomy_questions.json"

QUESTION_FIELDS = (
    "id, question_text, option_a, option_b, option_c, option_d, correct_option"
)


def _validate(raw: Any) -> list[tuple]:
    if not isinstance(raw, list):
        raise RuntimeError("Anatomiya banki ro'yxat bo'lishi kerak.")

    rows: list[tuple] = []
    for index, item in enumerate(raw, start=1):
        text = str(item.get("text", "")).strip()
        options = item.get("options", [])
        correct = item.get("correct")
        if (
            not text
            or not isinstance(options, list)
            or len(options) != 4
            or any(not str(option).strip() for option in options)
            or not isinstance(correct, int)
            or not 0 <= correct <= 3
        ):
            raise RuntimeError(
                f"Anatomiya savoli formati noto'g'ri (tartib={index})."
            )
        values = [str(option).strip() for option in options]
        rows.append((index, text, *values, correct, index))
    return rows


async def seed_anatomy() -> None:
    """Savollar bankini bazaga yuklaydi va yashirin natija fanini yaratadi."""
    try:
        raw = json.loads(ANATOMY_DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(
            f"Anatomiya banki topilmadi: {ANATOMY_DATA_PATH}"
        ) from None
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Anatomiya banki noto'g'ri JSON: {exc}"
        ) from None

    rows = _validate(raw)
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO subjects (
                id, code, name, emoji, description, order_index, is_active
            )
            VALUES (?, 'anatomy', 'Anatomiya', '🫀',
                    '2-kurs anatomiya test banki.', 900, 0)
            ON CONFLICT(id) DO UPDATE SET
                code = excluded.code,
                name = excluded.name,
                emoji = excluded.emoji,
                description = excluded.description,
                is_active = 0
            """,
            (ANATOMY_SUBJECT_ID,),
        )
        await db.execute("DELETE FROM anatomy_questions")
        await db.executemany(
            """
            INSERT INTO anatomy_questions (
                id, question_text, option_a, option_b, option_c, option_d,
                correct_option, order_index
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    logger.info("Anatomiya banki yuklandi: %s savol.", len(rows))


async def count_anatomy_questions() -> int:
    async with get_connection() as db:
        cursor = await db.execute("SELECT COUNT(*) AS total FROM anatomy_questions")
        row = await cursor.fetchone()
    return int(row["total"]) if row is not None else 0


async def get_anatomy_questions(limit: int) -> list[aiosqlite.Row]:
    if limit <= 0:
        return []
    async with get_connection() as db:
        cursor = await db.execute(
            f"""
            SELECT {QUESTION_FIELDS}
            FROM anatomy_questions
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (limit,),
        )
        return list(await cursor.fetchall())


async def get_anatomy_question(question_id: int) -> aiosqlite.Row | None:
    async with get_connection() as db:
        cursor = await db.execute(
            f"SELECT {QUESTION_FIELDS} FROM anatomy_questions WHERE id = ?",
            (question_id,),
        )
        return await cursor.fetchone()


async def get_anatomy_questions_by_ids(
    question_ids: list[int],
) -> dict[int, aiosqlite.Row]:
    if not question_ids:
        return {}
    placeholders = ", ".join("?" for _ in question_ids)
    async with get_connection() as db:
        cursor = await db.execute(
            f"""
            SELECT {QUESTION_FIELDS}
            FROM anatomy_questions
            WHERE id IN ({placeholders})
            """,
            tuple(question_ids),
        )
        rows = await cursor.fetchall()
    return {int(row["id"]): row for row in rows}


async def save_anatomy_session(user_id: int, data: dict[str, Any]) -> None:
    """Faol testni bazaga yozadi — bot qayta ishga tushsa ham yo'qolmaydi."""
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO anatomy_sessions (
                user_id, mode, question_ids, answered_index, correct, answers,
                current_id, deadline, started_at, chat_id, message_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                mode = excluded.mode,
                question_ids = excluded.question_ids,
                answered_index = excluded.answered_index,
                correct = excluded.correct,
                answers = excluded.answers,
                current_id = excluded.current_id,
                deadline = excluded.deadline,
                started_at = excluded.started_at,
                chat_id = excluded.chat_id,
                message_id = excluded.message_id
            """,
            (
                user_id,
                int(data["mode"]),
                json.dumps([int(item) for item in data["question_ids"]]),
                int(data.get("index", 0)),
                int(data.get("correct", 0)),
                json.dumps(data.get("answers", [])),
                int(data["current_id"]),
                float(data["deadline"]),
                float(data["started_at"]),
                int(data["chat_id"]),
                int(data["message_id"]),
            ),
        )


async def load_anatomy_session(user_id: int) -> dict[str, Any] | None:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT user_id, mode, question_ids, answered_index, correct,
                   answers, current_id, deadline, started_at, chat_id,
                   message_id
            FROM anatomy_sessions
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
    if row is None:
        return None
    return {
        "mode": int(row["mode"]),
        "question_ids": [int(item) for item in json.loads(row["question_ids"])],
        "index": int(row["answered_index"]),
        "correct": int(row["correct"]),
        "answers": json.loads(row["answers"]),
        "current_id": int(row["current_id"]),
        "deadline": float(row["deadline"]),
        "started_at": float(row["started_at"]),
        "chat_id": int(row["chat_id"]),
        "message_id": int(row["message_id"]),
    }


async def delete_anatomy_session(user_id: int) -> None:
    async with get_connection() as db:
        await db.execute(
            "DELETE FROM anatomy_sessions WHERE user_id = ?", (user_id,)
        )

