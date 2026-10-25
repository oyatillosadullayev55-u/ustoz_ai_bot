# `config.py` — sozlamalar

**Yo'l:** [`config.py`](../../config.py)
**Vazifasi:** `.env` faylidan xavfsiz qiymatlarni o'qish, tekshirish va `Settings` obyektiga yig'ish.

## Tuzilma

- `BASE_DIR` — loyiha ildizi; `DATABASE_PATH` va `content/seed_data.json` shunga nisbatan hisoblanadi.
- `load_dotenv(ENV_FILE)` — `.env` faylini jarayon muhitiga yuklaydi. `.env` GitHub'ga yuborilmaydi.
- `ConfigError` — noto'g'ri yoki yetishmayotgan sozlama uchun xato.
- `Settings` — `frozen=True, slots=True` dataclass; barcha sozlamalar bitta joyda.

## `Settings` maydonlari

| Maydon | Manba | Tekshiruv |
|---|---|---|
| `bot_token` | `BOT_TOKEN` | Bo'sh emas va `:` belgisi bor |
| `admin_ids` | `ADMIN_IDS` | Vergul/nuqtali vergul bilan ajratilgan musbat ID'lar |
| `database_path` | `DATABASE_PATH` | Nisbiy yo'l `BASE_DIR` ga ulanadi |
| `log_level` | `LOG_LEVEL` | DEBUG…CRITICAL |
| `default_language` | `DEFAULT_LANGUAGE` | `uz`, `ru`, `en` |
| `ai_enabled` | `AI_ENABLED` | `true/false`, `1/0`, `yes/no`, `on/off` |
| `ai_api_key` | `AI_API_KEY` | Bo'sh bo'lishi mumkin |
| `ai_base_url` | `AI_BASE_URL` | `http://` yoki `https://` |
| `ai_model` | `AI_MODEL` | Standart `gpt-4o-mini` |
| `ai_timeout` | `AI_TIMEOUT` | 5–120 soniya |
| `ai_daily_limit` | `AI_DAILY_LIMIT` | 1–500 savol |
| `ai_min_interval` | `AI_MIN_INTERVAL` | 0–60 soniya |
| `ai_max_tokens` | `AI_MAX_TOKENS` | 100–4000 |
| `ai_history_limit` | `AI_HISTORY_LIMIT` | 0–20 xabar |
| `daily_reminders_enabled` | `DAILY_REMINDERS_ENABLED` | `true/false` |
| `daily_reminder_hour` | `DAILY_REMINDER_HOUR` | 0–23 (UTC+5) |

## Yordamchi metodlar

- `is_admin(telegram_id)` — foydalanuvchi admin ro'yxatida borligini tekshiradi.
- `ai_configured` — AI yoqilgan, kalit, model va manzil to'liq bo'lsa `True`.
- `get_settings()` — `lru_cache` bilan bitta nusxa qaytaradi. Testlarda qiymatlarni almashtirish uchun `get_settings.cache_clear()` ishlatiladi.

## Xavfsizlik

- Maxfiy token, AI kaliti va admin ID'lar faqat muhit o'zgaruvchilaridan o'qiladi.
- Xato xabarlarida token qiymati ko'rsatilmaydi.
- `.env.example` faqat namuna qiymatlarni saqlaydi.
