"""Kunlik o'quv rejasi va maqsadlar."""

from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.goals import get_today_goal, set_goal_targets
from database.progress import get_activity_stats
from handlers.common import (
    progress_bar,
    require_user,
    require_user_callback,
    safe_edit,
)
from keyboards.inline_buttons import get_goal_keyboard
from keyboards.main_menu import BTN_DAILY_PLAN
from time_utils import local_now

router = Router(name="daily_plan")


async def _build_plan_text(user) -> str:
    user_id = user["telegram_id"]
    goal = await get_today_goal(user_id)
    activity = await get_activity_stats(user_id)

    target_lessons = int(goal["target_lessons"])
    target_quizzes = int(goal["target_quizzes"])
    done_lessons = int(goal["completed_lessons"])
    done_quizzes = int(goal["completed_quizzes"])

    lessons_done = done_lessons >= target_lessons
    quizzes_done = done_quizzes >= target_quizzes
    lessons_icon = "✅" if lessons_done else "⏳"
    quizzes_icon = "✅" if quizzes_done else "⏳"

    remaining_lessons = max(target_lessons - done_lessons, 0)
    remaining_quizzes = max(target_quizzes - done_quizzes, 0)

    if remaining_lessons == 0 and remaining_quizzes == 0:
        status = "🎉 <b>Bugungi maqsad bajarildi!</b> Ajoyib natija."
    else:
        status = (
            f"Qoldi: <b>{remaining_lessons}</b> dars, "
            f"<b>{remaining_quizzes}</b> test."
        )

    today = local_now().strftime("%d.%m.%Y")
    return (
        f"📅 <b>Bugungi reja</b> · {today}\n\n"
        f"👤 {html.escape(user['full_name'])}\n\n"
        f"📚 Darslar: <b>{done_lessons}/{target_lessons}</b>  "
        f"{progress_bar(done_lessons, target_lessons)} {lessons_icon}\n"
        f"📝 Testlar: <b>{done_quizzes}/{target_quizzes}</b>  "
        f"{progress_bar(done_quizzes, target_quizzes)} {quizzes_icon}\n\n"
        f"🔥 Ketma-ket kunlar: <b>{activity['streak']}</b>\n\n"
        f"{status}"
    )


@router.message(F.text == BTN_DAILY_PLAN)
async def daily_plan_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return

    goal = await get_today_goal(user["telegram_id"])
    await message.answer(
        await _build_plan_text(user),
        reply_markup=get_goal_keyboard(
            int(goal["target_lessons"]), int(goal["target_quizzes"])
        ),
    )


@router.callback_query(F.data == "goal:refresh")
async def refresh_plan(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    goal = await get_today_goal(user["telegram_id"])
    await safe_edit(
        callback,
        await _build_plan_text(user),
        get_goal_keyboard(
            int(goal["target_lessons"]), int(goal["target_quizzes"])
        ),
    )
    await callback.answer("Yangilandi ✅")


@router.callback_query(F.data.startswith("goal:set:"))
async def update_plan(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("Noto'g'ri maqsad.", show_alert=True)
        return

    try:
        target_lessons = int(parts[2])
        target_quizzes = int(parts[3])
    except ValueError:
        await callback.answer("Noto'g'ri maqsad.", show_alert=True)
        return

    if not (
        0 <= target_lessons <= 20
        and 0 <= target_quizzes <= 20
        and target_lessons + target_quizzes > 0
    ):
        await callback.answer("Maqsad qiymati noto'g'ri.", show_alert=True)
        return

    await set_goal_targets(user["telegram_id"], target_lessons, target_quizzes)
    await safe_edit(
        callback,
        await _build_plan_text(user),
        get_goal_keyboard(target_lessons, target_quizzes),
    )
    await callback.answer("Maqsad yangilandi ✅")
