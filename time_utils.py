"""Vaqt va sana bilan ishlash uchun yordamchi funksiyalar."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone

LOCAL_TZ = timezone(timedelta(hours=5))


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


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
        parsed = parsed.replace(tzinfo=UTC)
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


def seconds_until_local_time(
    hour: int, minute: int = 0, *, now: datetime | None = None
) -> float:
    """Mahalliy vaqt bo'yicha keyingi belgilangan vaqtgacha soniyalar."""
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("Vaqt qiymati noto'g'ri.")

    current = now or local_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=LOCAL_TZ)
    current = current.astimezone(LOCAL_TZ)

    target = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= current:
        target += timedelta(days=1)
    return (target - current).total_seconds()
