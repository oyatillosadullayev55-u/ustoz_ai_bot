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
| AI Ustoz | Savol-javob, AI provayderi yoki dars bazasidan fallback, kunlik limit |
| Darslar | 10 fan, 20 dars, darsni tugatish va natijani kuzatish |
| Testlar | Har urinishda 5 ta tasodifiy savol, 4 variant, yakuniy natija |
| Natijalar | Testlar, o'rtacha va eng yaxshi natija, faol kunlar, streak |
| Kunlik reja | Dars va test maqsadi, progress ko'rsatkichlari |
| Sozlamalar | Daraja, bildirishnomalar, til va AI holati |
| Admin panel | Statistika, foydalanuvchilarga xabar yuborish |
| Kontent | JSON orqali fan, dars va savollarni boshqarish |

Jami: **10 fan**, **20 dars**, **60 savol**. Har bir savolda 4 ta variant va izoh.

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
   ├── services/ai_service.py ── AI provayderi + lokal fallback
   ▼
database/  ── SQL so'rovlar qatlami
   │
   ▼
SQLite (WAL, foreign keys, busy_timeout)
```

- **bot.py** — logging, Dispatcher, routerlarni ulash, xatolarni markaziy ushlash,
  bot buyruqlarini o'rnatish va pollingni boshlash.
- **config.py** — `.env` dan sozlamalarni o'qiydi, qiymatlarni tekshiradi.
  Sozlamalar `lru_cache` bilan bir marta o'qiladi.
- **handlerlar** — har bir bo'lim alohida router. Har bir handler avval
  foydalanuvchining bazada borligini tekshiradi.
- **database/** — har bir jadval uchun alohida modul; SQL faqat shu qatlamda.
- **services/ai_service.py** — tashqi AI bilan ishlash; handler AI provayderining
  detallarini bilmaydi.
- **time_utils.py** — UTC saqlash, UTC+5 bo'yicha kun va streak hisoblash.

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
| `lessons` | Darslar | `id`, `subject_id` (FK), `title`, `content`, `order_index`, `is_active` |
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
2. Fan tanlanganda darslar ro'yxati ochiladi; tugatilgan darslar ✅ bilan belgilanadi.
3. Dars ochilganda `study_progress` ga `started` holati yoziladi.
4. «✅ Darsni tugatdim» birinchi bosishda `completed` holatiga o'tadi va kunlik
   rejaga +1 dars qo'shadi. Takroriy bosish qayta hisoblanmaydi.
5. Darsdan to'g'ridan-to'g'ri shu fan testiga o'tish mumkin.

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
- Bildirishnomalar o'chirilgan foydalanuvchilarga admin broadcast yuborilmaydi.
- Til hozircha ko'rsatiladi; interfeys matnlari o'zbek tilida.

### 7. AI Ustoz

1. Foydalanuvchi «🧠 AI Ustoz» tugmasini bosadi — FSM `chatting` holatiga o'tadi.
2. Savol 2–1000 belgi oralig'ida tekshiriladi.
3. Kunlik limit va minimal tanaffus tekshiriladi.
4. Suhbat tarixining oxirgi N xabari kontekst sifatida olinadi.
5. AI provayderi sozlanmagan yoki xato bo'lsa, dars bazasidan mos parcha qidiriladi.
6. Javob HTML sifatida ekranlanadi va 3900 belgigacha qisqartiriladi.
7. «⬅️ Chiqish» yoki menyu tugmasi rejimdan chiqaradi.

### 8. Admin panel

- Faqat `ADMIN_IDS` ro'yxatidagi Telegram ID'lar uchun.
- Statistika: foydalanuvchilar, bugungi faollik, testlar, darslar, AI so'rovlari,
  kontent soni.
- Broadcast: matn (1–3000 belgi) → tasdiqlash → yuborish.
- Telegram `retry after` limiti hisobga olinadi; yakunda muvaffaqiyat va xatolar soni
  ko'rsatiladi.

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
- Provayder xatosi yoki timeout → dars bazasidan javob + ogohlantirish.
- Mos dars topilmasa → mavjud fanlar ro'yxati va aniqroq yozish taklifi.

API kaliti faqat `.env` dan o'qiladi, loglarga yozilmaydi. Xato loglarida HTTP
status kodi qayd etiladi, kalit yoki so'rov matni emas.

## Xavfsizlik

- Token va AI kaliti faqat `.env` da; `.env`, baza, loglar `.gitignore` da.
- Foydalanuvchi ismi va AI javoblari HTML sifatida ekranlanadi.
- Kiritilgan matn uzunligi tekshiriladi (ism, savol, broadcast).
- Testda to'g'ri javob yakuniy natijagacha oshkor qilinmaydi.
- Callback ma'lumotlari qayta tekshiriladi; eskirgan holat rad etiladi.
- Bir foydalanuvchining test javoblari `asyncio.Lock` bilan ketma-ket qayta ishlanadi.
- AI uchun timeout, kunlik limit va minimal interval qo'llanadi.
- Admin amallari `ADMIN_IDS` bilan cheklangan.
- Kutilmagan xatolar markaziy handler orqali logga yoziladi.

## Testlar

Loyihada Telegram'ga ulanmasdan ishlaydigan ikkita test to'plami bor:

| Test | Qamrov | Natija |
| --- | --- | --- |
| `tests/test_offline.py` | Baza sxemasi, kontent, qidiruv, natijalar, streak, AI fallback, admin statistikasi | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | Ro'yxatdan o'tish, dars, 5 savolli test, statistika, reja, sozlamalar, AI, `/id`, admin, broadcast | `HANDLER_FLOW_OK` |

Testlar vaqtinchalik SQLite faylidan foydalanadi va haqiqiy bazaga tegmaydi.
Handler testi aiogram `FakeSession` orqali chiquvchi so'rovlarni ushlaydi; bu
tarmoqqa ulanmasdan to'liq foydalanuvchi oqimini tekshirish imkonini beradi.

```powershell
python tests\test_offline.py
python tests\test_handlers_offline.py
```

## Kontentni boshqarish

Manba: `content/seed_data.json`.

- Fan `id` va `code` barqaror bo'lishi kerak.
- Dars `id` — global unikal son.
- Savol ID'si avtomatik `dars_id * 10 + tartib` bo'ladi.
- Har bir savolda aynan 4 ta variant va `0`–`3` oralig'idagi `correct` bo'lishi shart.
- Bot har ishga tushganda kontent upsert qilinadi; JSON'dan olib tashlangan fan yoki
  dars `is_active = 0` bo'ladi, foydalanuvchi natijalari saqlanadi.
- Savollar har safar qayta yoziladi, shuning uchun savol matnini o'zgartirish uchun
  botni qayta ishga tushirish kifoya.

## Fayl tuzilmasi

```text
ustoz_ai_bot/
├── bot.py                 # Kirish nuqtasi, Dispatcher, routerlar
├── config.py              # .env sozlamalari va validatsiya
├── time_utils.py          # UTC+5 vaqt va streak
├── content/seed_data.json # O'quv kontenti
├── database/              # Sxema, seed va jadval modullari
├── handlers/              # Bo'limlar bo'yicha routerlar
├── keyboards/             # Reply va inline klaviaturalar
├── services/ai_service.py # AI provayderi va fallback
├── tests/                 # Offline testlar
└── docs/                  # Ushbu hujjat va foydalanuvchi qo'llanmasi
```

## Cheklovlar

- FSM holati `MemoryStorage` da — bot qayta ishga tushsa, tugallanmagan test yoki
  AI suhbati holati yo'qoladi (natijalar bazada saqlanadi).
- Eslatmalar uchun scheduler hali yo'q; kunlik reja faqat qo'lda ochiladi.
- Interfeys faqat o'zbek tilida.
- SQLite bitta bot nusxasi uchun mo'ljallangan; bir vaqtda bir nechta polling
  jarayoni ishlatilmasligi kerak.
- Vaqt mintaqasi UTC+5 ga belgilangan.

## Kelgusi ishlar

- Eslatmalar va kunlik reja bo'yicha avtomatik bildirishnomalar.
- Ko'proq dars, savol va fan qo'shish.
- Natijalar bo'yicha batafsil tahlil (mavzular kesimida).
- Ko'p tilli interfeys.
- Docker yoki server uchun deployment qo'llanmasi.
