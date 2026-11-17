"""Turk tili gaplari uchun ovozli (OGG/Opus) fayllarni yaratadi.

Bu skript faqat ishlab chiqish muhitida ishlatiladi: natijadagi fayllar
`assets/turkish_audio/` papkasiga yoziladi va bot bilan birga tarqatiladi.
Serverda edge-tts yoki ffmpeg talab qilinmaydi.

Ishlatish:
    .venv/Scripts/python.exe scripts/generate_turkish_audio.py
    .venv/Scripts/python.exe scripts/generate_turkish_audio.py --force
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "content" / "turkish_courses.json"
OUTPUT_DIR = BASE_DIR / "assets" / "turkish_audio"

VOICE = "tr-TR-EmelNeural"
RATE = "-8%"


def audio_filename(lesson_id: int, phrase_index: int) -> str:
    return f"lesson_{lesson_id}_{phrase_index}.ogg"


def convert_to_ogg(mp3_path: Path, ogg_path: Path) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg,
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(mp3_path),
        "-c:a",
        "libopus",
        "-b:a",
        "48k",
        "-ar",
        "48000",
        "-ac",
        "1",
        str(ogg_path),
    ]
    subprocess.run(command, check=True)


async def synthesize(text: str, ogg_path: Path) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        mp3_path = Path(temp_dir) / "phrase.mp3"
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(str(mp3_path))
        convert_to_ogg(mp3_path, ogg_path)


async def generate(force: bool) -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    lessons = [
        lesson
        for subject in data.get("subjects", [])
        for lesson in subject.get("lessons", [])
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    for lesson in lessons:
        lesson_id = int(lesson["id"])
        for phrase_index, phrase in enumerate(lesson.get("phrases", []), start=1):
            target = OUTPUT_DIR / audio_filename(lesson_id, phrase_index)
            if target.exists() and not force:
                skipped += 1
                continue
            await synthesize(str(phrase["tr"]), target)
            created += 1
            print(f"[{created + skipped}] {target.name}: {phrase['tr']}")

    print(f"Tayyor: {created} yangi fayl, {skipped} mavjud o'tkazib yuborildi.")
    print(f"Papka: {OUTPUT_DIR}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Mavjud ovoz fayllarini ham qayta yaratish.",
    )
    args = parser.parse_args()
    return asyncio.run(generate(args.force))


if __name__ == "__main__":
    raise SystemExit(main())
