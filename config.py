"""Bot konfiguratsiyasi. Maxfiy qiymatlar faqat .env faylidan o'qiladi."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

SUPPORTED_LANGUAGES = frozenset({"uz", "ru", "en"})
LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


class ConfigError(RuntimeError):
    """Konfiguratsiya noto'g'ri bo'lganda ko'tariladigan xato."""


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    admin_ids: frozenset[int]
    database_path: Path
    log_level: str
    default_language: str
    ai_enabled: bool
    ai_api_key: str
    ai_base_url: str
    ai_model: str
    ai_timeout: int
    ai_daily_limit: int
    ai_min_interval: int
    ai_max_tokens: int
    ai_history_limit: int
    daily_reminders_enabled: bool
    daily_reminder_hour: int

    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self.admin_ids

    @property
    def ai_configured(self) -> bool:
        return (
            self.ai_enabled
            and bool(self.ai_api_key)
            and bool(self.ai_model)
            and bool(self.ai_base_url)
        )


def _parse_admin_ids(raw: str) -> frozenset[int]:
    if not raw.strip():
        return frozenset()

    admin_ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            admin_id = int(part)
        except ValueError:
            raise ConfigError(
                "ADMIN_IDS faqat raqamlardan iborat bo'lishi kerak "
                "(masalan: ADMIN_IDS=123456789)."
            ) from None
        if admin_id <= 0:
            raise ConfigError("ADMIN_IDS ichida noto'g'ri Telegram ID bor.")
        admin_ids.add(admin_id)

    return frozenset(admin_ids)


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"{name} qiymati true yoki false bo'lishi kerak.")


def _read_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, str(default)).strip() or str(default)
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(
            f"{name} butun son bo'lishi kerak (masalan: {default})."
        ) from None
    if not minimum <= value <= maximum:
        raise ConfigError(
            f"{name} {minimum} va {maximum} orasida bo'lishi kerak."
        )
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise ConfigError(
            "BOT_TOKEN topilmadi. .env.example faylidan .env nusxa oling va "
            "BotFather bergan tokenni BOT_TOKEN= qatoriga yozing."
        )
    if ":" not in bot_token or bot_token.startswith(":"):
        raise ConfigError(
            "BOT_TOKEN formati noto'g'ri. BotFather bergan tokenni to'liq ko'chiring."
        )

    language = os.getenv("DEFAULT_LANGUAGE", "uz").strip().lower() or "uz"
    if language not in SUPPORTED_LANGUAGES:
        raise ConfigError(
            "DEFAULT_LANGUAGE faqat uz, ru yoki en bo'lishi mumkin."
        )

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO"
    if log_level not in LOG_LEVELS:
        raise ConfigError(
            "LOG_LEVEL qiymatlari: DEBUG, INFO, WARNING, ERROR, CRITICAL."
        )

    database_raw = os.getenv("DATABASE_PATH", "ustoz_ai.db").strip() or "ustoz_ai.db"
    database_path = Path(database_raw).expanduser()
    if not database_path.is_absolute():
        database_path = BASE_DIR / database_path

    ai_base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    if not ai_base_url.startswith(("https://", "http://")):
        raise ConfigError(
            "AI_BASE_URL http:// yoki https:// bilan boshlanishi kerak."
        )

    return Settings(
        bot_token=bot_token,
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        database_path=database_path,
        log_level=log_level,
        default_language=language,
        ai_enabled=_read_bool("AI_ENABLED", False),
        ai_api_key=os.getenv("AI_API_KEY", "").strip(),
        ai_base_url=ai_base_url,
        ai_model=os.getenv("AI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        ai_timeout=_read_int("AI_TIMEOUT", 30, 5, 120),
        ai_daily_limit=_read_int("AI_DAILY_LIMIT", 30, 1, 500),
        ai_min_interval=_read_int("AI_MIN_INTERVAL", 3, 0, 60),
        ai_max_tokens=_read_int("AI_MAX_TOKENS", 700, 100, 4000),
        ai_history_limit=_read_int("AI_HISTORY_LIMIT", 8, 0, 20),
        daily_reminders_enabled=_read_bool("DAILY_REMINDERS_ENABLED", True),
        daily_reminder_hour=_read_int("DAILY_REMINDER_HOUR", 19, 0, 23),
    )
