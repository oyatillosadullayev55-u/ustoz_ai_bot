"""Gamifikatsiya: XP, darajalar, yutuqlar va haftalik reyting."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from database.gamification import (
    award_xp,
    get_achievement_codes,
    get_achievement_stats,
    get_total_xp,
    get_weekly_leaderboard,
    get_weekly_xp,
    unlock_achievements,
)
from database.progress import get_activity_stats

XP_LESSON = 20
XP_QUIZ_BASE = 5
XP_QUIZ_PER_CORRECT = 2
XP_PERFECT_BONUS = 10
XP_GOAL_BONUS = 15
XP_ACHIEVEMENT = 15
XP_AI = 1


@dataclass(frozen=True, slots=True)
class Rank:
    emoji: str
    name: str
    min_xp: int


RANKS: tuple[Rank, ...] = (
    Rank("🌱", "Yangi boshlovchi", 0),
    Rank("📗", "O'quvchi", 100),
    Rank("📘", "Bilimdon", 300),
    Rank("🎓", "Tajribali", 700),
    Rank("🏅", "Ustoz", 1500),
    Rank("👑", "Afsona", 3000),
)


def rank_for(xp: int) -> Rank:
    rank = RANKS[0]
    for item in RANKS:
        if xp >= item.min_xp:
            rank = item
    return rank


def next_rank(xp: int) -> Rank | None:
    for item in RANKS:
        if xp < item.min_xp:
            return item
    return None


@dataclass(frozen=True, slots=True)
class Achievement:
    code: str
    emoji: str
    title: str
    description: str
    check: Callable[[dict[str, int]], bool] = field(repr=False, compare=False)


ACHIEVEMENTS: tuple[Achievement, ...] = (
    Achievement(
        "first_lesson", "📖", "Birinchi qadam",
        "Birinchi darsni tugatdingiz", lambda s: s["lessons"] >= 1,
    ),
    Achievement(
        "five_lessons", "📚", "Izlanuvchi",
        "5 ta darsni tugatdingiz", lambda s: s["lessons"] >= 5,
    ),
    Achievement(
        "fifteen_lessons", "🎓", "Bilimdon",
        "15 ta darsni tugatdingiz", lambda s: s["lessons"] >= 15,
    ),
    Achievement(
        "all_lessons", "🏆", "Marafon",
        "Barcha 35 ta darsni tugatdingiz", lambda s: s["lessons"] >= 35,
    ),
    Achievement(
        "first_quiz", "📝", "Birinchi sinov",
        "Birinchi testni yakunladingiz", lambda s: s["quizzes"] >= 1,
    ),
    Achievement(
        "ten_quizzes", "🧠", "Test ustasi",
        "10 ta test yechdingiz", lambda s: s["quizzes"] >= 10,
    ),
    Achievement(
        "perfect_quiz", "🎯", "Mukammal natija",
        "Testda 100% natija qayd etdingiz", lambda s: s["perfect"] >= 1,
    ),
    Achievement(
        "streak_3", "🔥", "Uch kun",
        "3 kun ketma-ket o'qidingiz", lambda s: s["streak"] >= 3,
    ),
    Achievement(
        "streak_7", "⚡", "Bir hafta",
        "7 kun ketma-ket o'qidingiz", lambda s: s["streak"] >= 7,
    ),
    Achievement(
        "favorite_5", "⭐", "Kolleksioner",
        "5 ta darsni sevimlilarga qo'shdingiz", lambda s: s["favorites"] >= 5,
    ),
    Achievement(
        "ai_10", "🤖", "AI hamkor",
        "AI Ustozga 10 ta savol berdingiz", lambda s: s["ai_messages"] >= 10,
    ),
    Achievement(
        "goal_5", "🎯", "Maqsadli",
        "5 kun kunlik maqsadni bajardingiz", lambda s: s["goal_days"] >= 5,
    ),
)

ACHIEVEMENT_MAP = {item.code: item for item in ACHIEVEMENTS}


@dataclass(slots=True)
class RewardResult:
    xp: int
    xp_gained: int
    rank: Rank
    rank_up: bool
    achievements: list[Achievement]


async def reward(
    user_id: int,
    amount: int = 0,
    reason: str = "activity",
    *,
    once_key: str | None = None,
) -> RewardResult:
    """XP qo'shadi, yutuqlarni tekshiradi va natijani qaytaradi."""
    old_xp = await get_total_xp(user_id)
    if amount > 0:
        await award_xp(user_id, amount, reason, once_key=once_key)

    stats = await get_achievement_stats(user_id)
    stats["streak"] = int((await get_activity_stats(user_id))["streak"])

    unlocked = await get_achievement_codes(user_id)
    candidates = [
        item
        for item in ACHIEVEMENTS
        if item.code not in unlocked and item.check(stats)
    ]
    inserted = set(await unlock_achievements(user_id, [item.code for item in candidates]))
    if inserted:
        await award_xp(user_id, XP_ACHIEVEMENT * len(inserted), "achievement")

    new_xp = await get_total_xp(user_id)
    new_rank = rank_for(new_xp)
    return RewardResult(
        xp=new_xp,
        xp_gained=max(new_xp - old_xp, 0),
        rank=new_rank,
        rank_up=new_rank.min_xp > rank_for(old_xp).min_xp,
        achievements=[item for item in candidates if item.code in inserted],
    )


def combine_rewards(*results: RewardResult) -> RewardResult:
    """Bir amaldagi bir nechta mukofot natijasini birlashtiradi."""
    if not results:
        raise ValueError("Kamida bitta natija kerak.")

    seen: set[str] = set()
    achievements: list[Achievement] = []
    for result in results:
        for item in result.achievements:
            if item.code not in seen:
                seen.add(item.code)
                achievements.append(item)

    last = results[-1]
    return RewardResult(
        xp=last.xp,
        xp_gained=sum(result.xp_gained for result in results),
        rank=last.rank,
        rank_up=any(result.rank_up for result in results),
        achievements=achievements,
    )


async def get_profile(user_id: int) -> dict[str, object]:
    xp = await get_total_xp(user_id)
    return {
        "xp": xp,
        "rank": rank_for(xp),
        "next_rank": next_rank(xp),
        "weekly_xp": await get_weekly_xp(user_id),
        "achievements": len(await get_achievement_codes(user_id)),
        "total_achievements": len(ACHIEVEMENTS),
    }


async def get_achievements_with_state(
    user_id: int,
) -> list[tuple[Achievement, bool]]:
    unlocked = await get_achievement_codes(user_id)
    return [(item, item.code in unlocked) for item in ACHIEVEMENTS]


async def get_leaderboard(user_id: int, limit: int = 10) -> dict[str, object]:
    return await get_weekly_leaderboard(user_id, limit=limit)
