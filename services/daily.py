"""Kunlik sovg'a va haftalik missiyalar mantiqi."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from database.daily import (
    current_week_key,
    get_claimed_missions,
    get_weekly_activity,
)
from time_utils import calculate_streak

GIFT_MIN_XP = 5
GIFT_MAX_XP = 25


@dataclass(frozen=True, slots=True)
class Mission:
    code: str
    emoji: str
    title: str
    stat: str
    target: int
    reward_xp: int


MISSIONS: tuple[Mission, ...] = (
    Mission("lessons_3", "📚", "3 ta darsni tugatish", "lessons", 3, 30),
    Mission("quizzes_2", "📝", "2 ta test yechish", "quizzes", 2, 25),
    Mission("ai_3", "🤖", "3 ta AI savol berish", "ai_messages", 3, 20),
)

MISSION_MAP = {item.code: item for item in MISSIONS}


@dataclass(frozen=True, slots=True)
class MissionState:
    mission: Mission
    progress: int
    done: bool
    claimed: bool


def gift_amount() -> int:
    """Kunlik sovg'a uchun tasodifiy XP miqdori."""
    return secrets.randbelow(GIFT_MAX_XP - GIFT_MIN_XP + 1) + GIFT_MIN_XP


def mission_once_key(code: str) -> str:
    return f"mission:{code}:{current_week_key()}"


def daily_streak(days: set[str]) -> int:
    return calculate_streak(days)


async def get_mission_states(user_id: int) -> list[MissionState]:
    stats = await get_weekly_activity(user_id)
    claimed = await get_claimed_missions(user_id)
    states: list[MissionState] = []
    for mission in MISSIONS:
        progress = min(int(stats.get(mission.stat, 0)), mission.target)
        states.append(
            MissionState(
                mission=mission,
                progress=progress,
                done=progress >= mission.target,
                claimed=mission.code in claimed,
            )
        )
    return states
