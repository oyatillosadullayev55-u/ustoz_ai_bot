"""Darslar bo'limi: fanlar, mavzular va darsni tugatish."""

from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.content import (
    get_lesson,
    get_lessons,
    get_subject,
    get_subjects_with_counts,
    search_lessons,
)
from database.goals import increment_goal
from database.progress import (
    complete_lesson,
    get_completed_lesson_ids,
    mark_lesson_started,
)
from handlers.common import (
    progress_bar,
    require_user,
    require_user_callback,
    safe_edit,
)
from keyboards.inline_buttons import (
    get_lesson_keyboard,
    get_lessons_keyboard,
    get_search_results_keyboard,
    get_subjects_keyboard,
)
from keyboards.main_menu import BTN_LESSONS, get_main_menu_keyboard
from services.lesson_media import get_lesson_photo, remember_lesson_file_id

router = Router(name="lessons")
logger = logging.getLogger(__name__)

SEARCH_MIN_LENGTH = 2
SEARCH_MAX_LENGTH = 100
SEARCH_RESULTS_LIMIT = 5
LESSON_CAPTION_LIMIT = 1024


def _subjects_text(subjects) -> str:
    total_lessons = sum(int(subject["lesson_count"]) for subject in subjects)
    return (
        "📚 <b>Darslar</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        "🖼️ Har bir dars rasmli kartochka ko'rinishida ochiladi.\n"
        f"📖 {len(subjects)} fan · {total_lessons} dars\n\n"
        "Fan tanlang:"
    )


def _lessons_text(subject, lessons, completed_ids: set[int]) -> str:
    completed_count = sum(
        1 for lesson in lessons if int(lesson["id"]) in completed_ids
    )
    return (
        f"{subject['emoji']} "
        f"<b>{html.escape(str(subject['name']).upper())}</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        f"{html.escape(subject['description'])}\n\n"
        f"📊 {completed_count}/{len(lessons)} dars · "
        f"{progress_bar(completed_count, len(lessons))}\n\n"
        "Mavzuni tanlang:"
    )


def build_lesson_card(lesson, *, completed: bool) -> str:
    status = (
        "✅ <b>Tugatilgan.</b> Natijangizda saqlandi."
        if completed
        else "💡 <b>Maslahat:</b> Matnni o'qib, «Darsni tugatdim» tugmasini bosing."
    )
    return (
        f"{lesson['subject_emoji']} "
        f"<b>{html.escape(str(lesson['subject_name']).upper())}</b>"
        f" · <b>{lesson['order_index']}-DARS</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"📖 <b>{html.escape(lesson['title'])}</b>\n\n"
        f"{html.escape(str(lesson['content']).strip())}\n\n"
        "━━━━━━━━━━━━━━\n"
        f"{status}"
    )


async def _send_lesson_card(
    callback: CallbackQuery, lesson, *, completed: bool
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        return

    text = build_lesson_card(lesson, completed=completed)
    lesson_id = int(lesson["id"])
    keyboard = get_lesson_keyboard(
        lesson_id=lesson_id,
        subject_id=int(lesson["subject_id"]),
        is_completed=completed,
    )
    photo = get_lesson_photo(lesson_id)

    if photo is None or len(text) > LESSON_CAPTION_LIMIT:
        await safe_edit(callback, text, keyboard)
        return

    if message.photo:
        try:
            await message.edit_caption(caption=text, reply_markup=keyboard)
            return
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    try:
        sent = await message.answer_photo(
            photo=photo, caption=text, reply_markup=keyboard
        )
    except TelegramBadRequest:
        logger.warning("Dars rasmini yuborib bo'lmadi: dars=%s", lesson_id)
        await message.answer(text, reply_markup=keyboard)
        return

    if isinstance(sent, Message) and sent.photo:
        remember_lesson_file_id(lesson_id, sent.photo[-1].file_id)


def _search_results_text(query: str, lessons) -> str:
    lines = [
        "🔎 <b>Qidiruv natijalari</b>",
        "━━━━━━━━━━━━━━",
        "",
        f"So'rov: <i>{html.escape(query)}</i>",
        f"Topildi: <b>{len(lessons)}</b> ta dars",
        "",
    ]
    for number, lesson in enumerate(lessons, 1):
        lines.append(
            f"{number}. {lesson['subject_emoji']} "
            f"<b>{html.escape(lesson['title'])}</b> — "
            f"{html.escape(lesson['subject_name'])}"
        )
    lines.extend(["", "Mavzuni ochish uchun tugmani bosing:"])
    return "\n".join(lines)


@router.message(Command("qidiruv", "search"))
async def search_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        return
    if await require_user(message) is None:
        return

    parts = (message.text or "").split(maxsplit=1)
    query = parts[1].strip() if len(parts) == 2 else ""

    if not query:
        await message.answer(
            "🔎 <b>Dars qidiruvi</b>\n\n"
            "Mavzu nomini yozing: <code>/qidiruv fotosintez</code>"
        )
        return

    if len(query) < SEARCH_MIN_LENGTH:
        await message.answer(
            "Qidiruv so'zi juda qisqa. Kamida 2 ta belgi kiriting."
        )
        return

    if len(query) > SEARCH_MAX_LENGTH:
        await message.answer(
            f"Qidiruv matni juda uzun. {SEARCH_MAX_LENGTH} belgidan oshirmang."
        )
        return

    results = await search_lessons(query, limit=SEARCH_RESULTS_LIMIT)
    if not results:
        await message.answer(
            f"🔎 «{html.escape(query)}» bo'yicha dars topilmadi.\n\n"
            "Boshqa so'z bilan urinib ko'ring yoki fanlar ro'yxatidan tanlang.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(
        _search_results_text(query, results),
        reply_markup=get_search_results_keyboard(results),
    )
    logger.info(
        "Dars qidiruvi: user=%s, natija=%s",
        message.from_user.id,
        len(results),
    )


@router.message(F.text == BTN_LESSONS)
async def lessons_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    if await require_user(message) is None:
        return

    subjects = await get_subjects_with_counts()
    await message.answer(
        _subjects_text(subjects),
        reply_markup=get_subjects_keyboard(subjects, "lesson"),
    )


@router.callback_query(F.data == "lesson:subjects")
async def show_subjects(callback: CallbackQuery) -> None:
    if await require_user_callback(callback) is None:
        return

    subjects = await get_subjects_with_counts()
    await safe_edit(
        callback,
        _subjects_text(subjects),
        get_subjects_keyboard(subjects, "lesson"),
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
    await safe_edit(
        callback,
        _lessons_text(subject, lessons, completed_ids),
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

    await _send_lesson_card(callback, lesson, completed=is_completed)
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
    await _send_lesson_card(callback, lesson, completed=True)
    await callback.answer("Dars tugatildi ✅ Kunlik rejaga qo'shildi.")
    logger.info("Foydalanuvchi darsni tugatdi: id=%s, dars=%s", user_id, lesson_id)
