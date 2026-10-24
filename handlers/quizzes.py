"""Testlar bo'limi: 4 variantli savollar va natijalar."""

from __future__ import annotations

import asyncio
import html
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.content import (
    get_question,
    get_quiz_questions,
    get_subject,
    get_subjects_with_counts,
)
from database.goals import increment_goal
from database.quizzes import save_quiz_result
from handlers.common import require_user, require_user_callback, safe_edit
from keyboards.inline_buttons import (
    get_quiz_options_keyboard,
    get_quiz_result_keyboard,
    get_subjects_keyboard,
)
from keyboards.main_menu import BTN_QUIZZES

router = Router(name="quizzes")
logger = logging.getLogger(__name__)

QUIZ_SIZE = 5

_locks: dict[int, asyncio.Lock] = {}


class QuizStates(StatesGroup):
    answering = State()


def _lock_for(user_id: int) -> asyncio.Lock:
    lock = _locks.get(user_id)
    if lock is None:
        lock = asyncio.Lock()
        _locks[user_id] = lock
    return lock


def _subjects_text() -> str:
    return (
        "📝 <b>Testlar</b>\n\n"
        f"Har bir test {QUIZ_SIZE} ta savoldan iborat. Savolga 4 ta variantdan "
        "bittasini tanlang.\n\n"
        "Fan tanlang:"
    )


def _question_text(subject_name: str, question, index: int, total: int) -> str:
    return (
        f"📝 <b>{html.escape(subject_name)}</b> · "
        f"savol {index + 1}/{total}\n\n"
        f"{html.escape(question['question_text'])}"
    )


def _result_text(
    *, subject_name: str, emoji: str, correct: int, total: int, percent: int
) -> str:
    if percent >= 90:
        message = "Ajoyib natija! 🎉 Mavzuni juda yaxshi o'zlashtirgansiz."
    elif percent >= 70:
        message = "Yaxshi natija! 👏 Yana bir oz mashq bilan mukammal bo'ladi."
    elif percent >= 50:
        message = "Yaxshi harakat! 📈 Xato qilgan mavzularni darslarda takrorlang."
    else:
        message = "Mashq qilishda davom eting. 💪 Darslarni o'qib, testni qayta yeching."

    return (
        "🏁 <b>Test yakunlandi!</b>\n\n"
        f"{emoji} {html.escape(subject_name)}\n"
        f"✅ To'g'ri javoblar: <b>{correct}/{total}</b>\n"
        f"📊 Natija: <b>{percent}%</b>\n\n"
        f"{message}\n\n"
        "📅 Natija kunlik rejaga qo'shildi."
    )


@router.message(F.text == BTN_QUIZZES)
async def quizzes_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    if await require_user(message) is None:
        return

    subjects = await get_subjects_with_counts()
    await message.answer(
        _subjects_text(), reply_markup=get_subjects_keyboard(subjects, "quiz")
    )


@router.callback_query(F.data == "quiz:subjects")
async def show_quiz_subjects(callback: CallbackQuery, state: FSMContext) -> None:
    if await require_user_callback(callback) is None:
        return

    await state.clear()
    subjects = await get_subjects_with_counts()
    await safe_edit(
        callback, _subjects_text(), get_subjects_keyboard(subjects, "quiz")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("quiz:subject:"))
async def start_quiz(
    callback: CallbackQuery, state: FSMContext
) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        subject_id = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer("Fan topilmadi.", show_alert=True)
        return

    subject = await get_subject(subject_id)
    if subject is None:
        await callback.answer("Fan topilmadi.", show_alert=True)
        return

    questions = await get_quiz_questions(subject_id, QUIZ_SIZE)
    if not questions:
        await callback.answer(
            "Bu fan bo'yicha testlar hali qo'shilmagan.", show_alert=True
        )
        return

    first = questions[0]
    await state.clear()
    await state.set_state(QuizStates.answering)
    await state.update_data(
        subject_id=subject_id,
        subject_name=subject["name"],
        subject_emoji=subject["emoji"],
        question_ids=[question["id"] for question in questions],
        index=0,
        correct=0,
        current_id=first["id"],
    )

    await safe_edit(
        callback,
        _question_text(subject["name"], first, 0, len(questions)),
        get_quiz_options_keyboard(
            first["id"],
            [
                first["option_a"],
                first["option_b"],
                first["option_c"],
                first["option_d"],
            ],
        ),
    )
    await callback.answer("Test boshlandi. Omad! 🍀")


@router.callback_query(QuizStates.answering, F.data.startswith("quiz:answer:"))
async def answer_question(callback: CallbackQuery, state: FSMContext) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        _, _, question_raw, option_raw = callback.data.split(":")
        question_id = int(question_raw)
        option = int(option_raw)
    except ValueError:
        await callback.answer("Noto'g'ri javob.", show_alert=True)
        return

    if option not in range(4):
        await callback.answer("Noto'g'ri variant tanlandi.", show_alert=True)
        return

    user_id = user["telegram_id"]
    async with _lock_for(user_id):
        data = await state.get_data()
        if not data or data.get("current_id") != question_id:
            await callback.answer(
                "Bu savol allaqachon yakunlangan.", show_alert=True
            )
            return

        question_ids: list[int] = list(data.get("question_ids", []))
        index = int(data.get("index", 0))
        correct_total = int(data.get("correct", 0))
        subject_id = int(data["subject_id"])
        subject_name = str(data["subject_name"])
        subject_emoji = str(data["subject_emoji"])

        if question_id not in question_ids or index >= len(question_ids):
            await state.clear()
            await callback.answer("Test ma'lumotlari eskirgan.", show_alert=True)
            return

        question = await get_question(question_id)
        if question is None:
            await state.clear()
            await callback.answer("Savol topilmadi.", show_alert=True)
            return

        if option == question["correct_option"]:
            correct_total += 1

        next_index = index + 1
        if next_index >= len(question_ids):
            percent = await save_quiz_result(
                user_id=user_id,
                subject_id=subject_id,
                total_questions=len(question_ids),
                correct_answers=correct_total,
            )
            await increment_goal(user_id, quizzes=1)
            await state.clear()

            await safe_edit(
                callback,
                _result_text(
                    subject_name=subject_name,
                    emoji=subject_emoji,
                    correct=correct_total,
                    total=len(question_ids),
                    percent=percent,
                ),
                get_quiz_result_keyboard(subject_id),
            )
            await callback.answer("Test yakunlandi! 🏁")
            logger.info(
                "Test yakunlandi: user=%s, fan=%s, natija=%s/%s",
                user_id,
                subject_id,
                correct_total,
                len(question_ids),
            )
            return

        next_question = await get_question(question_ids[next_index])
        if next_question is None:
            await state.clear()
            await callback.answer("Keyingi savol topilmadi.", show_alert=True)
            return

        await state.update_data(
            index=next_index,
            correct=correct_total,
            current_id=next_question["id"],
        )
        await safe_edit(
            callback,
            _question_text(subject_name, next_question, next_index, len(question_ids)),
            get_quiz_options_keyboard(
                next_question["id"],
                [
                    next_question["option_a"],
                    next_question["option_b"],
                    next_question["option_c"],
                    next_question["option_d"],
                ],
            ),
        )

    await callback.answer("✅ Javob qabul qilindi")
