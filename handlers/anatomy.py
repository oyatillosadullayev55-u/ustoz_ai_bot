"""Anatomiya: vaqt cheklangan testlar va natijalar."""

from __future__ import annotations

import asyncio
import html
import logging
import time

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import BASE_DIR
from database.anatomy import (
    ANATOMY_SUBJECT_ID,
    count_anatomy_questions,
    delete_anatomy_session,
    get_anatomy_question,
    get_anatomy_questions,
    get_anatomy_questions_by_ids,
    load_anatomy_session,
    save_anatomy_session,
)
from database.goals import increment_goal
from database.quizzes import get_subject_best_score, save_quiz_result
from handlers.common import (
    is_not_modified_error,
    progress_bar,
    react,
    require_user_callback,
    reward_notice,
)
from keyboards.inline_buttons import (
    ANATOMY_MODE_LABELS,
    ANATOMY_MODES,
    OPTION_LETTERS,
    get_anatomy_menu_keyboard,
    get_anatomy_options_keyboard,
    get_anatomy_result_keyboard,
)
from services.gamification import (
    XP_GOAL_BONUS,
    XP_PERFECT_BONUS,
    XP_QUIZ_BASE,
    XP_QUIZ_PER_CORRECT,
    combine_rewards,
    reward,
)
from time_utils import local_today

router = Router(name="anatomy")
logger = logging.getLogger(__name__)

ANATOMY_BANNER = BASE_DIR / "assets" / "anatomy_banner.png"
OPTION_FIELDS = ("option_a", "option_b", "option_c", "option_d")
REVIEW_LIMIT = 8
STALE_TEXT = (
    "⏳ Bu test yakunlangan yoki bekor qilingan.\n"
    "Yangi testni 📚 Darslar → 🫀 Anatomiya orqali boshlang."
)

_timers: dict[int, asyncio.Task] = {}
_locks: dict[int, asyncio.Lock] = {}
_sessions: dict[int, dict] = {}


def _lock_for(user_id: int) -> asyncio.Lock:
    lock = _locks.get(user_id)
    if lock is None:
        lock = asyncio.Lock()
        _locks[user_id] = lock
    return lock


def _cancel_timer(user_id: int) -> None:
    task = _timers.pop(user_id, None)
    if task is not None and task is not asyncio.current_task() and not task.done():
        task.cancel()


async def _load_session(user_id: int) -> dict | None:
    """Faol testni xotiradan, bo'lmasa bazadan oladi."""
    session = _sessions.get(user_id)
    if session is not None:
        return session
    session = await load_anatomy_session(user_id)
    if session is not None:
        _sessions[user_id] = session
    return session


async def _store_session(user_id: int, data: dict) -> None:
    _sessions[user_id] = data
    await save_anatomy_session(user_id, data)


async def _drop_session(user_id: int) -> dict | None:
    _cancel_timer(user_id)
    session = _sessions.pop(user_id, None)
    await delete_anatomy_session(user_id)
    return session


def _start_timer(bot, user_id: int) -> None:
    _cancel_timer(user_id)
    _timers[user_id] = asyncio.create_task(_timeout_task(bot, user_id))


def _clock(seconds: float | int) -> str:
    value = max(0, int(seconds))
    return f"{value // 60:02d}:{value % 60:02d}"


def _short(text: str, limit: int) -> str:
    value = " ".join(str(text).split())
    if len(value) <= limit:
        return value
    return f"{value[: limit - 1].rstrip()}…"


def _menu_text(total: int, best: int | None) -> str:
    best_line = (
        f"🏆 Eng yaxshi natijangiz: <b>{best}%</b>"
        if best is not None
        else "🏆 Hali natija yo'q — birinchi urinish!"
    )
    return (
        "🫀 <b>ANATOMIYA</b>\n"
        "━━━━━━━━━━━━━━\n"
        "🧬 Biologiya · 2-kurs test banki\n"
        f"📚 Bazada <b>{total}</b> ta savol\n"
        f"{best_line}\n\n"
        "⏱ Har bir rejimda vaqt cheklangan. Vaqt tugasa, javob berilgan "
        "savollar bo'yicha natija chiqadi.\n\n"
        "⚡ <b>Tezkor</b> — 10 savol · 5 daqiqa\n"
        "🎯 <b>Standart</b> — 20 savol · 10 daqiqa\n"
        "🏆 <b>Marafon</b> — 50 savol · 25 daqiqa\n\n"
        "Rejimni tanlang:"
    )


def _question_text(
    question, index: int, total: int, deadline: float
) -> str:
    remaining = max(0, int(deadline - time.time()))
    options = "\n".join(
        f"<b>{letter})</b> {html.escape(str(question[field]))}"
        for letter, field in zip(OPTION_LETTERS, OPTION_FIELDS, strict=True)
    )
    return (
        f"🫀 <b>ANATOMIYA</b> · <b>{index + 1}/{total}</b>\n"
        f"⏳ <b>{_clock(remaining)}</b> qoldi · "
        f"{progress_bar(index, total, 10)}\n"
        "━━━━━━━━━━━━━━\n\n"
        f"❓ <b>Savol {index + 1}.</b> "
        f"{html.escape(str(question['question_text']))}\n\n"
        f"{options}\n\n"
        "Javobni tanlang 👇"
    )


def _result_reaction(percent: int) -> str:
    if percent >= 90:
        return "🏆"
    if percent >= 70:
        return "👏"
    if percent >= 50:
        return "👍"
    return "💪"


def _result_text(
    *,
    mode: int,
    correct: int,
    total: int,
    percent: int,
    best: int,
    is_record: bool,
    xp_amount: int,
    timed_out: bool,
    elapsed: int,
) -> str:
    if percent >= 90:
        message = "Ajoyib natija! 🎉 Mavzuni juda yaxshi o'zlashtirgansiz."
    elif percent >= 70:
        message = "Yaxshi natija! 👏 Yana bir oz mashq bilan mukammal bo'ladi."
    elif percent >= 50:
        message = "Yaxshi harakat! 📈 Xato mavzularni darslarda takrorlang."
    else:
        message = "Mashq qilishda davom eting. 💪 Har bir urinish kuchliroq qiladi."

    if is_record:
        best_line = "🎉 <b>Yangi rekord!</b> Bu sizning eng yaxshi natijangiz."
    elif best > 0:
        best_line = f"🏆 Eng yaxshi natijangiz: <b>{best}%</b>"
    else:
        best_line = "🏆 Bu bo'limdagi birinchi natijangiz."

    lines = [
        "⏰ <b>VAQT TUGADI</b>" if timed_out else "🏁 <b>TEST YAKUNLANDI</b>",
        "",
        f"🫀 <b>ANATOMIYA</b> · {mode} savol",
        f"✅ To'g'ri javoblar: <b>{correct}/{total}</b>",
        f"📊 Natija: <b>{percent}%</b>",
        progress_bar(percent, 100, 10),
        f"⏱ Sarflandi: <b>{_clock(elapsed)}</b> / "
        f"{_clock(ANATOMY_MODES[mode])}",
        best_line,
        f"⭐ Mukofot: <b>+{xp_amount} XP</b>",
        "",
        message,
        (
            "🔍 Xato javoblar tahlili alohida xabarda yuborildi."
            if correct < total
            else "🎯 Xatolar yo'q — barcha javoblar to'g'ri!"
        ),
        "",
        "📅 Natija kunlik rejaga qo'shildi.",
    ]
    if timed_out and total < mode:
        lines.insert(
            6,
            f"ℹ️ Vaqt tugagani uchun javob berilgan <b>{total}</b> ta savol "
            "baholandi.",
        )
    return "\n".join(lines)


def _review_text(wrong_answers: list[tuple]) -> str:
    lines = ["🔍 <b>Xatolar tahlili</b>", ""]
    for number, (question, selected) in enumerate(
        wrong_answers[:REVIEW_LIMIT], 1
    ):
        correct = int(question["correct_option"])
        lines.append(
            f"{number}. <b>{html.escape(_short(question['question_text'], 150))}</b>"
        )
        lines.append(
            "❌ Siz tanladingiz: "
            f"<b>{OPTION_LETTERS[selected]}) "
            f"{html.escape(_short(question[OPTION_FIELDS[selected]], 90))}</b>"
        )
        lines.append(
            "✅ To'g'ri javob: "
            f"<b>{OPTION_LETTERS[correct]}) "
            f"{html.escape(_short(question[OPTION_FIELDS[correct]], 90))}</b>"
        )
        lines.append("")
    remaining = len(wrong_answers) - REVIEW_LIMIT
    if remaining > 0:
        lines.append(f"… yana <b>{remaining}</b> ta xato bor.")
        lines.append("")
    lines.append("Mavzularni darslarda takrorlab, yana urinib ko'ring.")
    return "\n".join(lines)


async def _edit_message(
    bot, chat_id: int, message_id: int, text: str, markup
) -> int:
    """Xabarni tahrirlaydi; iloji bo'lmasa yangisini yuboradi."""
    try:
        result = await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
        )
    except TelegramBadRequest as exc:
        if is_not_modified_error(exc):
            return message_id
        sent = await bot.send_message(chat_id, text, reply_markup=markup)
        return int(sent.message_id)
    if isinstance(result, Message):
        return int(result.message_id)
    return message_id


async def _finish(
    bot,
    user_id: int,
    data: dict,
    *,
    timed_out: bool,
) -> None:
    question_ids = [int(item) for item in data.get("question_ids", [])]
    answers: list[dict[str, int]] = list(data.get("answers", []))
    correct_total = int(data.get("correct", 0))
    mode = int(data["mode"])
    chat_id = int(data["chat_id"])
    message_id = int(data["message_id"])
    started_at = float(data.get("started_at", time.time()))
    elapsed = min(int(time.time() - started_at), ANATOMY_MODES[mode])

    await _drop_session(user_id)

    total = len(answers) if timed_out else len(question_ids)
    if total <= 0:
        await _edit_message(
            bot,
            chat_id,
            message_id,
            "⏰ <b>Vaqt tugadi</b>\n\n"
            "Birorta savolga javob berishga ulgurmadingiz. "
            "Natija saqlanmadi.\n\n"
            "Keyingi safar tezroq boshlang! 🚀",
            get_anatomy_result_keyboard(),
        )
        return

    previous_best = await get_subject_best_score(user_id, ANATOMY_SUBJECT_ID)
    percent = await save_quiz_result(
        user_id=user_id,
        subject_id=ANATOMY_SUBJECT_ID,
        total_questions=total,
        correct_answers=correct_total,
    )
    best = max(previous_best or 0, percent)
    is_record = percent > (previous_best or 0)

    xp_amount = XP_QUIZ_BASE + correct_total * XP_QUIZ_PER_CORRECT
    if not timed_out and correct_total == total:
        xp_amount += XP_PERFECT_BONUS

    goal_done = await increment_goal(user_id, quizzes=1)
    reward_result = await reward(user_id, xp_amount, "anatomy")
    if goal_done:
        reward_result = combine_rewards(
            reward_result,
            await reward(
                user_id,
                XP_GOAL_BONUS,
                "goal",
                once_key=f"goal:{local_today()}",
            ),
        )

    await _edit_message(
        bot,
        chat_id,
        message_id,
        _result_text(
            mode=mode,
            correct=correct_total,
            total=total,
            percent=percent,
            best=best,
            is_record=is_record,
            xp_amount=xp_amount,
            timed_out=timed_out,
            elapsed=elapsed,
        ),
        get_anatomy_result_keyboard(),
    )

    notice = reward_notice(reward_result)
    if notice:
        await bot.send_message(chat_id, notice)

    question_map = await get_anatomy_questions_by_ids(question_ids)
    wrong_answers = [
        (question_map[item["question_id"]], item["selected"])
        for item in answers
        if item["question_id"] in question_map
        and item["selected"] != int(question_map[item["question_id"]]["correct_option"])
    ]
    if wrong_answers:
        await bot.send_message(chat_id, _review_text(wrong_answers))

    logger.info(
        "Anatomiya yakunlandi: user=%s, rejim=%s, natija=%s/%s, timeout=%s",
        user_id,
        mode,
        correct_total,
        total,
        timed_out,
    )


async def _timeout_task(bot, user_id: int) -> None:
    me = asyncio.current_task()
    try:
        while True:
            data = await _load_session(user_id)
            if data is None:
                return
            delay = float(data["deadline"]) - time.time()
            if delay > 0:
                await asyncio.sleep(delay)
                continue
            async with _lock_for(user_id):
                data = await _load_session(user_id)
                if data is None:
                    return
                if float(data["deadline"]) > time.time():
                    continue
                await _finish(bot, user_id, data, timed_out=True)
            return
    finally:
        if _timers.get(user_id) is me:
            _timers.pop(user_id, None)


@router.callback_query(F.data == "anatomy:menu")
async def show_menu(callback: CallbackQuery, state: FSMContext) -> None:
    user = await require_user_callback(callback)
    if user is None:
        return

    user_id = int(user["telegram_id"])
    await state.clear()
    await _drop_session(user_id)

    total = await count_anatomy_questions()
    best = await get_subject_best_score(user_id, ANATOMY_SUBJECT_ID)
    text = _menu_text(total, best)
    markup = get_anatomy_menu_keyboard()

    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if ANATOMY_BANNER.exists():
        try:
            await message.answer_photo(
                photo=FSInputFile(ANATOMY_BANNER),
                caption=text,
                reply_markup=markup,
            )
            await callback.answer()
            return
        except TelegramBadRequest:
            logger.warning("Anatomiya bannerini yuborib bo'lmadi.")

    await message.answer(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("anatomy:start:"))
async def start_test(callback: CallbackQuery, state: FSMContext) -> None:
    user = await require_user_callback(callback)
    if user is None or callback.data is None:
        return

    try:
        mode = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer("Rejim topilmadi.", show_alert=True)
        return

    seconds = ANATOMY_MODES.get(mode)
    if seconds is None:
        await callback.answer("Rejim topilmadi.", show_alert=True)
        return

    questions = await get_anatomy_questions(mode)
    if len(questions) < mode:
        await callback.answer(
            "Savollar banki yetarli emas. Keyinroq urinib ko'ring.",
            show_alert=True,
        )
        return

    message = callback.message
    if not isinstance(message, Message):
        return

    now = time.time()
    deadline = now + seconds
    first = questions[0]
    text = _question_text(first, 0, len(questions), deadline)
    markup = get_anatomy_options_keyboard(int(first["id"]))

    if message.photo:
        try:
            await message.delete()
        except TelegramBadRequest:
            pass
        sent = await message.answer(text, reply_markup=markup)
        chat_id = int(message.chat.id)
        message_id = (
            int(sent.message_id)
            if isinstance(sent, Message)
            else int(message.message_id)
        )
    else:
        edited = await message.edit_text(text, reply_markup=markup)
        sent = edited if isinstance(edited, Message) else message
        chat_id = int(sent.chat.id)
        message_id = int(sent.message_id)

    user_id = int(user["telegram_id"])
    await state.clear()
    await _store_session(
        user_id,
        {
            "question_ids": [int(question["id"]) for question in questions],
            "index": 0,
            "correct": 0,
            "answers": [],
            "current_id": int(first["id"]),
            "deadline": deadline,
            "started_at": now,
            "mode": mode,
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )
    _start_timer(callback.bot, user_id)

    await react(sent if isinstance(sent, Message) else message, "🫀")
    await callback.answer(
        f"⏱ {ANATOMY_MODE_LABELS[mode]} boshlandi. Omad! 🍀"
    )


@router.callback_query(F.data.startswith("anatomy:answer:"))
async def answer_question(callback: CallbackQuery) -> None:
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

    user_id = int(user["telegram_id"])
    async with _lock_for(user_id):
        data = await _load_session(user_id)
        if data is None:
            await callback.answer(STALE_TEXT, show_alert=True)
            return

        timer = _timers.get(user_id)
        if timer is None or timer.done():
            _start_timer(callback.bot, user_id)

        if time.time() >= float(data["deadline"]):
            await _finish(callback.bot, user_id, data, timed_out=True)
            await callback.answer("⏰ Vaqt tugadi!", show_alert=True)
            return

        if int(data.get("current_id", 0)) != question_id:
            await callback.answer(
                "Bu savol allaqachon yakunlangan.", show_alert=True
            )
            return

        question = await get_anatomy_question(question_id)
        if question is None:
            await _drop_session(user_id)
            await callback.answer("Savol topilmadi.", show_alert=True)
            return

        question_ids = [int(item) for item in data["question_ids"]]
        answers: list[dict[str, int]] = list(data["answers"])
        index = int(data["index"])
        correct_total = int(data["correct"])

        is_correct = option == int(question["correct_option"])
        if is_correct:
            correct_total += 1
        answers.append({"question_id": question_id, "selected": option})
        await react(callback.message, "✅" if is_correct else "❌")

        next_index = index + 1
        if next_index >= len(question_ids):
            data.update(correct=correct_total, answers=answers)
            await _finish(callback.bot, user_id, data, timed_out=False)
            await callback.answer("Test yakunlandi! 🏁")
            return

        next_question = await get_anatomy_question(question_ids[next_index])
        if next_question is None:
            await _drop_session(user_id)
            await callback.answer("Keyingi savol topilmadi.", show_alert=True)
            return

        data.update(
            index=next_index,
            correct=correct_total,
            answers=answers,
            current_id=int(next_question["id"]),
        )
        await _store_session(user_id, data)
        message_id = await _edit_message(
            callback.bot,
            int(data["chat_id"]),
            int(data["message_id"]),
            _question_text(
                next_question,
                next_index,
                len(question_ids),
                float(data["deadline"]),
            ),
            get_anatomy_options_keyboard(int(next_question["id"])),
        )
        if message_id != int(data["message_id"]):
            data["message_id"] = message_id
            await _store_session(user_id, data)

    await callback.answer("✅ Javob qabul qilindi")
