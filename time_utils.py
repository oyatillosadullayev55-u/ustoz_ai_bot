"""Vaqt va sana bilan ishlash uchun yordamchi funksiyalar."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

LOCAL_TZ = timezone(timedelta(hours=5))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def local_now() -> datetime:
    return datetime.now(LOCAL_TZ)


def local_today() -> str:
    return local_now().date().isoformat()


def local_date_of(value: str | None) -> date | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(LOCAL_TZ).date()


def format_local_date(value: str | None, fmt: str = "%d.%m.%Y") -> str:
    day = local_date_of(value)
    return day.strftime(fmt) if day else "—"


def calculate_streak(days: set[str]) -> int:
    """Bugundan (yoki kechadan) boshlab ketma-ket faol kunlarni sanaydi."""
    if not days:
        return 0

    cursor = local_now().date()
    if cursor.isoformat() not in days:
        cursor -= timedelta(days=1)

    streak = 0
    while cursor.isoformat() in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
