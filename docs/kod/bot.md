# `bot.py` — kirish nuqtasi

**Yo'l:** [`bot.py`](../../bot.py)
**Vazifasi:** botni ishga tushirish, loggingni sozlash, routerlarni ulash va kunlik eslatma vazifasini boshqarish.

## Asosiy funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `setup_logging(level)` | Konsol va `logs/bot.log` uchun aylanadigan log sozlamalarini o'rnatadi (1 MB × 3 fayl). |
| `set_bot_commands(bot, settings)` | Telegramdagi buyruqlar menyusini o'rnatadi; adminlar uchun `/admin` qo'shadi. |
| `on_error(event)` | `ErrorEvent` orqali kutilmagan xatolarni logga yozadi va foydalanuvchiga xabar beradi. |
| `run_bot(settings)` | Health server va bazani tayyorlaydi, `Bot` va `Dispatcher` yaratadi, routerlarni ulaydi, pollingni boshlaydi. |
| `main()` | `.env` sozlamalarini o'qiydi, loggingni yoqadi va `asyncio.run(run_bot(...))` chaqiradi. |

## Ishga tushish tartibi

1. `get_settings()` orqali `.env` tekshiriladi. `BOT_TOKEN` bo'lmasa dastur `ConfigError` bilan to'xtaydi.
2. Logging sozlanadi va AI holati haqida qisqa log yoziladi (kalitning o'zi hech qachon logga tushmaydi).
3. `start_health_server()` chaqiriladi. `PORT` berilgan bo'lsa (Render yoki Docker), HTTP
   server `/`, `/health`, `/healthz` manzillarida javob beradi; lokal ishda `PORT` bo'sh
   bo'lsa, server ochilmaydi.
4. `init_db()` 8 ta jadvalni yaratadi, migratsiyani bajaradi va kontentni yuklaydi.
5. Routerlar tartib bilan ulanadi: `start → ai_tutor → lessons → quizzes → progress → daily_plan → settings → admin → menu`.
6. `DAILY_REMINDERS_ENABLED=true` bo'lsa `run_daily_reminders(bot)` fon vazifasi sifatida ishga tushadi.
7. `dispatcher.start_polling(bot)` Telegramdan yangilanishlarni qabul qiladi.
8. Dastur to'xtaganda eslatma vazifasi bekor qilinadi, bot sessiyasi va health server yopiladi (`finally`).

## Muhim jihatlar

- Bot tokeni faqat `Settings` orqali ishlatiladi; kodda yoki logda saqlanmaydi.
- `menu` routeri eng oxirida turadi, shuning uchun u boshqa routerlar tanimagan xabarlar uchun zaxira bo'ladi.
- `/qidiruv` buyrug'i global buyruqlar ro'yxatiga qo'shilgan.
- Eslatma vazifasi polling bilan parallel ishlaydi; xatolik bo'lsa `services/reminders.py` uni logga yozadi va tsikl davom etadi.
- Health server faqat port tinglaydi; Telegram pollingga ta'sir qilmaydi va foydalanuvchi
  ma'lumotini ko'rsatmaydi. `RENDER_GIT_COMMIT` bo'lsa, javobda qisqartirilgan commit
  hash qaytadi.

## Bog'liq fayllar

- [`config.py`](../../config.py) — sozlamalar
- [`database/db.py`](../../database/db.py) — baza tayyorlash
- [`handlers/`](../../handlers) — routerlar
- [`services/reminders.py`](../../services/reminders.py) — eslatmalar
- [`services/health_server.py`](../../services/health_server.py) — health-check server
- [`docs/SERVERGA_JOYLASH.md`](../../SERVERGA_JOYLASH.md) — serverga joylash qo'llanmasi
