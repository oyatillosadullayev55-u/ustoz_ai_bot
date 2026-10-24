"""Fanlar, darslar va savollar bilan ishlash."""

from __future__ import annotations

import re
from typing import Any

import aiosqlite

from database.db import get_connection

STOPWORDS = frozenset(
    {
        "bilan",
        "uchun",
        "qanday",
        "nima",
        "nima?",
        "nega",
        "qaysi",
        "bolsa",
        "bo'lsa",
        "ham",
        "yoki",
        "lekin",
        "men",
        "sen",
        "u",
        "biz",
        "siz",
        "ular",
        "bu",
        "shu",
        "juda",
        "yana",
        "menga",
        "senga",
        "haqida",
        "kerak",
        "mumkin",
        "the",
        "and",
        "what",
        "how",
        "why",
    }
)


async def get_subjects_with_counts() -> list[aiosqlite.Row]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT s.id, s.code, s.name, s.emoji, s.description, s.order_index,
                   COUNT(DISTINCT l.id) AS lesson_count,
                   COUNT(DISTINCT q.id) AS question_count
            FROM subjects AS s
            LEFT JOIN lessons AS l
                ON l.subject_id = s.id AND l.is_active = 1
            LEFT JOIN questions AS q ON q.lesson_id = l.id
            WHERE s.is_active = 1
            GROUP BY s.id
            ORDER BY s.order_index, s.id
            """
        )
        return list(await cursor.fetchall())


async def get_subject(subject_id: int) -> aiosqlite.Row | None:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT id, code, name, emoji, description, order_index
            FROM subjects
            WHERE id = ? AND is_active = 1
            """,
            (subject_id,),
        )
        return await cursor.fetchone()


async def get_lessons(subject_id: int) -> list[aiosqlite.Row]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT id, subject_id, title, order_index
            FROM lessons
            WHERE subject_id = ? AND is_active = 1
            ORDER BY order_index, id
            """,
            (subject_id,),
        )
        return list(await cursor.fetchall())


async def get_lesson(lesson_id: int) -> aiosqlite.Row | None:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT l.id, l.subject_id, l.title, l.content, l.order_index,
                   s.name AS subject_name, s.emoji AS subject_emoji
            FROM lessons AS l
            JOIN subjects AS s ON s.id = l.subject_id
            WHERE l.id = ? AND l.is_active = 1 AND s.is_active = 1
            """,
            (lesson_id,),
        )
        return await cursor.fetchone()


async def get_quiz_questions(subject_id: int, limit: int) -> list[aiosqlite.Row]:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT q.id, q.lesson_id, q.question_text, q.option_a, q.option_b,
                   q.option_c, q.option_d, q.correct_option, q.explanation
            FROM questions AS q
            JOIN lessons AS l ON l.id = q.lesson_id
            WHERE l.subject_id = ? AND l.is_active = 1
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (subject_id, limit),
        )
        return list(await cursor.fetchall())


async def get_question(question_id: int) -> aiosqlite.Row | None:
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT q.id, q.lesson_id, q.question_text, q.option_a, q.option_b,
                   q.option_c, q.option_d, q.correct_option, q.explanation,
                   l.title AS lesson_title, s.id AS subject_id,
                   s.name AS subject_name, s.emoji AS subject_emoji
            FROM questions AS q
            JOIN lessons AS l ON l.id = q.lesson_id
            JOIN subjects AS s ON s.id = l.subject_id
            WHERE q.id = ? AND l.is_active = 1 AND s.is_active = 1
            """,
            (question_id,),
        )
        return await cursor.fetchone()


def extract_tokens(text: str, limit: int = 5) -> list[str]:
    words = re.findall(r"[0-9a-zA-Zа-яА-ЯёЁʻ'’]+", text.lower())
    tokens: list[str] = []
    for word in words:
        if len(word) < 3 or word in STOPWORDS or word in tokens:
            continue
        tokens.append(word)
        if len(tokens) >= limit:
            break
    return tokens


async def search_lessons(text: str, limit: int = 2) -> list[aiosqlite.Row]:
    tokens = extract_tokens(text)
    if not tokens:
        return []

    conditions = " OR ".join(
        ["lower(l.title) LIKE ? OR lower(l.content) LIKE ?"] * len(tokens)
    )
    params: list[Any] = []
    for token in tokens:
        pattern = f"%{token}%"
        params.extend((pattern, pattern))

    async with get_connection() as db:
        cursor = await db.execute(
            f"""
            SELECT l.id, l.title, l.content, s.id AS subject_id,
                   s.name AS subject_name, s.emoji AS subject_emoji
            FROM lessons AS l
            JOIN subjects AS s ON s.id = l.subject_id
            WHERE l.is_active = 1 AND s.is_active = 1 AND ({conditions})
            ORDER BY
                CASE WHEN lower(l.title) LIKE ? THEN 0 ELSE 1 END,
                l.order_index
            LIMIT ?
            """,
            (*params, f"%{tokens[0]}%", limit),
        )
        return list(await cursor.fetchall())
