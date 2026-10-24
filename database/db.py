"""SQLite ulanishini boshqarish va jadvallarni yaratish."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite

from config import get_settings

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL CHECK (length(full_name) BETWEEN 1 AND 100),
    username TEXT,
    language TEXT NOT NULL DEFAULT 'uz'
        CHECK (language IN ('uz', 'ru', 'en')),
    level TEXT NOT NULL DEFAULT 'beginner'
        CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    notifications_enabled INTEGER NOT NULL DEFAULT 1
        CHECK (notifications_enabled IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    emoji TEXT NOT NULL DEFAULT '📚',
    description TEXT NOT NULL DEFAULT '',
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option INTEGER NOT NULL CHECK (correct_option BETWEEN 0 AND 3),
    explanation TEXT NOT NULL DEFAULT '',
    order_index INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    total_questions INTEGER NOT NULL CHECK (total_questions > 0),
    correct_answers INTEGER NOT NULL CHECK (correct_answers >= 0),
    score_percent INTEGER NOT NULL CHECK (score_percent BETWEEN 0 AND 100),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS study_progress (
    user_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'started'
        CHECK (status IN ('started', 'completed')),
    completed_at TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    goal_date TEXT NOT NULL,
    target_lessons INTEGER NOT NULL DEFAULT 1
        CHECK (target_lessons BETWEEN 0 AND 20),
    target_quizzes INTEGER NOT NULL DEFAULT 1
        CHECK (target_quizzes BETWEEN 0 AND 20),
    completed_lessons INTEGER NOT NULL DEFAULT 0 CHECK (completed_lessons >= 0),
    completed_quizzes INTEGER NOT NULL DEFAULT 0 CHECK (completed_quizzes >= 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (user_id, goal_date)
);

CREATE INDEX IF NOT EXISTS idx_lessons_subject
    ON lessons (subject_id, order_index);
CREATE INDEX IF NOT EXISTS idx_questions_lesson
    ON questions (lesson_id, order_index);
CREATE INDEX IF NOT EXISTS idx_quiz_results_user
    ON quiz_results (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_study_progress_user
    ON study_progress (user_id, status);
CREATE INDEX IF NOT EXISTS idx_chat_history_user
    ON chat_history (user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_daily_goals_user_date
    ON daily_goals (user_id, goal_date);
"""


@asynccontextmanager
async def get_connection() -> AsyncIterator[aiosqlite.Connection]:
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("PRAGMA busy_timeout = 5000")
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def init_db() -> None:
    """Jadvallarni yaratadi, kontentni yuklaydi va mavjud ma'lumotni saqlaydi."""
    async with get_connection() as db:
        await db.execute("PRAGMA journal_mode = WAL")
        await db.executescript(SCHEMA_SQL)
        await db.commit()

    from database.seed import seed_content

    await seed_content()
    logger.info("Ma'lumotlar bazasi tayyor: %s", get_settings().database_path)
