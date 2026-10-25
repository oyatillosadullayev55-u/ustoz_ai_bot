# `bot.py` — kirish nuqtasi

**Yo'l:** [`bot.py`](../../bot.py)
**Vazifasi:** botni ishga tushirish, loggingni sozlash, routerlarni ulash va kunlik eslatma vazifasini boshqarish.

## Asosiy funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `setup_logging(level)` | Konsol va `logs/bot.log` uchun aylanadigan log sozlamalarini o'rnatadi (1 MB × 3 fayl). |
| `set_bot_commands(bot, settings)` | Telegramdagi buyruqlar menyusini o'rnatadi; adminlar uchun `/admin` qo'shadi. |
| `on_error(event)` | `ErrorEvent` orqali kutilmagan xatolarni logga yozadi va foydalanuvchiga xabar beradi. |
| `run_bot(settings)` | Bazani tayyorlaydi, `Bot` va `Dispatcher` yaratadi, routerlarni ulaydi, pollingni boshlaydi. |
| `main()` | `.env` sozlamalarini o'qiydi, loggingni yoqadi va `asyncio.run(run_bot(...))` chaqiradi. |

## Ishga tushish tartibi

1. `get_settings()` orqali `.env` tekshiriladi. `BOT_TOKEN` bo'lmasa dastur `ConfigError` bilan to'xtaydi.
2. Logging sozlanadi va AI holati haqida qisqa log yoziladi (kalitning o'zi hech qachon logga tushmaydi).
3. `init_db()` 8 ta jadvalni yaratadi va kontentni yuklaydi.
4. Routerlar tartib bilan ulanadi: `start → ai_tutor → lessons → quizzes → progress → daily_plan → settings → admin → menu`.
5. `DAILY_REMINDERS_ENABLED=true` bo'lsa `run_daily_reminders(bot)` fon vazifasi sifatida ishga tushadi.
6. `dispatcher.start_polling(bot)` Telegramdan yangilanishlarni qabul qiladi.
7. Dastur to'xtaganda eslatma vazifasi bekor qilinadi va bot sessiyasi yopiladi (`finally`).

## Muhim jihatlar

- Bot tokeni faqat `Settings` orqali ishlatiladi; kodda yoki logda saqlanmaydi.
- `menu` routeri eng oxirida turadi, shuning uchun u boshqa routerlar tanimagan xabarlar uchun zaxira bo'ladi.
- `/qidiruv` buyrug'i global buyruqlar ro'yxatiga qo'shilgan.
- Eslatma vazifasi polling bilan parallel ishlaydi; xatolik bo'lsa `services/reminders.py` uni logga yozadi va tsikl davom etadi.

## Bog'liq fayllar

- [`config.py`](../../config.py) — sozlamalar
- [`database/db.py`](../../database/db.py) — baza tayyorlash
- [`handlers/`](../../handlers) — routerlar
- [`services/reminders.py`](../../services/reminders.py) — eslatmalar
