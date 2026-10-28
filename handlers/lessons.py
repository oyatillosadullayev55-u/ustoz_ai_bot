"""Darslar bo'limi: fanlar, mavzular va darsni tugatish."""

from __future__ import annotations

import html
import json
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

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
    get_lesson_details_keyboard,
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
LESSON_TEXT_LIMIT = 4000

COURSE_URLS: dict[int, str] = {
    1101: "https://osonstudio.uz/prompt-kurs",
    1102: "https://osonstudio.uz/airasm-kurs",
    1103: "https://osonstudio.uz/aivideo-kurs",
    1104: "https://osonstudio.uz/agent-kurs",
    1105: "https://osonstudio.uz/loop-kurs",
    1106: "https://osonstudio.uz/excel-kurs",
    1107: "https://osonstudio.uz/buxgalteriya-kurs",
    1108: "https://osonstudio.uz/xavfsizlik-kurs",
    1109: "https://osonstudio.uz/windows-buyruqlari-kurs",
    1110: "https://osonstudio.uz/kompyuter-arxitekturasi-kurs",
    1111: "https://osonstudio.uz/operatsion-tizimlar-kurs",
    1112: "https://osonstudio.uz/algoritmlar-kurs",
    1113: "https://osonstudio.uz/malumotlar-tuzilmasi-kurs",
    1114: "https://osonstudio.uz/malumotlar-bazasi-kurs",
    1115: "https://osonstudio.uz/kompyuter-tarmoqlari-kurs",
}

LESSON_LEVEL_LABELS = {
    "beginner": "🟢 Boshlang'ich",
    "intermediate": "🟡 O'rta",
    "advanced": "🔴 Yuqori",
}


def _subjects_text(subjects) -> str:
    total_lessons = sum(int(subject["lesson_count"]) for subject in subjects)
    return (
        "📚 <b>Darslar</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        "🖼️ Har bir dars rasmli kartochka ko'rinishida ochiladi.\n"
        "🎯 Qisqa mazmun, asosiy fikrlar, batafsil izoh va mini mashq.\n"
        f"📖 {len(subjects)} fan · {total_lessons} dars\n\n"
        "Fan tanlang:"
    )


def _lessons_text(subject, lessons, completed_ids: set[int]) -> str:
    completed_count = sum(
        1 for lesson in lessons if int(lesson["id"]) in completed_ids
    )
    durations = [int(lesson["duration_min"]) for lesson in lessons]
    duration_note = ""
    if durations:
        duration_note = f"⏱️ Har bir dars {min(durations)}–{max(durations)} daqiqa.\n"

    is_prog = (subject["code"] == "programming") if "code" in subject.keys() else False
    title_suffix = " YO'NALISHLARI" if is_prog else ""
    choose_prompt = "Yo'nalishni tanlang:" if is_prog else "Mavzuni tanlang:"

    return (
        f"{subject['emoji']} "
        f"<b>{html.escape(str(subject['name']).upper())}{title_suffix}</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        f"{html.escape(subject['description'])}\n\n"
        f"📊 {completed_count}/{len(lessons)} dars · "
        f"{progress_bar(completed_count, len(lessons))}\n"
        f"{duration_note}\n"
        f"{choose_prompt}"
    )


def _key_points(raw: str) -> list[str]:
    try:
        value = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _level_label(lesson) -> str:
    return LESSON_LEVEL_LABELS.get(
        str(lesson["level"]), "🟢 Boshlang'ich"
    )


def _lesson_status(completed: bool) -> str:
    if completed:
        return "✅ <b>Tugatilgan.</b> Natijangizda saqlandi."
    return (
        "💡 <b>Maslahat:</b> «Batafsil o'qish» bilan mavzuni chuqurroq "
        "o'rganing."
    )


def build_lesson_card(lesson, *, completed: bool) -> str:
    summary = str(lesson["summary"]).strip()
    if not summary:
        summary = " ".join(str(lesson["content"]).split())[:220]

    lines = [
        f"{lesson['subject_emoji']} "
        f"<b>{html.escape(str(lesson['subject_name']).upper())}</b>"
        f" · <b>{lesson['order_index']}-DARS</b>",
        "━━━━━━━━━━━━━━",
        f"📖 <b>{html.escape(str(lesson['title']))}</b>",
        "",
        f"🎯 {html.escape(summary)}",
    ]

    points = _key_points(str(lesson["key_points"]))
    if points:
        lines.extend(["", "🔑 <b>Asosiy fikrlar</b>"])
        lines.extend(f"• {html.escape(point)}" for point in points[:4])

    lines.extend(
        [
            "",
            f"⏱️ {lesson['duration_min']} daqiqa · {_level_label(lesson)}",
            "━━━━━━━━━━━━━━",
            _lesson_status(completed),
        ]
    )
    return "\n".join(lines)


def build_lesson_details(lesson, *, completed: bool) -> str:
    content = str(lesson["content"]).strip()
    header = (
        f"📖 <b>{html.escape(str(lesson['title']))}</b>\n"
        f"{lesson['subject_emoji']} "
        f"{html.escape(str(lesson['subject_name']))} · "
        f"{lesson['order_index']}-dars\n"
        f"⏱️ {lesson['duration_min']} daqiqa · {_level_label(lesson)}\n"
        "━━━━━━━━━━━━━━\n\n"
    )
    footer = (
        "\n\n━━━━━━━━━━━━━━\n"
        f"{_lesson_status(completed)}\n"
        "📝 Darsni tugatgach, test orqali bilimingizni sinang."
    )
    escaped = html.escape(content)
    room = LESSON_TEXT_LIMIT - len(header) - len(footer)
    if room > 0 and len(escaped) > room:
        escaped = escaped[: room - 1].rstrip() + "…"
    return f"{header}{escaped}{footer}"


async def _adjacent_lesson_ids(lesson) -> tuple[int | None, int | None]:
    lessons = await get_lessons(int(lesson["subject_id"]))
    lesson_ids = [int(item["id"]) for item in lessons]
    current_id = int(lesson["id"])
    if current_id not in lesson_ids:
        return None, None
    index = lesson_ids.index(current_id)
    previous_id = lesson_ids[index - 1] if index > 0 else None
    next_id = lesson_ids[index + 1] if index + 1 < len(lesson_ids) else None
    return previous_id, next_id


async def _send_lesson_card(
    callback: CallbackQuery, lesson, *, completed: bool
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        return

    text = build_lesson_card(lesson, completed=completed)
    lesson_id = int(lesson["id"])
    previous_id, next_id = await _adjacent_lesson_ids(lesson)
    keyboard = get_lesson_keyboard(
        lesson_id=lesson_id,
        subject_id=int(lesson["subject_id"]),
        is_completed=completed,
        prev_lesson_id=previous_id,
        next_lesson_id=next_id,
        url=COURSE_URLS.get(lesson_id),
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


async def _send_lesson_details(
    callback: CallbackQuery, lesson, *, completed: bool
) -> None:
    previous_id, next_id = await _adjacent_lesson_ids(lesson)
    await safe_edit(
        callback,
        build_lesson_details(lesson, completed=completed),
        get_lesson_details_keyboard(
            lesson_id=int(lesson["id"]),
            subject_id=int(lesson["subject_id"]),
            is_completed=completed,
            prev_lesson_id=previous_id,
            next_lesson_id=next_id,
            url=COURSE_URLS.get(int(lesson["id"])),
        ),
    )


def _is_details_view(message: Message) -> bool:
    markup = message.reply_markup
    if not isinstance(markup, InlineKeyboardMarkup):
        return False
    return any(
        button.text == "🖼️ Kartochkaga qaytish"
        for row in markup.inline_keyboard
        for button in row
    )


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


@router.callback_query(F.data.startswith("lesson:read:"))
async def read_lesson(callback: CallbackQuery) -> None:
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
    await _send_lesson_details(
        callback, lesson, completed=lesson_id in completed_ids
    )
    await callback.answer("Batafsil izoh ochildi 📖")


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
    if isinstance(callback.message, Message) and _is_details_view(callback.message):
        await _send_lesson_details(callback, lesson, completed=True)
    else:
        await _send_lesson_card(callback, lesson, completed=True)
    await callback.answer("Dars tugatildi ✅ Kunlik rejaga qo'shildi.")
    logger.info("Foydalanuvchi darsni tugatdi: id=%s, dars=%s", user_id, lesson_id)
