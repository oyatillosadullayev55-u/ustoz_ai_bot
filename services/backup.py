"""Baza zaxirasini olish va CSV eksport qilish."""

from __future__ import annotations

import asyncio
import contextlib
import csv
import os
import sqlite3
from pathlib import Path

from config import BASE_DIR, get_settings
from database.admin import get_export_rows
from time_utils import local_now

BACKUP_KEEP = 5

CSV_HEADERS = (
    "telegram_id",
    "full_name",
    "username",
    "level",
    "xp",
    "notifications_enabled",
    "created_at",
    "last_seen_at",
    "lessons_completed",
    "quizzes",
    "average_score",
    "best_score",
)


def _timestamp() -> str:
    return local_now().strftime("%Y%m%d_%H%M%S")


def _backup_dir() -> Path:
    """BACKUP_DIR berilmasa, loyiha ichidagi `backups` papkasi ishlatiladi."""
    raw = os.getenv("BACKUP_DIR", "").strip()
    path = Path(raw).expanduser() if raw else BASE_DIR / "backups"
    if not path.is_absolute():
        path = BASE_DIR / path
    path.mkdir(parents=True, exist_ok=True)
    return path


async def create_backup_copy() -> Path:
    """SQLite backup API orqali izchil nusxa yaratadi (WAL rejimida ham)."""
    settings = get_settings()
    target = _backup_dir() / f"ustoz_ai_{_timestamp()}.db"
    source_path = str(settings.database_path)

    def _copy() -> None:
        source = sqlite3.connect(source_path)
        try:
            destination = sqlite3.connect(target)
            try:
                source.backup(destination)
            finally:
                destination.close()
        finally:
            source.close()

    await asyncio.to_thread(_copy)
    return target


def cleanup_old_backups(keep: int = BACKUP_KEEP) -> None:
    """Eski baza nusxalarini o'chiradi, oxirgi `keep` tasini qoldiradi."""
    directory = _backup_dir()
    files = sorted(
        directory.glob("*.db"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for old in files[keep:]:
        with contextlib.suppress(OSError):
            old.unlink()


async def create_export_csv() -> tuple[Path, int]:
    """Foydalanuvchilar bo'yicha yig'ma CSV fayl yaratadi."""
    rows = await get_export_rows()
    path = _backup_dir() / f"foydalanuvchilar_{_timestamp()}.csv"

    def _write() -> None:
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
            for row in rows:
                writer.writerow([row[header] for header in CSV_HEADERS])

    await asyncio.to_thread(_write)
    return path, len(rows)
