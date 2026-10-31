"""Ichki (inline) tugmalar."""

from __future__ import annotations

from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

LEVELS: dict[str, str] = {
    "beginner": "🟢 Boshlang'ich",
    "intermediate": "🟡 O'rta",
    "advanced": "🔴 Yuqori",
}

OPTION_LETTERS = ("A", "B", "C", "D")


def get_levels_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in LEVELS.items():
        builder.button(text=label, callback_data=f"level:{code}")
    builder.adjust(1)
    return builder.as_markup()


def _subject_label(subject, best_scores: dict[int, int] | None) -> str:
    label = f"{subject['emoji']} {subject['name']}"
    if best_scores is not None:
        best = best_scores.get(int(subject["id"]))
        if best is not None:
            label += f" · {best}%"
        return label
    if "completed_count" in subject.keys():
        label += (
            f" · {int(subject['completed_count'])}/{int(subject['lesson_count'])}"
        )
    return label


def get_subjects_keyboard(
    subjects: Sequence,
    prefix: str,
    best_scores: dict[int, int] | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for subject in subjects:
        builder.button(
            text=_subject_label(subject, best_scores),
            callback_data=f"{prefix}:subject:{subject['id']}",
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"))
    return builder.as_markup()


def get_lessons_keyboard(
    lessons: Sequence, completed_ids: set[int], subject_id: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lesson in lessons:
        mark = "✅" if lesson["id"] in completed_ids else "📖"
        builder.button(
            text=f"{mark} {lesson['order_index']}. {lesson['title']}",
            callback_data=f"lesson:view:{lesson['id']}",
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Fanlar", callback_data="lesson:subjects"
        ),
        InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def _lesson_nav_row(
    builder: InlineKeyboardBuilder,
    *,
    prev_lesson_id: int | None,
    next_lesson_id: int | None,
) -> None:
    buttons = []
    if prev_lesson_id is not None:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi dars",
                callback_data=f"lesson:view:{prev_lesson_id}",
            )
        )
    if next_lesson_id is not None:
        buttons.append(
            InlineKeyboardButton(
                text="➡️ Keyingi dars",
                callback_data=f"lesson:view:{next_lesson_id}",
            )
        )
    if buttons:
        builder.row(*buttons)


def get_lesson_keyboard(
    *,
    lesson_id: int,
    subject_id: int,
    is_completed: bool,
    is_favorite: bool = False,
    prev_lesson_id: int | None = None,
    next_lesson_id: int | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📖 Batafsil o'qish", callback_data=f"lesson:read:{lesson_id}"
    )
    if not is_completed:
        builder.button(
            text="✅ Darsni tugatdim",
            callback_data=f"lesson:complete:{lesson_id}",
        )
    builder.button(
        text="🧠 AI Ustozga so'rash", callback_data=f"lesson:ask:{lesson_id}"
    )
    builder.button(
        text=(
            "⭐ Sevimlilardan olib tashlash"
            if is_favorite
            else "⭐ Sevimlilarga qo'shish"
        ),
        callback_data=f"lesson:fav:{lesson_id}",
    )
    builder.button(
        text="📝 Test yechish", callback_data=f"quiz:subject:{subject_id}"
    )
    builder.adjust(1)
    _lesson_nav_row(
        builder,
        prev_lesson_id=prev_lesson_id,
        next_lesson_id=next_lesson_id,
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Darslar", callback_data=f"lesson:subject:{subject_id}"
        ),
        InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def get_lesson_details_keyboard(
    *,
    lesson_id: int,
    subject_id: int,
    is_completed: bool,
    is_favorite: bool = False,
    prev_lesson_id: int | None = None,
    next_lesson_id: int | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🖼️ Kartochkaga qaytish",
        callback_data=f"lesson:view:{lesson_id}",
    )
    if not is_completed:
        builder.button(
            text="✅ Darsni tugatdim",
            callback_data=f"lesson:complete:{lesson_id}",
        )
    builder.button(
        text="🧠 AI Ustozga so'rash", callback_data=f"lesson:ask:{lesson_id}"
    )
    builder.button(
        text=(
            "⭐ Sevimlilardan olib tashlash"
            if is_favorite
            else "⭐ Sevimlilarga qo'shish"
        ),
        callback_data=f"lesson:fav:{lesson_id}",
    )
    builder.button(
        text="📝 Test yechish", callback_data=f"quiz:subject:{subject_id}"
    )
    builder.adjust(1)
    _lesson_nav_row(
        builder,
        prev_lesson_id=prev_lesson_id,
        next_lesson_id=next_lesson_id,
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Darslar", callback_data=f"lesson:subject:{subject_id}"
        ),
        InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def get_quiz_options_keyboard(question_id: int, options: Sequence[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(options[:4]):
        label = f"{OPTION_LETTERS[index]}) {option}"
        if len(label) > 60:
            label = f"{label[:57]}..."
        builder.button(
            text=label, callback_data=f"quiz:answer:{question_id}:{index}"
        )
    builder.adjust(1)
    return builder.as_markup()


def get_quiz_result_keyboard(subject_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔁 Qayta yechish", callback_data=f"quiz:subject:{subject_id}"
    )
    builder.button(
        text="📚 Darslarni takrorlash",
        callback_data=f"lesson:subject:{subject_id}",
    )
    builder.button(text="📚 Boshqa fanlar", callback_data="quiz:subjects")
    builder.button(text="🏠 Bosh menyu", callback_data="menu:home")
    builder.adjust(1)
    return builder.as_markup()


def get_search_results_keyboard(lessons: Sequence) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lesson in lessons:
        label = f"📖 {lesson['title']}"
        if len(label) > 60:
            label = f"{label[:57]}..."
        builder.button(
            text=label, callback_data=f"lesson:view:{lesson['id']}"
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="📚 Darslar", callback_data="lesson:subjects"),
        InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def get_progress_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏅 Yutuqlarim", callback_data="stats:achievements"),
        InlineKeyboardButton(
            text="🏆 Haftalik reyting", callback_data="stats:leaderboard"
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Sevimlilarim", callback_data="stats:favorites"),
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="stats:refresh"),
    )
    builder.row(
        InlineKeyboardButton(text="📝 Test yechish", callback_data="quiz:subjects")
    )
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"))
    return builder.as_markup()


def get_stats_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Natijalar", callback_data="stats:refresh"),
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def get_favorite_lessons_keyboard(lessons: Sequence) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lesson in lessons:
        label = f"{lesson['subject_emoji']} {lesson['title']}"
        if len(label) > 60:
            label = f"{label[:57]}..."
        builder.button(text=label, callback_data=f"lesson:view:{lesson['id']}")
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="⬅️ Natijalar", callback_data="stats:refresh"),
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def get_ai_answer_keyboard(related: Sequence[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lesson_id, title in list(related)[:2]:
        label = f"📖 {title}"
        if len(label) > 60:
            label = f"{label[:57]}..."
        builder.button(text=label, callback_data=f"lesson:view:{lesson_id}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"))
    return builder.as_markup()


def get_goal_keyboard(target_lessons: int, target_quizzes: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lessons, quizzes, label in (
        (1, 1, "🟢 Oson — 1 dars + 1 test"),
        (2, 2, "🟡 O'rta — 2 dars + 2 test"),
        (3, 3, "🔴 Intensiv — 3 dars + 3 test"),
    ):
        mark = " ✅" if (lessons, quizzes) == (target_lessons, target_quizzes) else ""
        builder.button(
            text=f"{label}{mark}",
            callback_data=f"goal:set:{lessons}:{quizzes}",
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="goal:refresh"),
        InlineKeyboardButton(text="🏠 Menyu", callback_data="menu:home"),
    )
    return builder.as_markup()


def get_settings_keyboard(
    level: str, notifications_enabled: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in LEVELS.items():
        mark = " ✅" if code == level else ""
        builder.button(
            text=f"{label}{mark}", callback_data=f"settings:level:{code}"
        )
    builder.adjust(1)

    toggle_label = (
        "🔔 Bildirishnomalar: Yoqilgan"
        if notifications_enabled
        else "🔕 Bildirishnomalar: O'chirilgan"
    )
    builder.row(
        InlineKeyboardButton(text=toggle_label, callback_data="settings:notify")
    )
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"))
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistika", callback_data="admin:stats")
    builder.button(text="📢 Xabar yuborish", callback_data="admin:broadcast")
    builder.row(
        InlineKeyboardButton(text="💾 Baza zaxirasi", callback_data="admin:backup"),
        InlineKeyboardButton(text="📤 CSV eksport", callback_data="admin:export"),
    )
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:home"))
    builder.adjust(1)
    return builder.as_markup()


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Yuborish", callback_data="admin:broadcast_confirm"
    )
    builder.button(
        text="❌ Bekor qilish", callback_data="admin:broadcast_cancel"
    )
    builder.adjust(2)
    return builder.as_markup()


def get_broadcast_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Bekor qilish", callback_data="admin:broadcast_cancel"
    )
    return builder.as_markup()
