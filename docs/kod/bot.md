# `bot.py` — kirish nuqtasi

**Yo'l:** [`bot.py`](../../bot.py)
**Vazifasi:** botni ishga tushirish, loggingni sozlash, routerlarni ulash va kunlik eslatma vazifasini boshqarish.

## Asosiy funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `log_start_environment()` | `[START]` qatorida `BOT_TOKEN`, `ADMIN_IDS` va `PORT` bor-yo'qligini qiymatlarsiz yozadi. Render logida birinchi bo'lib ko'rinadi. |
| `setup_logging(level)` | Konsol va `logs/bot.log` uchun aylanadigan log sozlamalarini o'rnatadi (1 MB × 3 fayl). |
| `set_bot_commands(bot, settings)` | Telegramdagi buyruqlar menyusini o'rnatadi; adminlar uchun `/admin` qo'shadi. |
| `on_error(event)` | `ErrorEvent` orqali kutilmagan xatolarni logga yozadi va foydalanuvchiga xabar beradi. |
| `run_bot(settings)` | Health server va bazani tayyorlaydi, `Bot` va `Dispatcher` yaratadi, routerlarni ulaydi, pollingni boshlaydi. |
| `main()` | `.env` sozlamalarini o'qiydi, loggingni yoqadi va `asyncio.run(run_bot(...))` chaqiradi. |

## Ishga tushish tartibi

1. `log_start_environment()` birinchi qatorni chop etadi:
   `[START] BOT_TOKEN: bor | ADMIN_IDS: bor | PORT: 10000`. Token qiymati hech qachon
   ko'rsatilmaydi. Render'da `BOT_TOKEN: YO'Q` chiqsa, environment to'ldirilmagan.
2. `get_settings()` orqali muhit tekshiriladi. `BOT_TOKEN` bo'lmasa yoki formati
   noto'g'ri bo'lsa dastur aniq `[XATO]` xabari bilan to'xtaydi.
3. Logging sozlanadi, baza/admin/AI/eslatma holati haqida qisqa log yoziladi
   (kalitning o'zi logga tushmaydi).
4. `start_health_server()` chaqiriladi. `PORT` berilgan bo'lsa (Render yoki Docker), HTTP
   server `/`, `/health`, `/healthz` manzillarida javob beradi; lokal ishda `PORT` bo'sh
   bo'lsa, server ochilmaydi.
5. `init_db()` 8 ta jadvalni yaratadi, migratsiyani bajaradi va kontentni yuklaydi.
6. Routerlar tartib bilan ulanadi: `start → ai_tutor → lessons → quizzes → progress → daily_plan → settings → admin → menu`.
7. `DAILY_REMINDERS_ENABLED=true` bo'lsa `run_daily_reminders(bot)` fon vazifasi sifatida ishga tushadi.
8. `dispatcher.start_polling(bot)` Telegramdan yangilanishlarni qabul qiladi.
9. Dastur to'xtaganda eslatma vazifasi bekor qilinadi, bot sessiyasi va health server yopiladi (`finally`).

## Muhim jihatlar

- Bot tokeni faqat `Settings` orqali ishlatiladi; kodda yoki logda saqlanmaydi.
- Telegram tokeni rad etsa (`401 Unauthorized`), `main()` buni alohida ushlaydi va
  BotFather'da yangi token olish bo'yicha aniq xabar yozadi; traceback o'rniga
  tushunarli sabab ko'rinadi.
- Start logida faqat muhit o'zgaruvchilarining bor-yo'qligi ko'rsatiladi, qiymatlari emas.
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
