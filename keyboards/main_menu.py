"""Bosh menyu va AI rejimi klaviaturalari."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_AI_TUTOR = "🧠 AI Ustoz"
BTN_LESSONS = "📚 Darslar"
BTN_QUIZZES = "📝 Testlar"
BTN_PROGRESS = "📊 Mening natijalarim"
BTN_DAILY_PLAN = "📅 Kunlik reja"
BTN_SETTINGS = "⚙️ Sozlamalar"

BTN_AI_EXIT = "⬅️ Chiqish"

MAIN_MENU_TEXTS = frozenset(
    {
        BTN_AI_TUTOR,
        BTN_LESSONS,
        BTN_QUIZZES,
        BTN_PROGRESS,
        BTN_DAILY_PLAN,
        BTN_SETTINGS,
    }
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_AI_TUTOR), KeyboardButton(text=BTN_LESSONS)],
            [KeyboardButton(text=BTN_QUIZZES), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_DAILY_PLAN), KeyboardButton(text=BTN_SETTINGS)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Bo'limni tanlang...",
    )


def get_ai_mode_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_AI_EXIT)]],
        resize_keyboard=True,
        input_field_placeholder="Savolingizni yozing...",
    )
