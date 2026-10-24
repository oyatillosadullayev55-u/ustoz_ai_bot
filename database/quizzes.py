"""Test natijalarini saqlash."""

from __future__ import annotations

from database.db import get_connection
from time_utils import utc_now


async def save_quiz_result(
    *,
    user_id: int,
    subject_id: int,
    total_questions: int,
    correct_answers: int,
) -> int:
    if total_questions <= 0:
        raise ValueError("Savollar soni noldan katta bo'lishi kerak.")
    if not 0 <= correct_answers <= total_questions:
        raise ValueError("To'g'ri javoblar soni savollar sonidan oshmasligi kerak.")

    score_percent = round(correct_answers / total_questions * 100)
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO quiz_results (
                user_id, subject_id, total_questions, correct_answers,
                score_percent, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                subject_id,
                total_questions,
                correct_answers,
                score_percent,
                utc_now(),
            ),
        )
    return score_percent
