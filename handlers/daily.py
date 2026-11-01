"""Kunlik sovg'a, kunlik savol va haftalik missiyalar."""

from __future__ import annotations

import html
from datetime import timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.daily import (
    DAILY_CORRECT_XP,
    DAILY_WRONG_XP,
    current_week_key,
    get_daily_answer,
    get_daily_answer_days,
    get_daily_question,
    get_gift_days,
    has_daily_gift,
    save_daily_answer,
    week_start_date,
)
from handlers.common import (
    notify_rewards,
    progress_bar,
    react,
    require_user,
    require_user_callback,
    safe_edit,
)
from keyboards.inline_buttons import (
    get_daily_question_keyboard,
    get_daily_result_keyboard,
    get_gift_keyboard,
    get_missions_keyboard,
)
from keyboards.main_menu import BTN_DAILY_QUESTION, BTN_GIFT, BTN_MISSIONS
from services.daily import (
    MISSION_MAP,
    daily_streak,
    get_mission_states,
    gift_amount,
    mission_once_key,
)
from services.gamification import reward
from time_utils import local_today

router = Router(name="daily")

LETTERS = ("A", "B", "C", "D")


def _options(question) -> list[str]:
    return [
        str(question["option_a"]),
        str(question["option_b"]),
        str(question["option_c"]),
        str(question["option_d"]),
    ]


def _question_text(question) -> str:
    return "\n".join(
        [
            "❓ <b>Kunlik savol</b>",
            "━━━━━━━━━━━━━━",
            f"{question['subject_emoji']} "
            f"<b>{html.escape(str(question['subject_name']))}</b> · "
            f"{html.escape(str(question['lesson_title']))}",
            "",
            html.escape(str(question["question_text"])),
            "",
            "To'g'ri javobni tanlang. Bugun faqat bitta urinish bor.",
        ]
    )


def _result_text(
    question,
    selected: int,
    correct: bool,
    streak: int,
    *,
    xp: int | None = None,
) -> str:
    options = _options(question)
    correct_index = int(question["correct_option"])
    correct_letter = LETTERS[correct_index]
    selected_letter = LETTERS[selected]
    lines = [
        "✅ <b>To'g'ri javob!</b>" if correct else "❌ <b>Xato javob</b>",
        "━━━━━━━━━━━━━━",
        f"{question['subject_emoji']} "
        f"<b>{html.escape(str(question['subject_name']))}</b> · "
        f"{html.escape(str(question['lesson_title']))}",
        "",
        html.escape(str(question["question_text"])),
        "",
        f"Javobingiz: <b>{selected_letter}) "
        f"{html.escape(options[selected])}</b>",
        f"To'g'ri javob: <b>{correct_letter}) "
        f"{html.escape(options[correct_index])}</b>",
    ]
    explanation = str(question["explanation"]).strip()
    if explanation:
        lines.extend(["", f"💡 {html.escape(explanation)}"])
    if xp is not None:
        lines.extend(["", f"⭐ Mukofot: <b>+{xp} XP</b>"])
    lines.extend(["", f"🔥 Kunlik seriya: <b>{streak} kun</b>"])
    if xp is None:
        lines.append("Bugungi savolga allaqachon javob berdingiz. Ertaga yangisi keladi.")
    return "\n".join(lines)


async def _send_daily_question(target: Message, user_id: int) -> None:
    day = local_today()
    question = await get_daily_question(day)
    if question is None:
        await target.answer(
            "❓ Hozircha kunlik savol uchun mavzu topilmadi. Keyinroq urinib ko'ring."
        )
        return

    answer = await get_daily_answer(user_id, day)
    if answer is not None:
        days = await get_daily_answer_days(user_id)
        text = _result_text(
            question,
            int(answer["selected_option"]),
            bool(answer["is_correct"]),
            daily_streak(days),
        )
        keyboard = get_daily_result_keyboard(int(question["lesson_id"]))
    else:
        text = _question_text(question)
        keyboard = get_daily_question_keyboard(
            int(question["id"]), _options(question)
        )

    await target.answer(text, reply_markup=keyboard)
    await react(target, "❓")


@router.message(F.text == BTN_GIFT)
async def gift_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return
    await _send_gift(message, int(user["telegram_id"]))


async def _send_gift(target: Message, user_id: int) -> None:
    day = local_today()
    gift_days = await get_gift_days(user_id)

    if await has_daily_gift(user_id, day):
        text = "\n".join(
            [
                "🎁 <b>Kunlik sovg'a</b>",
                "",
                "Bugungi sovg'angizni allaqachon oldingiz.",
                f"🔥 Sovg'a seriyasi: <b>{daily_streak(gift_days)} kun</b>",
                "",
                "Ertaga yangi sovg'a sizni kutmoqda!",
            ]
        )
        await target.answer(text, reply_markup=get_gift_keyboard())
        return

    amount = gift_amount()
    result = await reward(user_id, amount, "gift", once_key=f"gift:{day}")

    gift_days.add(day)
    streak = daily_streak(gift_days)
    lines = [
        "🎁 <b>Kunlik sovg'a ochildi!</b>",
        "",
        f"Sizga <b>+{amount} XP</b> tushdi.",
        f"🔥 Sovg'a seriyasi: <b>{streak} kun</b>",
        "",
        "Ertaga yana kelib sovg'angizni oling!",
    ]
    if streak >= 3:
        lines.insert(4, "Zo'r ketmoqda — seriyani uzmang! 💪")
    await target.answer("\n".join(lines), reply_markup=get_gift_keyboard())
    await react(target, "🎁")
    await notify_rewards(target, result)


@router.message(F.text == BTN_DAILY_QUESTION)
async def daily_question_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return
    await _send_daily_question(message, int(user["telegram_id"]))


@router.callback_query(F.data == "daily:question")
async def daily_question_callback(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    await _send_daily_question(callback.message, int(user["telegram_id"]))
    await callback.answer()


@router.callback_query(F.data.startswith("daily:answer:"))
async def answer_daily_question(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or not callback.data:
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("Noto'g'ri amal.", show_alert=True)
        return

    try:
        question_id = int(parts[2])
        selected = int(parts[3])
    except ValueError:
        await callback.answer("Noto'g'ri amal.", show_alert=True)
        return
    if not 0 <= selected <= 3:
        await callback.answer("Noto'g'ri variant.", show_alert=True)
        return

    user_id = int(user["telegram_id"])
    day = local_today()
    question = await get_daily_question(day)
    if question is None or int(question["id"]) != question_id:
        await callback.answer(
            "Savol eskirgan. Kunlik savolni qayta oching.", show_alert=True
        )
        return

    existing = await get_daily_answer(user_id, day)
    if existing is not None:
        days = await get_daily_answer_days(user_id)
        text = _result_text(
            question,
            int(existing["selected_option"]),
            bool(existing["is_correct"]),
            daily_streak(days),
        )
        await safe_edit(callback, text, get_daily_result_keyboard(int(question["lesson_id"])))
        await callback.answer("Bugun allaqachon javob berdingiz.", show_alert=True)
        return

    correct = selected == int(question["correct_option"])
    saved = await save_daily_answer(
        user_id, day, question_id, selected, correct
    )
    if not saved:
        await callback.answer("Javob saqlanmadi, qayta urinib ko'ring.", show_alert=True)
        return

    amount = DAILY_CORRECT_XP if correct else DAILY_WRONG_XP
    result = await reward(
        user_id, amount, "daily", once_key=f"daily:{day}"
    )

    days = await get_daily_answer_days(user_id)
    text = _result_text(
        question,
        selected,
        correct,
        daily_streak(days),
        xp=amount,
    )
    await safe_edit(callback, text, get_daily_result_keyboard(int(question["lesson_id"])))
    await notify_rewards(callback.message, result)
    await react(callback.message, "✅" if correct else "❌")
    await callback.answer("To'g'ri ✅" if correct else "Xato ❌")


def _missions_text(states) -> str:
    start = week_start_date()
    end = start + timedelta(days=6)
    lines = [
        "🎯 <b>Haftalik missiyalar</b>",
        "━━━━━━━━━━━━━━",
        f"Hafta: {start:%d.%m}–{end:%d.%m} · {current_week_key()}",
        "",
    ]
    for state in states:
        mission = state.mission
        if state.claimed:
            mark = "✅"
        elif state.done:
            mark = "🎁"
        else:
            mark = "⏳"
        lines.append(f"{mark} {mission.emoji} <b>{mission.title}</b>")
        lines.append(
            f"{progress_bar(state.progress, mission.target)} "
            f"{state.progress}/{mission.target} · mukofot "
            f"<b>+{mission.reward_xp} XP</b>"
        )
        lines.append("")

    if any(state.done and not state.claimed for state in states):
        lines.append("Bajarilgan missiya mukofotini tugma orqali oling.")
    elif states and all(state.claimed for state in states):
        lines.append("Barcha missiyalar bajarildi! Yangi missiyalar dushanba kuni.")
    else:
        lines.append("Missiyalar har dushanba yangilanadi. Davom eting!")
    return "\n".join(lines)


async def _show_missions(target: Message, user_id: int) -> None:
    states = await get_mission_states(user_id)
    await target.answer(
        _missions_text(states), reply_markup=get_missions_keyboard(states)
    )


@router.message(F.text == BTN_MISSIONS)
async def missions_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await require_user(message)
    if user is None:
        return
    await _show_missions(message, int(user["telegram_id"]))


@router.callback_query(F.data == "missions:show")
async def missions_callback(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    states = await get_mission_states(int(user["telegram_id"]))
    await safe_edit(callback, _missions_text(states), get_missions_keyboard(states))
    await callback.answer("Missiyalar yangilandi ✅")


@router.callback_query(F.data.startswith("mission:claim:"))
async def claim_mission(callback: CallbackQuery) -> None:
    user = await require_user_callback(callback)
    if user is None or not callback.data:
        return

    code = callback.data.split(":", 2)[2]
    mission = MISSION_MAP.get(code)
    if mission is None:
        await callback.answer("Missiya topilmadi.", show_alert=True)
        return

    user_id = int(user["telegram_id"])
    states = await get_mission_states(user_id)
    state = next(
        (item for item in states if item.mission.code == code), None
    )
    if state is None:
        await callback.answer("Missiya topilmadi.", show_alert=True)
        return
    if state.claimed:
        await callback.answer("Bu mukofot allaqachon olingan.", show_alert=True)
        return
    if not state.done:
        await callback.answer(
            "Missiya hali bajarilmagan.", show_alert=True
        )
        return

    result = await reward(
        user_id,
        mission.reward_xp,
        "mission",
        once_key=mission_once_key(code),
    )
    if result.xp_gained <= 0:
        await callback.answer("Mukofot allaqachon olingan.", show_alert=True)
        return

    if isinstance(callback.message, Message):
        await notify_rewards(callback.message, result)
    states = await get_mission_states(user_id)
    await safe_edit(callback, _missions_text(states), get_missions_keyboard(states))
    await callback.answer(f"+{mission.reward_xp} XP ✅")
