# Kod fayllari bo'yicha hujjatlar

Bu papkada UstozAI loyihasining **har bir kod fayli** uchun alohida markdown hujjat bor. Har bir hujjat faylning vazifasi, asosiy funksiyalari, ish oqimi va xavfsizlik jihatlarini tushuntiradi.

## Asosiy fayllar

| Fayl | Hujjat |
|---|---|
| `bot.py` | [bot.md](bot.md) |
| `config.py` | [config.md](config.md) |
| `time_utils.py` | [time_utils.md](time_utils.md) |
| `.env.example` | [env-example.md](env-example.md) |

## Ma'lumotlar bazasi

| Fayl | Hujjat |
|---|---|
| `database/__init__.py` | [database/index.md](database/index.md) |
| `database/db.py` | [database/db.md](database/db.md) |
| `database/seed.py` | [database/seed.md](database/seed.md) |
| `database/users.py` | [database/users.md](database/users.md) |
| `database/content.py` | [database/content.md](database/content.md) |
| `database/quizzes.py` | [database/quizzes.md](database/quizzes.md) |
| `database/progress.py` | [database/progress.md](database/progress.md) |
| `database/goals.py` | [database/goals.md](database/goals.md) |
| `database/chat.py` | [database/chat.md](database/chat.md) |
| `database/admin.py` | [database/admin.md](database/admin.md) |

## Handlerlar

| Fayl | Hujjat |
|---|---|
| `handlers/__init__.py` | [handlers/index.md](handlers/index.md) |
| `handlers/start.py` | [handlers/start.md](handlers/start.md) |
| `handlers/ai_tutor.py` | [handlers/ai_tutor.md](handlers/ai_tutor.md) |
| `handlers/lessons.py` | [handlers/lessons.md](handlers/lessons.md) |
| `handlers/quizzes.py` | [handlers/quizzes.md](handlers/quizzes.md) |
| `handlers/progress.py` | [handlers/progress.md](handlers/progress.md) |
| `handlers/daily_plan.py` | [handlers/daily_plan.md](handlers/daily_plan.md) |
| `handlers/settings.py` | [handlers/settings.md](handlers/settings.md) |
| `handlers/admin.py` | [handlers/admin.md](handlers/admin.md) |
| `handlers/common.py` | [handlers/common.md](handlers/common.md) |
| `handlers/menu.py` | [handlers/menu.md](handlers/menu.md) |

## Klaviaturalar

| Fayl | Hujjat |
|---|---|
| `keyboards/__init__.py` | [keyboards/index.md](keyboards/index.md) |
| `keyboards/main_menu.py` | [keyboards/main_menu.md](keyboards/main_menu.md) |
| `keyboards/inline_buttons.py` | [keyboards/inline_buttons.md](keyboards/inline_buttons.md) |

## Servislar

| Fayl | Hujjat |
|---|---|
| `services/__init__.py` | [services/index.md](services/index.md) |
| `services/ai_service.py` | [services/ai_service.md](services/ai_service.md) |
| `services/lesson_media.py` | [services/lesson_media.md](services/lesson_media.md) |
| `services/reminders.py` | [services/reminders.md](services/reminders.md) |

## Testlar va kontent

| Fayl | Hujjat |
|---|---|
| `tests/test_offline.py` | [tests/test_offline.md](tests/test_offline.md) |
| `tests/test_handlers_offline.py` | [tests/test_handlers_offline.md](tests/test_handlers_offline.md) |
| `content/seed_data.json` | [content/seed_data.md](content/seed_data.md) |

## Infratuzilma

| Fayl | Hujjat |
|---|---|
| `.github/workflows/ci.yml` | [infra/ci.md](infra/ci.md) |
| `pyproject.toml` | [infra/pyproject.md](infra/pyproject.md) |
| `requirements.txt`, `requirements-dev.txt` | [infra/requirements.md](infra/requirements.md) |
| `.run/UstozAI Bot.run.xml` | [infra/pycharm-run.md](infra/pycharm-run.md) |

## Boshqa hujjatlar

- [Loyiha arxitekturasi](../LOYIHA.md)
- [Foydalanuvchi va admin qo'llanmasi](../FOYDALANISH.md)
- [README](../../README.md)

## Yangilangan imkoniyatlar

- Test yakunida xato javoblar tahlili (tanlangan variant, to'g'ri variant, izoh).
- `/qidiruv` va `/search` orqali darslardan matnli qidiruv.
- Har kuni belgilangan vaqtda kunlik reja eslatmasi (UTC+5).
- Faollik statistikasida AI suhbat kunlari ham hisobga olinadi.
- Ruff lint va GitHub Actions CI.
