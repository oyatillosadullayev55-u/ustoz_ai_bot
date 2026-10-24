"""Darslar bo'limi: fanlar, mavzular va darsni tugatish."""

from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.content import (
    get_lesson,
    get_lessons,
    get_subject,
    get_subjects_with_counts,
)
from database.goals import increment_goal
from database.progress import (
    complete_lesson,
    get_completed_lesson_ids,
    mark_lesson_started,
)
from handlers.common import require_user, require_user_callback, safe_edit
from keyboards.inline_buttons import (
    get_lesson_keyboard,
    get_lessons_keyboard,
    get_subjects_keyboard,
)
from keyboards.main_menu import BTN_LESSONS

router = Router(name="lessons")
logger = logging.getLogger(__name__)


def _subjects_text() -> str:
    return (
        "📚 <b>Darslar</b>\n\n"
        "Fan tanlang va mavzularni bosqichma-bosqich o'rganing.\n"
        "Har bir dars oxirida test yechish tugmasi mavjud."
    )


def _lesson_text(lesson, *, completed: bool) -> str:
    text = (
        f"{lesson['subject_emoji']} <b>{html.escape(lesson['subject_name'])}</b>\n\n"
        f"<b>{lesson['order_index']}. {html.escape(lesson['title'])}</b>\n\n"
        f"{html.escape(lesson['content'])}"
    )
    if completed:
        text += "\n\n✅ <b>Bu dars tugatilgan.</b>"
    return text


@router.message(F.text == BTN_LESSONS)
async def lessons_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    if await require_user(message) is None:
        return

    subjects = await get_subjects_with_counts()
    await message.answer(
        _subjects_text(),
        reply_markup=get_subjects_keyboard(subjects, "lesson"),
    )


@router.callback_query(F.data == "lesson:subjects")
async def show_subjects(callback: CallbackQuery) -> None:
    if await require_user_callback(callback) is None:
        return

    subjects = await get_subjects_with_counts()
    await safe_edit(
        callback, _subjects_text(), get_subjects_keyboard(subjects, "lesson")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lesson:subject:"))
async def show_lessons(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        subject_id = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer("Noto'g'ri bo'lim.", show_alert=True)
        return

    subject = await get_subject(subject_id)
    if subject is None:
        await callback.answer("Fan topilmadi.", show_alert=True)
        return

    lessons = await get_lessons(subject_id)
    completed_ids = await get_completed_lesson_ids(user["telegram_id"], subject_id)
    text = (
        f"{subject['emoji']} <b>{html.escape(subject['name'])}</b>\n\n"
        f"{html.escape(subject['description'])}\n\n"
        "Mavzuni tanlang:"
    )
    await safe_edit(
        callback,
        text,
        get_lessons_keyboard(lessons, completed_ids, subject_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lesson:view:"))
async def view_lesson(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        lesson_id = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    lesson = await get_lesson(lesson_id)
    if lesson is None:
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    user_id = user["telegram_id"]
    await mark_lesson_started(user_id, lesson_id)
    completed_ids = await get_completed_lesson_ids(user_id, lesson["subject_id"])
    is_completed = lesson_id in completed_ids

    await safe_edit(
        callback,
        _lesson_text(lesson, completed=is_completed),
        get_lesson_keyboard(
            lesson_id=lesson_id,
            subject_id=lesson["subject_id"],
            is_completed=is_completed,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lesson:complete:"))
async def mark_completed(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        lesson_id = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    lesson = await get_lesson(lesson_id)
    if lesson is None:
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    user_id = user["telegram_id"]
    is_new_completion = await complete_lesson(user_id, lesson_id)
    if not is_new_completion:
        await callback.answer(
            "Siz bu darsni allaqachon tugatgansiz ✅", show_alert=True
        )
        return

    await increment_goal(user_id, lessons=1)
    await safe_edit(
        callback,
        _lesson_text(lesson, completed=True),
        get_lesson_keyboard(
            lesson_id=lesson_id,
            subject_id=lesson["subject_id"],
            is_completed=True,
        ),
    )
    await callback.answer("Dars tugatildi ✅ Kunlik rejaga qo'shildi.")
    logger.info("Foydalanuvchi darsni tugatdi: id=%s, dars=%s", user_id, lesson_id)
