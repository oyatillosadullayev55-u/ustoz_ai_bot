"""Dars kartochkalari uchun rasm fayllarini boshqarish."""

from __future__ import annotations

from pathlib import Path

from aiogram.types import FSInputFile

from config import BASE_DIR

LESSON_IMAGES_DIR = BASE_DIR / "assets" / "lesson_images"
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")

_file_ids: dict[int, str] = {}


def get_lesson_image_path(lesson_id: int) -> Path | None:
    for suffix in IMAGE_SUFFIXES:
        path = LESSON_IMAGES_DIR / f"lesson_{lesson_id}{suffix}"
        if path.is_file():
            return path
    return None


def get_lesson_photo(lesson_id: int) -> FSInputFile | str | None:
    cached_file_id = _file_ids.get(lesson_id)
    if cached_file_id:
        return cached_file_id

    path = get_lesson_image_path(lesson_id)
    if path is None:
        return None
    return FSInputFile(path)


def remember_lesson_file_id(lesson_id: int, file_id: str) -> None:
    if file_id:
        _file_ids[lesson_id] = file_id
