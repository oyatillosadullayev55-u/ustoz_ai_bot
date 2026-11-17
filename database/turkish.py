"""Turk tili kursi: darslar, gaplar va talaffuz audio fayllari."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiosqlite

from config import BASE_DIR
from database.db import get_connection
from time_utils import utc_now

logger = logging.getLogger(__name__)

TURKISH_SUBJECT_ID = 9
TURKISH_DATA_PATH = BASE_DIR / "content" / "turkish_courses.json"
VALID_LEVELS = frozenset({"beginner", "intermediate", "advanced"})


def _require_text(value: Any, message: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RuntimeError(message)
    return text


def _validate_lesson(
    lesson: dict,
) -> tuple[str, list[str], list[dict], list[dict], str, str, int]:
    lesson_id = lesson.get("id")
    if not isinstance(lesson_id, int):
        raise RuntimeError("Turk tili darsida id butun son bo'lishi kerak.")

    summary = _require_text(
        lesson.get("summary"),
        f"Turk tili darsida qisqa mazmun yo'q (dars id={lesson_id}).",
    )
    raw_points = lesson.get("key_points", [])
    if not isinstance(raw_points, list) or not 1 <= len(raw_points) <= 5:
        raise RuntimeError(
            "Har bir turk tili darsida 1-5 ta asosiy fikr bo'lishi kerak "
            f"(dars id={lesson_id})."
        )
    key_points = [_require_text(point, "Asosiy fikr bo'sh.") for point in raw_points]

    level = str(lesson.get("level", "beginner")).strip()
    if level not in VALID_LEVELS:
        raise RuntimeError(
            f"Turk tili dars darajasi noto'g'ri: {level!r} (dars id={lesson_id})."
        )
    duration = lesson.get("duration_min", 8)
    if not isinstance(duration, int) or not 1 <= duration <= 120:
        raise RuntimeError(
            "Turk tili dars davomiyligi 1-120 daqiqa bo'lishi kerak "
            f"(dars id={lesson_id})."
        )

    raw_phrases = lesson.get("phrases", [])
    if not isinstance(raw_phrases, list) or not raw_phrases:
        raise RuntimeError(
            f"Turk tili darsida gaplar ro'yxati yo'q (dars id={lesson_id})."
        )
    phrases: list[dict] = []
    for phrase in raw_phrases:
        phrases.append(
            {
                "tr": _require_text(
                    phrase.get("tr"),
                    f"Turkcha gap bo'sh (dars id={lesson_id}).",
                ),
                "uz": _require_text(
                    phrase.get("uz"),
                    f"Gap tarjimasi bo'sh (dars id={lesson_id}).",
                ),
                "hint": str(phrase.get("hint", "")).strip(),
            }
        )

    raw_questions = lesson.get("questions", [])
    if not isinstance(raw_questions, list) or not raw_questions:
        raise RuntimeError(
            f"Turk tili darsida savollar yo'q (dars id={lesson_id})."
        )
    questions: list[dict] = []
    for question in raw_questions:
        options = question.get("options", [])
        correct = question.get("correct")
        if (
            not isinstance(options, list)
            or len(options) != 4
            or any(not str(option).strip() for option in options)
            or not isinstance(correct, int)
            or not 0 <= correct <= 3
        ):
            raise RuntimeError(
                "Savol formati noto'g'ri: 4 ta variant va 0-3 oralig'idagi "
                f"javob kerak (dars id={lesson_id})."
            )
        questions.append(
            {
                "text": _require_text(
                    question.get("text"),
                    f"Savol matni bo'sh (dars id={lesson_id}).",
                ),
                "options": [str(option).strip() for option in options],
                "correct": correct,
                "explanation": str(question.get("explanation", "")).strip(),
            }
        )

    content = _require_text(
        lesson.get("content"),
        f"Turk tili darsida asosiy matn yo'q (dars id={lesson_id}).",
    )
    return summary, key_points, phrases, questions, content, level, duration


async def seed_turkish() -> None:
    """Turk tili fanini va darslarini bazaga yuklaydi.

    `seed_content()` barcha fanlarni nofaol qiladi, shuning uchun bu funksiya
    undan keyin ishga tushishi shart — u turk tili fanini qayta faollashtiradi.
    """
    try:
        data = json.loads(TURKISH_DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(
            f"Turk tili kontenti topilmadi: {TURKISH_DATA_PATH}"
        ) from None
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Turk tili kontenti noto'g'ri JSON: {TURKISH_DATA_PATH} ({exc})"
        ) from None

    subjects = data.get("subjects", [])
    if not isinstance(subjects, list) or not subjects:
        raise RuntimeError("Turk tili kontentida fan yo'q.")

    now = utc_now()
    lesson_count = 0
    phrase_count = 0
    question_count = 0

    async with get_connection() as db:
        for subject_order, subject in enumerate(subjects, start=1):
            subject_id = int(subject.get("id", TURKISH_SUBJECT_ID))
            await db.execute(
                """
                INSERT INTO subjects (
                    id, code, name, emoji, description, order_index, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(id) DO UPDATE SET
                    code = excluded.code,
                    name = excluded.name,
                    emoji = excluded.emoji,
                    description = excluded.description,
                    order_index = excluded.order_index,
                    is_active = 1
                """,
                (
                    subject_id,
                    str(subject["code"]),
                    str(subject["name"]),
                    str(subject.get("emoji", "🇹🇷")),
                    str(subject.get("description", "")),
                    9 + subject_order - 1,
                ),
            )

            for lesson_order, lesson in enumerate(subject.get("lessons", []), start=1):
                (
                    summary,
                    key_points,
                    phrases,
                    questions,
                    content,
                    level,
                    duration,
                ) = _validate_lesson(lesson)
                lesson_id = int(lesson["id"])

                await db.execute(
                    """
                    INSERT INTO lessons (
                        id, subject_id, title, content, summary, key_points,
                        level, duration_min, order_index, is_active, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        subject_id = excluded.subject_id,
                        title = excluded.title,
                        content = excluded.content,
                        summary = excluded.summary,
                        key_points = excluded.key_points,
                        level = excluded.level,
                        duration_min = excluded.duration_min,
                        order_index = excluded.order_index,
                        is_active = 1
                    """,
                    (
                        lesson_id,
                        subject_id,
                        str(lesson["title"]),
                        content,
                        summary,
                        json.dumps(key_points, ensure_ascii=False),
                        level,
                        duration,
                        lesson_order,
                        now,
                    ),
                )

                await db.execute(
                    "DELETE FROM questions WHERE lesson_id = ?", (lesson_id,)
                )
                for question_order, question in enumerate(questions, start=1):
                    options = question["options"]
                    await db.execute(
                        """
                        INSERT INTO questions (
                            id, lesson_id, question_text, option_a, option_b,
                            option_c, option_d, correct_option, explanation,
                            order_index
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            lesson_id * 10 + question_order,
                            lesson_id,
                            question["text"],
                            options[0],
                            options[1],
                            options[2],
                            options[3],
                            question["correct"],
                            question["explanation"],
                            question_order,
                        ),
                    )
                    question_count += 1

                await db.execute(
                    "DELETE FROM turkish_phrases WHERE lesson_id = ?", (lesson_id,)
                )
                for phrase_index, phrase in enumerate(phrases, start=1):
                    await db.execute(
                        """
                        INSERT INTO turkish_phrases (
                            lesson_id, phrase_index, phrase_tr, phrase_uz, hint
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            lesson_id,
                            phrase_index,
                            phrase["tr"],
                            phrase["uz"],
                            phrase["hint"],
                        ),
                    )
                    phrase_count += 1

                lesson_count += 1

        await db.commit()

    logger.info(
        "Turk tili yuklandi: %s dars, %s gap, %s savol.",
        lesson_count,
        phrase_count,
        question_count,
    )


async def get_turkish_phrases(lesson_id: int) -> list[aiosqlite.Row]:
    """Darsdagi gaplarni talaffuz tartibida qaytaradi."""
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT lesson_id, phrase_index, phrase_tr, phrase_uz, hint
            FROM turkish_phrases
            WHERE lesson_id = ?
            ORDER BY phrase_index
            """,
            (lesson_id,),
        )
        return list(await cursor.fetchall())
