# UstozAI — loyiha hujjati

Bu hujjat UstozAI Telegram botining arxitekturasi, ma'lumotlar bazasi, asosiy
oqimlari va texnik qarorlarini tavsiflaydi.

- **Maqsad:** o'zbek tilida sifatli ta'limni qulay va qiziqarli qilish.
- **Auditoriya:** maktab o'quvchilari, talabalar va mustaqil o'rganuvchilar.
- **Til:** interfeys va AI javoblari o'zbek tilida.
- **Platforma:** Telegram, polling rejimi.
- **Stack:** Python 3.13, aiogram 3.22, aiosqlite, SQLite, aiohttp, python-dotenv.

## Imkoniyatlar

| Bo'lim | Tavsif |
| --- | --- |
| Ro'yxatdan o'tish | Ism, bilim darajasi (boshlang'ich / o'rta / yuqori), ma'lumotlarni saqlash |
| AI Ustoz | Savol-javob, AI provayderi yoki dars bazasidan fallback, dars konteksti, kunlik limit |
| Darslar | 8 fan, 35 dars; qisqa mazmun, 3 asosiy fikr, batafsil izoh, mini mashq, oldingi/keyingi dars |
| Qidiruv | Darslarni nomi va mazmuni bo'yicha topish (`/qidiruv`) |
| Testlar | Har urinishda 5 ta tasodifiy savol, 4 variant, yakuniy natija va xato javoblar tahlili |
| Natijalar | Testlar, o'rtacha va eng yaxshi natija, faol kunlar, streak |
| Kunlik reja | Dars va test maqsadi, progress ko'rsatkichlari |
| Eslatmalar | Reja bajarilmagan foydalanuvchilarga kunlik eslatma |
| Sozlamalar | Daraja, bildirishnomalar, til va AI holati |
| Admin panel | Statistika, foydalanuvchilarga xabar yuborish |
| Kontent | JSON orqali fan, dars va savollarni boshqarish |
| Joylash | Render bepul tarifi, Docker/Compose, Oracle Always Free, `/health` |

Jami: **8 fan**, **35 dars**, **140 savol** (har bir darsda 4 tadan). Har bir
savolda 4 ta variant va izoh bor.

## Arxitektura

```text
Telegram
   │
   ▼
aiogram Dispatcher (polling)
   │  routerlar tartibi:
   │  start → ai_tutor → lessons → quizzes → progress →
   │  daily_plan → settings → admin → menu
   ▼
handlers/  ── FSM, validatsiya, foydalanuvchi oqimlari
   │
   ├── keyboards/  ── reply va inline tugmalar
   ├── services/ai_service.py ── AI provayderi + lokal fallback + dars konteksti
   ├── services/lesson_media.py ── dars rasmlari + file_id kesh
   ├── services/health_server.py ── Render uchun /health HTTP serveri
   ├── services/reminders.py ── kunlik eslatmalar
   ▼
database/  ── SQL so'rovlar qatlami
   │
   ▼
SQLite (WAL, foreign keys, busy_timeout)
```

- **bot.py** — logging, Dispatcher, routerlarni ulash, xatolarni markaziy ushlash,
  bot buyruqlarini o'rnatish, kunlik eslatma vazifasini ishga tushirish, ixtiyoriy
  health-check serverini ochish va pollingni boshlash.
- **config.py** — `.env` dan sozlamalarni o'qiydi, qiymatlarni tekshiradi.
  Sozlamalar `lru_cache` bilan bir marta o'qiladi.
- **handlerlar** — har bir bo'lim alohida router. Har bir handler avval
  foydalanuvchining bazada borligini tekshiradi.
- **database/** — har bir jadval uchun alohida modul; SQL faqat shu qatlamda.
- **services/ai_service.py** — tashqi AI bilan ishlash; handler AI provayderining
  detallarini bilmaydi. Darsdan ochilgan AI rejimida dars matni alohida system
  xabari sifatida beriladi.
- **services/lesson_media.py** — dars rasmlarini `assets/lesson_images/` dan topadi,
  birinchi yuborishdan keyin Telegram `file_id` sini keshlaydi. Dizayn tafsilotlari:
  [`DARS_DIZAYNI.md`](DARS_DIZAYNI.md).
- **services/health_server.py** — `PORT` o'rnatilgan bo'lsa `/`, `/health` va
  `/healthz` manzillarida javob beradigan kichik aiohttp serveri. Render bepul
  web-service talab qiladigan portni shu server ta'minlaydi; lokal ishda `PORT`
  bo'sh bo'lsa, server ochilmaydi.
- **services/reminders.py** — kunlik reja bo'yicha eslatmalarni yuboradi; Telegram
  limitlarini hisobga oladi va faqat ruxsat bergan foydalanuvchilarga yozadi.
- **time_utils.py** — UTC saqlash, UTC+5 bo'yicha kun va streak hisoblash.

Serverga joylash: `Dockerfile`, `docker-compose.yml` va `render.yaml`. Bepul
Render tarifi tez sinov uchun, Oracle Always Free esa doimiy SQLite bazasi uchun
mo'ljallangan. To'liq qo'llanma: [`SERVERGA_JOYLASH.md`](SERVERGA_JOYLASH.md).

Routerlar tartibi muhim: `menu` routeri eng oxirida turadi, chunki unda noma'lum
matn va boshqa callback'lar uchun catch-all handlerlar bor. Maxsus routerlar
(masalan, testlar) undan oldin ishlaydi.

## Ma'lumotlar bazasi

SQLite fayli `.env` dagi `DATABASE_PATH` bo'yicha yaratiladi. Ulanishda
`PRAGMA foreign_keys = ON`, `PRAGMA busy_timeout = 5000` va WAL rejimi yoqiladi.
Sxema idempotent: `CREATE TABLE IF NOT EXISTS`.

### Jadvalar

| Jadval | Vazifasi | Muhim ustunlar |
| --- | --- | --- |
| `users` | Foydalanuvchi profili | `telegram_id` (PK), `full_name`, `language`, `level`, `notifications_enabled` |
| `subjects` | Fanlar | `id`, `code` (UNIQUE), `name`, `emoji`, `order_index`, `is_active` |
| `lessons` | Darslar | `id`, `subject_id` (FK), `title`, `content`, `summary`, `key_points`, `level`, `duration_min`, `order_index`, `is_active` |
| `questions` | Test savollari | `id`, `lesson_id` (FK), `question_text`, `option_a..d`, `correct_option` (0–3), `explanation` |
| `quiz_results` | Test natijalari | `user_id` (FK), `subject_id` (FK), `total_questions`, `correct_answers`, `score_percent` |
| `study_progress` | Dars progressi | PK (`user_id`, `lesson_id`), `status` (`started` / `completed`) |
| `chat_history` | AI suhbati | `user_id` (FK), `role` (`user` / `assistant`), `message` |
| `daily_goals` | Kunlik maqsad | UNIQUE (`user_id`, `goal_date`), maqsad va bajarilgan sonlar |

### Bog'lanishlar

- `lessons.subject_id → subjects.id`
- `questions.lesson_id → lessons.id`
- `quiz_results.user_id → users.telegram_id`
- `quiz_results.subject_id → subjects.id`
- `study_progress.user_id → users.telegram_id`
- `study_progress.lesson_id → lessons.id`
- `chat_history.user_id → users.telegram_id`
- `daily_goals.user_id → users.telegram_id`

Foydalanuvchi o'chirilsa, unga tegishli natijalar, progress, suhbat va maqsadlar
ham o'chadi (`ON DELETE CASCADE`). Fan yoki dars o'chirilsa, unga tegishli darslar
va savollar o'chadi.

### Vaqt va kun

- Bazada barcha vaqtlar UTC ISO formatida saqlanadi.
- Kunlik maqsad va streak **UTC+5** (O'zbekiston) bo'yicha hisoblanadi.
- `goal_date` — `YYYY-MM-DD` ko'rinishidagi mahalliy sana.

## Asosiy oqimlar

### 1. Ro'yxatdan o'tish

1. `/start` → foydalanuvchi bazada bo'lsa, bosh menyu ko'rsatiladi.
2. Yangi foydalanuvchidan ism so'raladi (2–50 belgi).
3. Bilim darajasi inline tugmalar orqali tanlanadi.
4. `users` jadvaliga yoziladi; qayta `/start` dublikat yaratmaydi.

### 2. Darslar

1. Fanlar ro'yxati dars va savollar soni bilan chiqadi.
2. Fan tanlanganda darslar ro'yxati, tugatilgan darslar hisobi va progress bar ochiladi.
3. Dars 16:9 rasmli kartochka bo'lib ochiladi: fan va dars raqami, sarlavha, qisqa
   mazmun, 3 ta asosiy fikr, davomiylik va daraja. `study_progress` ga `started`
   holati yoziladi.
4. **📖 Batafsil o'qish** to'liq dars matnini alohida ekranda ochadi: maqsad, sodda
   tushuntirish, hayotiy misol, asosiy fikrlar, eslab qolish siri, mini mashq va
   xulosa. 4000 belgi limiti amal qiladi; **🖼️ Kartochkaga qaytish** orqali rasmli
   ko'rinishga qaytiladi.
5. **⬅️ Oldingi dars** va **➡️ Keyingi dars** tugmalari shu fan ichida navigatsiyani
   beradi; **🧠 AI Ustozga so'rash** shu dars konteksti bilan AI rejimini ochadi.
6. «✅ Darsni tugatdim» birinchi bosishda `completed` holatiga o'tadi, joriy ekran
   (kartochka yoki batafsil matn) yangilanadi va kunlik rejaga +1 dars qo'shiladi.
   Takroriy bosish qayta hisoblanmaydi.
7. Darsdan to'g'ridan-to'g'ri shu fan testiga o'tish mumkin.
8. `/qidiruv so'z` buyrug'i dars nomi va mazmuni bo'yicha izlaydi. So'rov 2–100
   belgi, natijalar soni 5 ta bilan cheklangan; natijadan darsni darhol ochish mumkin.
9. Rasm topilmasa yoki caption 1024 belgidan oshsa, dars matnli kartochka sifatida
   ochiladi — mazmun yo'qolmaydi.

### 3. Testlar

1. Fan tanlanadi; bazadan `ORDER BY RANDOM()` bilan 5 ta savol olinadi.
2. Savol matni va 4 ta variant inline tugma sifatida chiqadi.
3. Foydalanuvchi javob berganda to'g'riligi **darhol oshkor qilinmaydi**.
4. Har bir javob callback ID'sida faqat savol ID'si va variant indeksi bo'ladi —
   to'g'ri javob callback ichida yuborilmaydi.
5. Savol ID'si va joriy holat FSM bilan solishtiriladi; eskirgan yoki takroriy
   callback rad etiladi. Bir foydalanuvchi uchun `asyncio.Lock` ishlatiladi.
6. Test yakunida natija `quiz_results` ga yoziladi, foiz hisoblanadi va kunlik
   rejaga +1 test qo'shiladi.
7. Yakunda faqat xato javoblar bo'yicha alohida tahlil xabari yuboriladi: savol,
   tanlangan variant, to'g'ri variant va izoh. Barcha javob to'g'ri bo'lsa, tahlil
   yuborilmaydi. Bu to'g'ri javoblarni test davomida oshkor qilmaydi.

### 4. Statistika va streak

- Testlar soni, o'rtacha va eng yaxshi foiz.
- Tugatilgan darslar va AI savollari soni.
- Oxirgi 5 test natijasi.
- Faol kunlar: test natijalari, dars progressi va AI suhbati sanalari birlashtiriladi.
- Streak: bugundan (yoki kechadan) orqaga qarab ketma-ket faol kunlar.

### 5. Kunlik reja

- Har bir foydalanuvchi va kun uchun bitta yozuv.
- Birinchi ochilishda standart maqsad 1 dars + 1 test yaratiladi.
- Tayyor shablonlar: 1/1, 2/2, 3/3.
- Dars tugatilganda yoki test yakunlanganda bajarilgan sonlar atomar oshiriladi.

### 6. Sozlamalar

- Bilim darajasini o'zgartirish keyingi AI javoblarining uslubiga ta'sir qiladi.
- Bildirishnomalar o'chirilgan foydalanuvchilarga admin broadcast va kunlik
  eslatmalar yuborilmaydi.
- Til hozircha ko'rsatiladi; interfeys matnlari o'zbek tilida.

### 7. AI Ustoz

1. Foydalanuvchi «🧠 AI Ustoz» tugmasini bosadi — FSM `chatting` holatiga o'tadi.
   Dars kartochkasidagi «🧠 AI Ustozga so'rash» ham shu holatga o'tadi va FSM'ga
   `lesson_context` (fan, sarlavha, qisqa mazmun, dars matni) yozadi.
2. Savol 2–1000 belgi oralig'ida tekshiriladi.
3. Kunlik limit va minimal tanaffus tekshiriladi.
4. Suhbat tarixining oxirgi N xabari kontekst sifatida olinadi.
5. Dars konteksti bo'lsa, AI ga alohida system xabari yuboriladi: tushunarsiz joyni
   shu dars asosida sodda tushuntirish, hayotiy misol va mini mashq berish so'raladi.
6. AI provayderi sozlanmagan yoki xato bo'lsa, dars konteksti bo'lsa shu darsdan,
   aks holda bazadan mos parcha qidiriladi.
7. Javob HTML sifatida ekranlanadi va 3900 belgigacha qisqartiriladi.
8. «⬅️ Chiqish» yoki menyu tugmasi rejimdan chiqaradi va dars kontekstini tozalaydi.

### 8. Admin panel

- Faqat `ADMIN_IDS` ro'yxatidagi Telegram ID'lar uchun.
- Statistika: foydalanuvchilar, bugungi faollik, testlar, darslar, AI so'rovlari,
  kontent soni.
- Broadcast: matn (1–3000 belgi) → tasdiqlash → yuborish.
- Telegram `retry after` limiti hisobga olinadi; yakunda muvaffaqiyat va xatolar soni
  ko'rsatiladi.

### 9. Kunlik eslatmalar

1. `bot.py` ishga tushganda `DAILY_REMINDERS_ENABLED=true` bo'lsa, fon vazifasi
   yaratiladi.
2. Vazifa `DAILY_REMINDER_HOUR` (UTC+5) gacha kutadi, so'ng bugungi rejani tekshiradi.
3. Faqat bugun `daily_goals` yozuvi bor, maqsad bajarilmagan va bildirishnomalari
   yoqilgan foydalanuvchilar tanlanadi.
4. Har bir foydalanuvchiga bajarilgan/rejalashtirilgan dars va test soni yuboriladi.
5. Xabarlar orasida qisqa tanaffus qo'llanadi; `retry after` bo'lsa bir marta
   qayta uriniladi. Xatolar logga yoziladi, keyingi foydalanuvchiga o'tiladi.
6. Keyingi eslatma vaqti logga mahalliy vaqtda yoziladi; bot to'xtatilganda vazifa
   bekor qilinadi.

## AI xizmati

`services/ai_service.py` OpenAI bilan mos `/chat/completions` API'siga so'rov
yuboradi. Provayder, model va manzil `.env` orqali sozlanadi.

| Chegara | Standart qiymat |
| --- | --- |
| Kunlik so'rov limiti | 30 |
| So'rovlar orasidagi tanaffus | 3 soniya |
| Timeout | 30 soniya |
| Maksimal javob tokeni | 700 |
| Tarixga qo'shiladigan xabarlar | 8 |

Fallback mantiqi:

- `AI_ENABLED=false` yoki kalit yo'q → dars bazasidan javob + izoh.
- Dars konteksti berilgan bo'lsa → avval shu dars matnidan tegishli parcha olinadi.
- Provayder xatosi yoki timeout → dars bazasidan javob + ogohlantirish.
- Mos dars topilmasa → mavjud fanlar ro'yxati va aniqroq yozish taklifi.

API kaliti faqat `.env` yoki hosting environment'idan o'qiladi, loglarga yozilmaydi.
Xato loglarida HTTP status kodi qayd etiladi, kalit yoki so'rov matni emas.

## Xavfsizlik

- Token va AI kaliti faqat `.env` yoki hosting environment'ida; `.env`, baza, loglar
  `.gitignore` da, `.env` Docker image'ga kirmaydi.
- Foydalanuvchi ismi va AI javoblari HTML sifatida ekranlanadi.
- Kiritilgan matn uzunligi tekshiriladi (ism, savol, qidiruv so'rovi, broadcast).
- Testda to'g'ri javob yakuniy natijagacha oshkor qilinmaydi.
- Callback ma'lumotlari qayta tekshiriladi; eskirgan holat rad etiladi.
- Bir foydalanuvchining test javoblari `asyncio.Lock` bilan ketma-ket qayta ishlanadi.
- AI uchun timeout, kunlik limit va minimal interval qo'llanadi.
- Admin amallari `ADMIN_IDS` bilan cheklangan.
- Kunlik eslatmalar faqat bildirishnomalarga ruxsat bergan foydalanuvchilarga yuboriladi.
- Health server faqat `PORT` berilganda ochiladi va maxfiy ma'lumot qaytarmaydi.
- Kutilmagan xatolar markaziy handler orqali logga yoziladi.
- Serverda `.env` huquqi `600`; token oshkor bo'lsa, BotFather'da `/revoke` qilinadi.

## Testlar

Loyihada Telegram'ga ulanmasdan ishlaydigan ikkita test to'plami bor:

| Test | Qamrov | Natija |
| --- | --- | --- |
| `tests/test_offline.py` | Baza sxemasi va migratsiya, 140 savol, dars maydonlari, qidiruv, savollarni ID bo'yicha olish, natijalar, streak, vaqt yordamchilari, eslatmalar, AI fallback va dars konteksti, health server, admin statistikasi | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | Ro'yxatdan o'tish, rasmli kartochka, asosiy fikrlar, batafsil o'qish, oldingi/keyingi dars, batafsil ekranda tugatish, dars AI konteksti, qidiruv, 5 savolli test va xato tahlili, statistika, reja, sozlamalar, AI, `/id`, admin, broadcast, eslatma | `HANDLER_FLOW_OK` |

Testlar vaqtinchalik SQLite faylidan foydalanadi va haqiqiy bazaga tegmaydi.
Handler testi aiogram `FakeSession` orqali chiquvchi so'rovlarni ushlaydi; bu
tarmoqqa ulanmasdan to'liq foydalanuvchi oqimini tekshirish imkonini beradi.

```powershell
python tests\test_offline.py
python tests\test_handlers_offline.py
```

### Kod sifati va CI

- `pyproject.toml` Ruff sozlamalarini saqlaydi (`E`, `F`, `W`, `I`, `UP`, `B`).
- `requirements-dev.txt` test va lint uchun qo'shimcha paketlarni beradi.
- `.github/workflows/ci.yml` har push va pull request'da Python 3.13 muhitida
  Ruff va ikkala offline testni ishga tushiradi.

```powershell
pip install -r requirements-dev.txt
ruff check .
python -m compileall -q .
```

## Kontentni boshqarish

Manba: `content/seed_data.json`.

- Fan `id` va `code` barqaror bo'lishi kerak.
- Dars `id` — global unikal son.
- Har bir darsda `summary` (qisqa mazmun), `key_points` (1–5 ta asosiy fikr),
  `level` (`beginner` / `intermediate` / `advanced`) va `duration_min` (1–120) bor.
- Savol ID'si avtomatik `dars_id * 10 + tartib` bo'ladi.
- Har bir savolda aynan 4 ta variant va `0`–`3` oralig'idagi `correct` bo'lishi shart.
- Bot har ishga tushganda kontent upsert qilinadi; JSON'dan olib tashlangan fan yoki
  dars `is_active = 0` bo'ladi, foydalanuvchi natijalari saqlanadi.
- Savollar har safar qayta yoziladi, shuning uchun savol matnini o'zgartirish uchun
  botni qayta ishga tushirish kifoya.
- Eski bazaga yangi dars ustunlari `ALTER TABLE` orqali qo'shiladi; mavjud progress
  va natijalar saqlanadi.

## Fayl tuzilmasi

```text
ustoz_ai_bot/
├── bot.py                    # Kirish nuqtasi, Dispatcher, routerlar
├── config.py                 # .env sozlamalari va validatsiya
├── time_utils.py             # UTC+5 vaqt va streak
├── pyproject.toml            # Ruff sozlamalari
├── requirements.txt          # Ish vaqti kutubxonalari
├── requirements-dev.txt      # Ruff va testlar uchun
├── Dockerfile                # Python 3.13 image
├── docker-compose.yml        # Doimiy baza bilan ishga tushirish
├── render.yaml               # Render bepul web-service blueprint
├── .dockerignore
├── .github/workflows/ci.yml  # GitHub Actions CI
├── assets/lesson_images/     # 35 ta dars rasmi (1280x720 JPEG)
├── content/seed_data.json    # O'quv kontenti (140 savol)
├── database/                 # Sxema, seed va jadval modullari
├── handlers/                 # Bo'limlar bo'yicha routerlar
├── keyboards/                # Reply va inline klaviaturalar
├── services/                 # AI, rasm, health server va eslatmalar
├── tests/                    # Offline testlar
├── docs/                     # Hujjatlar va har bir kod fayli uchun tavsif
└── data/                     # Docker'dagi SQLite (git'ga kirmaydi)
```

## Cheklovlar

- FSM holati `MemoryStorage` da — bot qayta ishga tushsa, tugallanmagan test yoki
  AI suhbati holati yo'qoladi (natijalar bazada saqlanadi).
- Eslatmalar kuniga bir marta yuboriladi va faqat shu kuni kunlik reja ochilgan,
  maqsad bajarilmagan hamda bildirishnomalari yoqilgan foydalanuvchilarni qamrab
  oladi; alohida vaqt tanlash imkoniyati hozircha yo'q.
- Qidiruv SQLite `LIKE` bo'yicha ishlaydi; katta hajmdagi kontent uchun to'liq
  matnli indeks (FTS) keyinroq qo'shilishi mumkin.
- Interfeys faqat o'zbek tilida.
- SQLite bitta bot nusxasi uchun mo'ljallangan; bir vaqtda bir nechta polling
  jarayoni ishlatilmasligi kerak.
- Vaqt mintaqasi UTC+5 ga belgilangan.
- Render bepul tarifida doimiy disk yo'q: restartda baza nolga tushadi. Doimiy
  saqlash uchun Oracle Always Free + `docker compose` ishlatiladi.
- `MemoryStorage` tufayli bir nechta server instansiyasida FSM umumiy emas; polling
  uchun bitta instansiya saqlanadi.

## Kelgusi ishlar

- Foydalanuvchi o'zi eslatma vaqtini tanlashi.
- Ko'proq dars, savol va fan qo'shish.
- Natijalar bo'yicha batafsil tahlil (mavzular kesimida).
- Qidiruvni FTS bilan tezlashtirish va filtrlar qo'shish.
- Ko'p tilli interfeys.
- Doimiy tashqi baza (PostgreSQL) yoki bulutli disk bilan gorizontal masshtablash.
