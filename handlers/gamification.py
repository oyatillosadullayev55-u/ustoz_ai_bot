"""Yutuqlar, haftalik reyting va sevimli darslar ekranlari."""

from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.favorites import get_favorite_lessons
from handlers.common import require_user_callback, safe_edit
from keyboards.inline_buttons import (
    get_favorite_lessons_keyboard,
    get_stats_back_keyboard,
)
from services.gamification import (
    ACHIEVEMENTS,
    get_achievements_with_state,
    get_leaderboard,
)

router = Router(name="gamification")

MEDALS = ("🥇", "🥈", "🥉")


def _short(text: str, limit: int = 24) -> str:
    value = " ".join(str(text).split())
    return value if len(value) <= limit else f"{value[: limit - 1]}…"


def _achievements_text(rows) -> str:
    unlocked = sum(1 for _, state in rows if state)
    lines = [
        "🏅 <b>Yutuqlarim</b>",
        "━━━━━━━━━━━━━━",
        f"Ochilgan: <b>{unlocked}/{len(ACHIEVEMENTS)}</b>",
        "",
    ]
    for item, state in rows:
        mark = "✅" if state else "🔒"
        lines.append(f"{mark} {item.emoji} <b>{item.title}</b> — {item.description}")
    lines.extend(
        [
            "",
            "💡 Har bir yutuq <b>+15 XP</b> beradi. Yangi darslar, testlar va "
            "kunlik maqsadlar bilan ularni oching.",
        ]
    )
    return "\n".join(lines)


def _leaderboard_text(data: dict) -> str:
    rows = data["rows"]
    lines = [
        "🏆 <b>Haftalik reyting</b>",
        "━━━━━━━━━━━━━━",
        "So'nggi 7 kunda to'plangan XP bo'yicha:",
        "",
    ]

    if not rows:
        lines.append("Haftalik reyting hali bo'sh.")
        lines.append("Birinchi darsni tugatib, ro'yxatga kiring! 🚀")
        return "\n".join(lines)

    for position, row in enumerate(rows, 1):
        medal = MEDALS[position - 1] if position <= 3 else f"{position}."
        name = html.escape(_short(row["full_name"]))
        lines.append(f"{medal} {name} — <b>{int(row['week_xp'])} XP</b>")

    lines.append("")
    user_rank = data["user_rank"]
    user_week_xp = int(data["user_week_xp"])
    if user_rank is None:
        lines.append("Siz hali bu hafta XP to'plamadingiz.")
    elif user_rank <= len(rows):
        lines.append(f"🎯 Sizning o'rningiz: <b>#{user_rank}</b> · {user_week_xp} XP")
    else:
        lines.append(
            f"🎯 Sizning o'rningiz: <b>#{user_rank}</b> · {user_week_xp} XP "
            f"({data['total_players']} ishtirokchi ichida)"
        )
    return "\n".join(lines)


@router.callback_query(F.data == "stats:achievements")
async def show_achievements(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    rows = await get_achievements_with_state(user["telegram_id"])
    await safe_edit(callback, _achievements_text(rows), get_stats_back_keyboard())
    await callback.answer("Yutuqlar yangilandi ✅")


@router.callback_query(F.data == "stats:leaderboard")
async def show_leaderboard(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    data = await get_leaderboard(user["telegram_id"])
    await safe_edit(callback, _leaderboard_text(data), get_stats_back_keyboard())
    await callback.answer("Reyting yangilandi ✅")


@router.callback_query(F.data == "stats:favorites")
async def show_favorites(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    lessons = await get_favorite_lessons(user["telegram_id"])
    if not lessons:
        text = (
            "⭐ <b>Sevimli darslarim</b>\n\n"
            "Hali sevimli dars yo'q.\n\n"
            "Dars kartochkasidagi <b>⭐ Sevimlilarga qo'shish</b> tugmasi orqali "
            "yoqtirgan mavzularingizni saqlang."
        )
    else:
        lines = [
            "⭐ <b>Sevimli darslarim</b>",
            f"Jami: <b>{len(lessons)}</b> ta dars",
            "",
        ]
        for lesson in lessons:
            lines.append(
                f"{lesson['subject_emoji']} "
                f"<b>{html.escape(str(lesson['title']))}</b> — "
                f"{html.escape(str(lesson['subject_name']))}"
            )
        lines.append("")
        lines.append("Darsni ochish uchun tugmani bosing:")
        text = "\n".join(lines)

    await safe_edit(callback, text, get_favorite_lessons_keyboard(lessons))
    await callback.answer()
