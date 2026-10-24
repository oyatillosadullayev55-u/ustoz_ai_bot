# UstozAI — Bilim olish endi oson!

O'zbek tilida ishlaydigan to'liq ta'lim Telegram boti. **Python 3**, **aiogram 3**,
**SQLite** va **aiosqlite** asosida qurilgan.

> **Holat: barcha asosiy bo'limlar tayyor.** Ro'yxatdan o'tish, AI Ustoz, 10 fan
> bo'yicha darslar, 4 variantli testlar, natijalar statistikasi, kunlik reja,
> sozlamalar va admin panel ishlaydi.

## Hujjatlar

- [Loyiha hujjati](docs/LOYIHA.md) — arxitektura, baza sxemasi, asosiy oqimlar,
  AI cheklovlari, testlar va xavfsizlik.
- [Foydalanuvchi qo'llanmasi](docs/FOYDALANISH.md) — botdan foydalanish, buyruqlar,
  admin panelni sozlash va ko'p uchraydigan savollar.

## Nimalar ishlaydi

- `/start` — yangi foydalanuvchini ism va bilim darajasi orqali ro'yxatdan o'tkazadi.
- **AI Ustoz** — savol-javob rejimi. AI kaliti ulangan bo'lsa provayderdan javob oladi;
  kalit bo'lmasa dars bazasidan mos javob qidiradi. Kunlik limit va so'rovlar orasidagi
  tanaffus amal qiladi.
- **Darslar** — 10 fan, 20 dars. Dars matni, "Tugatdim" belgisi va shu darsdan testga
  o'tish.
- **Testlar** — har bir urinishda 5 ta tasodifiy savol, 4 ta variant. To'g'ri javob
  test yakunlanguncha ko'rsatilmaydi.
- **Mening natijalarim** — o'tilgan darslar, testlar soni, o'rtacha va eng yaxshi natija,
  faol kunlar, ketma-ket kunlar (streak), oxirgi 5 natija.
- **Kunlik reja** — dars va test maqsadi, bajarilish progressi, tayyor shablonlar.
- **Sozlamalar** — bilim darajasi, bildirishnomalar, joriy til va AI holati.
- **Admin panel** — `/admin`: statistika va barcha foydalanuvchilarga xabar yuborish.
- Xatolar `logs/bot.log` fayliga yoziladi; bot kutilmagan xatodan qulab tushmaydi.
- Bot tokeni va AI kaliti faqat `.env` faylidan o'qiladi.

### O'quv kontenti

| Fan | Darslar |
| --- | --- |
| Ingliz tili | 2 |
| Matematika | 2 |
| Fizika | 2 |
| Kimyo | 2 |
| Biologiya | 2 |
| Tarix | 2 |
| Ona tili va adabiyot | 2 |
| Informatika | 2 |
| Python | 2 |
| Dart va Flutter | 2 |

Jami **10 fan**, **20 dars**, **60 savol**. Har bir savolda 4 ta variant va izoh bor.

## Muhim: Python versiyasi

Loyiha **Python 3.11–3.13** uchun mo'ljallangan. Eng tavsiya etilgani — **Python 3.13**.

Python 3.14 va 3.15 hozircha ishlatilmasin: aiogram 3.22 talab qiladigan
`pydantic` va `aiohttp` paketlarining bu versiyalar uchun tayyor o'rnatish fayllari
yo'q. Natijada Windows'da "Microsoft Visual C++ 14.0 is required" xatosi chiqadi.

Loyiha **Python 3.13.15**, **aiogram 3.22.0** va **aiosqlite 0.22.1** bilan tekshirilgan.

```powershell
py -0p
```

Ro'yxatda 3.13 bo'lmasa:

```powershell
winget install -e --id Python.Python.3.13 --scope user
```

O'rnatishda **"Add python.exe to PATH"** belgisini qo'ying.

## Reponi klonlash

```powershell
git clone https://github.com/oyatillosadullayev55-u/ustoz_ai_bot.git
Set-Location ustoz_ai_bot
```

Keyin quyidagi bo'limlardagi kabi `.venv` yarating va `.env` faylini sozlang.

## PyCharm'da ochish

1. **File → Open** orqali `ustoz_ai_bot` papkasini oching.
2. Terminal oynasini oching (`Alt + F12`).
3. **Settings → Project: ustoz_ai_bot → Python Interpreter → Add Interpreter →
   Add Local Interpreter → Existing** bo'limida `.venv\Scripts\python.exe` ni tanlang.
4. **Run → Edit Configurations → + → Python**:
   - Script path: `bot.py`
   - Working directory: loyiha papkasi
   - Python interpreter: `.venv` ichidagi Python
5. Loyihada **UstozAI Bot** degan tayyor Run konfiguratsiyasi ham bor. Uni tanlab,
   yashil **Run** tugmasini bosing. Ko'rinmasa, PyCharm'ni qayta oching yoki `bot.py`
   faylida o'ng tugma → **Run 'bot'**.

## Virtual muhit va kutubxonalar (PowerShell)

```powershell
Set-Location C:\Loyihalar\ustoz_ai_bot

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Yo'lni o'zingizdagi loyiha papkasiga moslang.

Agar PowerShell skriptlarni bloklasa:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Muqobil: `.\.venv\Scripts\activate.bat`.

## BotFather orqali token olish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga o'ting.
2. `/newbot` → nom (`UstozAI`) → username (oxiri `bot` bilan).
3. Berilgan tokenni faqat `.env` fayliga yozing. Tokenni chatda, skrinshotda yoki
   GitHub'da ulashmang.
4. Token oshkor bo'lgan bo'lsa, **darhol** BotFather'da `/revoke` qilib yangisini oling.

## `.env` faylini sozlash

`.env` mavjud bo'lmasa:

```powershell
Copy-Item .env.example .env
notepad .env
```

Namuna:

```dotenv
BOT_TOKEN=123456789:AAE...
ADMIN_IDS=123456789
DATABASE_PATH=ustoz_ai.db
LOG_LEVEL=INFO
DEFAULT_LANGUAGE=uz

AI_ENABLED=false
AI_API_KEY=
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
AI_TIMEOUT=30
AI_DAILY_LIMIT=30
AI_MIN_INTERVAL=3
AI_MAX_TOKENS=700
AI_HISTORY_LIMIT=8
```

| O'zgaruvchi | Ma'nosi |
| --- | --- |
| `BOT_TOKEN` | BotFather bergan token (majburiy) |
| `ADMIN_IDS` | Admin Telegram ID'lari, vergul bilan |
| `DATABASE_PATH` | SQLite fayli yo'li |
| `LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR yoki CRITICAL |
| `DEFAULT_LANGUAGE` | uz, ru yoki en |
| `AI_ENABLED` | AI provayderidan foydalanish (true/false) |
| `AI_API_KEY` | Provayder API kaliti (faqat `.env` da) |
| `AI_BASE_URL` | OpenAI bilan mos API manzili |
| `AI_MODEL` | Model nomi |
| `AI_TIMEOUT` | Javob kutish vaqti, soniya (5–120) |
| `AI_DAILY_LIMIT` | Bir foydalanuvchi uchun kunlik so'rov limiti (1–500) |
| `AI_MIN_INTERVAL` | So'rovlar orasidagi minimal tanaffus, soniya (0–60) |
| `AI_MAX_TOKENS` | Bitta javob uchun maksimal token (100–4000) |
| `AI_HISTORY_LIMIT` | Suhbat tarixidan yuboriladigan xabarlar soni (0–20) |

`.env` faylini GitHub'ga **hech qachon** yubormang — u `.gitignore` ichida.

### Admin ID'ni qanday topish mumkin

1. `ADMIN_IDS` bo'sh holda botni ishga tushiring.
2. Telegram'da botga `/id` yuboring — bot ID raqamingizni ko'rsatadi.
3. Shu raqamni `.env` dagi `ADMIN_IDS=` qatoriga yozing va botni qayta ishga tushiring.
4. Endi `/admin` buyrug'i va admin menyusi ishlaydi.

Agar `/admin` ni adminsiz yuborsangiz, bot ID'ingizni va sozlash yo'lini ko'rsatadi.

### AI Ustozni ulash (ixtiyoriy)

AI o'chirilgan holatda ham AI Ustoz ishlaydi — u dars bazasidan mos mavzuni topib,
qisqa javob va tegishli darsga havola beradi.

Haqiqiy AI javoblarini olish uchun:

```dotenv
AI_ENABLED=true
AI_API_KEY=sizning_kalitingiz
AI_MODEL=gpt-4o-mini
```

`AI_BASE_URL` ni OpenRouter, Groq yoki boshqa OpenAI-mos provayderga o'zgartirish
mumkin. Kalit faqat `.env` da saqlanadi va loglarga yozilmaydi.

## Botni ishga tushirish

```powershell
python bot.py
```

Kutilgan natija:

```text
INFO | database.db | Ma'lumotlar bazasi tayyor: ...\ustoz_ai.db
INFO | database.seed | Kontent yuklandi: 10 fan, 20 dars, 60 savol.
INFO | bot | UstozAI ishga tushdi: @ustoz_ai_2026_bot
```

To'xtatish: `Ctrl + C`.

Birinchi ishga tushishda avtomatik yaratiladi:

- `ustoz_ai.db` — 8 jadval bilan SQLite bazasi;
- `logs/bot.log` — xatolar jurnali;
- 10 fan, 20 dars va 60 savol bazaga yuklanadi.

## Telegram'da tekshirish

1. `/start` → ism → daraja → asosiy menyu.
2. **📚 Darslar** → fan → dars → matnni o'qing → **✅ Tugatdim**.
3. **📝 Testlar** → fan → 5 ta savolga javob bering → natija va foiz.
4. **📊 Mening natijalarim** → darslar, testlar, o'rtacha natija va streak.
5. **📅 Kunlik reja** → maqsadni tanlang (1/1, 2/2, 3/3) → bajarilish yangilanadi.
6. **⚙️ Sozlamalar** → darajani va bildirishnomalarni o'zgartiring.
7. **🧠 AI Ustoz** → savol yozing (2–1000 belgi) → javob oling → **⬅️ Chiqish**.
8. `/id` → ID raqamingiz. `/help` → buyruqlar ro'yxati.
9. Admin sifatida `/admin` → statistika va xabar yuborish.

Test paytida to'g'ri javob faqat test yakunlangandan keyin hisoblanadi; har bir
javobdan keyin to'g'riligi oshkor qilinmaydi.

## Admin panel

- `/admin` — foydalanuvchilar, bugungi faollik, testlar, darslar va AI so'rovlari
  statistikasi.
- **📢 Xabar yuborish** — matn (1–3000 belgi) → ko'rinishni tasdiqlash → yuborish.
  Bildirishnomalarni o'chirgan foydalanuvchilarga xabar yuborilmaydi.
- Yuborish davomida Telegram limiti (`retry after`) hisobga olinadi; yakunda
  yuborilgan va xato bo'lgan xabarlar soni ko'rsatiladi.
- `/cancel` yoki bekor qilish tugmasi bilan jarayondan chiqish mumkin.

## O'quv kontentini tahrirlash

Fanlar, darslar va savollar `content/seed_data.json` faylida saqlanadi. Format:

```json
{
  "subjects": [
    {
      "id": 1,
      "code": "english",
      "name": "Ingliz tili",
      "emoji": "🇬🇧",
      "description": "...",
      "lessons": [
        {
          "id": 101,
          "title": "Salomlashish",
          "content": "Dars matni...",
          "questions": [
            {
              "text": "Savol?",
              "options": ["A", "B", "C", "D"],
              "correct": 0,
              "explanation": "Izoh..."
            }
          ]
        }
      ]
    }
  ]
}
```

- Har bir savolda aynan 4 ta variant va `0`–`3` oralig'idagi `correct` bo'lishi shart.
- Savol ID'si avtomatik `dars_id * 10 + tartib` sifatida yaratiladi.
- JSON'ni tahrirlab, botni qayta ishga tushiring — kontent yangilanadi. JSON'dan
  olib tashlangan fan yoki dars faolsizlantiriladi, foydalanuvchi natijalari saqlanadi.
- JSON xato bo'lsa, bot aniq xato matni bilan ishga tushmaydi.

## Offline testlar

Botni Telegram'ga ulanmasdan tekshirish:

```powershell
python tests\test_offline.py
python tests\test_handlers_offline.py
```

- `test_offline.py` — baza, kontent, qidiruv, natijalar, streak, AI fallback,
  bildirishnomalar va admin statistikasi. Natija: `OFFLINE_TESTS_OK`.
- `test_handlers_offline.py` — to'liq handler oqimi: ro'yxatdan o'tish, dars, 5 savolli
  test, statistika, kunlik reja, sozlamalar, AI, `/id`, admin va xabar yuborish.
  Natija: `HANDLER_FLOW_OK`.

Testlar vaqtinchalik bazadan foydalanadi va haqiqiy `ustoz_ai.db` ga tegmaydi.

Boshqa foydali buyruqlar:

```powershell
python -m compileall -q .
Get-Content logs\bot.log -Tail 20
```

## Loyiha tuzilmasi

```text
ustoz_ai_bot/
├── bot.py                    # Kirish nuqtasi, routerlar, xatolar
├── config.py                 # .env'dan sozlamalar
├── time_utils.py             # UTC+5 vaqt, streak hisoblash
├── requirements.txt
├── .env.example
├── README.md
├── content/
│   └── seed_data.json        # 10 fan, 20 dars, 60 savol
├── database/
│   ├── db.py                 # 8 jadval sxemasi, ulanish
│   ├── seed.py               # Kontentni yuklash
│   ├── users.py              # Foydalanuvchilar
│   ├── content.py            # Fanlar, darslar, qidiruv
│   ├── progress.py           # Darslar, statistika, streak
│   ├── quizzes.py            # Test natijalari
│   ├── goals.py              # Kunlik maqsadlar
│   ├── chat.py               # AI suhbat tarixi va limitlar
│   └── admin.py              # Admin statistikasi va qabul qiluvchilar
├── handlers/
│   ├── start.py              # /start va ro'yxatdan o'tish
│   ├── ai_tutor.py           # AI Ustoz rejimi
│   ├── lessons.py            # Darslar
│   ├── quizzes.py            # Testlar
│   ├── progress.py           # Natijalar
│   ├── daily_plan.py         # Kunlik reja
│   ├── settings.py           # Sozlamalar
│   ├── admin.py              # Admin panel
│   ├── menu.py               # Menyu, /help, /id, noma'lum xabarlar
│   └── common.py             # Yordamchi funksiyalar
├── keyboards/
│   ├── main_menu.py          # Bosh menyu
│   └── inline_buttons.py     # Barcha inline tugmalar
├── services/
│   └── ai_service.py         # AI provayderi va lokal fallback
├── tests/
│   ├── test_offline.py
│   └── test_handlers_offline.py
└── logs/bot.log
```

### Ma'lumotlar bazasi jadvallari

`users`, `subjects`, `lessons`, `questions`, `quiz_results`, `study_progress`,
`chat_history`, `daily_goals` — jami 8 ta jadval.

## Tez-tez uchraydigan xatolar

| Xato | Sababi | Yechim |
| --- | --- | --- |
| `python` tanilmayapti | Python PATH'da emas | Python 3.13 ni qayta o'rnatib, "Add to PATH" ni belgilang |
| `Microsoft Visual C++ 14.0 is required` | `.venv` Python 3.15 bilan yaratilgan | `.venv` ni o'chirib, 3.13 bilan qayta yarating |
| `ModuleNotFoundError: aiogram` | venv faol emas | `.\.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt` |
| `BOT_TOKEN topilmadi` | `.env` yo'q | `Copy-Item .env.example .env` va tokenni yozing |
| `Unauthorized` | Token noto'g'ri yoki bekor qilingan | BotFather'dan yangi token oling |
| `Conflict: terminated by other getUpdates request` | Bot ikki joyda ishlayapti | Ikkinchi `bot.py` jarayonini to'xtating |
| `database is locked` | Boshqa jarayon bazani ushlab turibdi | Bitta bot nusxasi ishlashiga ishonch hosil qiling |
| AI javob bermayapti | Kalit yo'q yoki limit tugagan | `.env` dagi AI sozlamalarini tekshiring; limit ertaga yangilanadi |
| Admin panel ko'rinmayapti | `ADMIN_IDS` bo'sh yoki bot qayta ishga tushirilmagan | `/id` orqali ID oling, `.env` ga yozing, botni qayta ishga tushiring |

Batafsil ma'lumot: `logs/bot.log`.

## Xavfsizlik qoidalari

- Token va API kalitlarini faqat `.env` da saqlang.
- `.env`, baza va loglarni GitHub'ga yubormang — ular `.gitignore` da.
- Token oshkor bo'lsa, darhol BotFather'da `/revoke` qiling.
- Foydalanuvchi matni uzunligi tekshiriladi; HTML matn ekranlanadi.
- AI so'rovlarida timeout, kunlik limit va minimal tanaffus qo'llanadi.
- Test javoblari yakuniy natijagacha oshkor qilinmaydi.

## GitHub'ga joylash

```powershell
git init
git check-ignore -v .env
git add .
git status
```

`git status` ro'yxatida `.env`, `ustoz_ai.db`, `.venv` yoki `logs` ko'rinmasligi kerak.

```powershell
git commit -m "UstozAI: to'liq funksional Telegram ta'lim boti"
git branch -M main
git remote add origin https://github.com/USERNAME/ustoz_ai_bot.git
git push -u origin main
```

Agar token tasodifan commitga tushgan bo'lsa: avval BotFather'da tokenni bekor qiling,
keyin git tarixidan o'chiring. Faylni shunchaki o'chirish yetarli emas.
