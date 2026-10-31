"""Foydalanuvchi natijalari va statistikasi."""

from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.progress import (
    get_activity_stats,
    get_recent_results,
    get_user_stats,
)
from handlers.common import (
    progress_bar,
    require_user,
    require_user_callback,
    safe_edit,
)
from keyboards.inline_buttons import LEVELS, get_progress_keyboard
from keyboards.main_menu import BTN_PROGRESS
from services.gamification import get_profile
from time_utils import format_local_date

router = Router(name="progress")


async def _build_stats_text(user) -> str:
    user_id = user["telegram_id"]
    stats = await get_user_stats(user_id)
    activity = await get_activity_stats(user_id)
    recent = await get_recent_results(user_id, limit=5)
    profile = await get_profile(user_id)

    level_label = LEVELS.get(user["level"], user["level"])
    rank = profile["rank"]
    next_rank_item = profile["next_rank"]
    xp = int(profile["xp"])

    lines = [
        "📊 <b>Mening natijalarim</b>",
        "",
        f"👤 {html.escape(user['full_name'])}",
        f"🎯 Bilim darajasi: {level_label}",
        f"{rank.emoji} Darajangiz: <b>{rank.name}</b> · <b>{xp} XP</b>",
    ]

    if next_rank_item is not None:
        needed = int(next_rank_item.min_xp) - xp
        lines.append(
            f"⏳ {next_rank_item.emoji} {next_rank_item.name} gacha: "
            f"<b>{needed} XP</b> "
            f"{progress_bar(xp - rank.min_xp, int(next_rank_item.min_xp) - rank.min_xp)}"
        )

    lines.extend(
        [
            f"🏅 Yutuqlar: <b>{profile['achievements']}/"
            f"{profile['total_achievements']}</b> · "
            f"Haftalik: <b>{profile['weekly_xp']} XP</b>",
            "",
            f"📚 Tugatilgan darslar: <b>{stats['lessons']}</b>",
            f"📝 Yechilgan testlar: <b>{stats['quizzes']}</b>",
            f"⭐ O'rtacha natija: <b>{round(stats['average'])}%</b>",
            f"🏆 Eng yuqori natija: <b>{stats['best']}%</b>",
            f"🔥 Ketma-ket kunlar: <b>{activity['streak']}</b>",
            f"🗓 Faol kunlar: <b>{activity['active_days']}</b>",
            f"🤖 AI savollar: <b>{stats['ai_messages']}</b>",
            "",
            "🕘 <b>So'nggi natijalar:</b>",
        ]
    )

    if not recent:
        lines.append("Hali test yechilmagan. 📝 Testlar bo'limidan boshlang.")
    else:
        for result in recent:
            lines.append(
                f"• {format_local_date(result['created_at'])} — "
                f"{result['subject_emoji']} {html.escape(result['subject_name'])}: "
                f"<b>{result['score_percent']}%</b> "
                f"({result['correct_answers']}/{result['total_questions']})"
            )

    return "\n".join(lines)


@router.message(F.text == BTN_PROGRESS)
async def progress_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return

    await message.answer(
        await _build_stats_text(user), reply_markup=get_progress_keyboard()
    )


@router.callback_query(F.data == "stats:refresh")
async def refresh_progress(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    await safe_edit(
        callback,
        await _build_stats_text(user),
        get_progress_keyboard(),
    )
    await callback.answer("Yangilandi ✅")
