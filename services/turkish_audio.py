"""Turk tili talaffuz mashqlari uchun ovozli fayllar."""

from __future__ import annotations

from pathlib import Path

from aiogram.types import FSInputFile

from config import BASE_DIR

TURKISH_AUDIO_DIR = BASE_DIR / "assets" / "turkish_audio"

_file_ids: dict[tuple[int, int], str] = {}


def audio_filename(lesson_id: int, phrase_index: int) -> str:
    return f"lesson_{lesson_id}_{phrase_index}.ogg"


def get_audio_path(lesson_id: int, phrase_index: int) -> Path | None:
    path = TURKISH_AUDIO_DIR / audio_filename(lesson_id, phrase_index)
    if path.is_file():
        return path
    return None


def get_audio_source(lesson_id: int, phrase_index: int) -> FSInputFile | str | None:
    """Avval Telegram file_id, keyin lokal faylni qaytaradi."""
    cached = _file_ids.get((lesson_id, phrase_index))
    if cached:
        return cached

    path = get_audio_path(lesson_id, phrase_index)
    if path is None:
        return None
    return FSInputFile(path)


def remember_audio_file_id(lesson_id: int, phrase_index: int, file_id: str) -> None:
    if file_id:
        _file_ids[(lesson_id, phrase_index)] = file_id


def missing_audio_files(lesson_ids: list[int], phrase_count: int) -> list[str]:
    """Tekshiruvlar uchun: yetishmayotgan ovoz fayllari nomlari."""
    missing: list[str] = []
    for lesson_id in lesson_ids:
        for phrase_index in range(1, phrase_count + 1):
            if get_audio_path(lesson_id, phrase_index) is None:
                missing.append(audio_filename(lesson_id, phrase_index))
    return missing
