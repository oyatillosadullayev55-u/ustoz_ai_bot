"""O'quv kontentini JSON fayldan bazaga yuklash."""

from __future__ import annotations

import json
import logging

from config import BASE_DIR
from database.db import get_connection
from time_utils import utc_now

logger = logging.getLogger(__name__)

SEED_PATH = BASE_DIR / "content" / "seed_data.json"


async def seed_content() -> None:
    try:
        raw = SEED_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        raise RuntimeError(f"Kontent fayli topilmadi: {SEED_PATH}") from None
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Kontent fayli noto'g'ri JSON: {SEED_PATH} ({exc})"
        ) from None

    subjects = data.get("subjects", [])
    now = utc_now()
    lesson_count = 0
    question_count = 0

    async with get_connection() as db:
        await db.execute("UPDATE subjects SET is_active = 0")
        await db.execute("UPDATE lessons SET is_active = 0")

        for subject_order, subject in enumerate(subjects, start=1):
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
                    subject["id"],
                    subject["code"],
                    subject["name"],
                    subject.get("emoji", "📚"),
                    subject.get("description", ""),
                    subject_order,
                ),
            )

            for lesson_order, lesson in enumerate(subject.get("lessons", []), start=1):
                await db.execute(
                    """
                    INSERT INTO lessons (
                        id, subject_id, title, content, order_index,
                        is_active, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        subject_id = excluded.subject_id,
                        title = excluded.title,
                        content = excluded.content,
                        order_index = excluded.order_index,
                        is_active = 1
                    """,
                    (
                        lesson["id"],
                        subject["id"],
                        lesson["title"],
                        lesson["content"],
                        lesson_order,
                        now,
                    ),
                )

                await db.execute(
                    "DELETE FROM questions WHERE lesson_id = ?", (lesson["id"],)
                )

                for question_order, question in enumerate(
                    lesson.get("questions", []), start=1
                ):
                    options = question.get("options", [])
                    correct = question.get("correct")
                    if len(options) != 4 or not isinstance(correct, int) or not 0 <= correct <= 3:
                        raise RuntimeError(
                            "Savol formati noto'g'ri: har bir savolda 4 ta variant "
                            f"va 0-3 oralig'idagi to'g'ri javob bo'lishi kerak "
                            f"(dars id={lesson['id']}, savol={question.get('text')!r})."
                        )

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
                            lesson["id"] * 10 + question_order,
                            lesson["id"],
                            question["text"],
                            options[0],
                            options[1],
                            options[2],
                            options[3],
                            correct,
                            question.get("explanation", ""),
                            question_order,
                        ),
                    )
                    question_count += 1

                lesson_count += 1

        await db.commit()

    logger.info(
        "Kontent yuklandi: %s fan, %s dars, %s savol.",
        len(subjects),
        lesson_count,
        question_count,
    )
