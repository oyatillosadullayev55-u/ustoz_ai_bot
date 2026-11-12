# UstozAI — yangilanishlar tarixi

Bu hujjat loyihaga qo'shilgan imkoniyatlar, ularni qanday ishlatish va tekshiruv
natijalarini jamlaydi. Eng so'nggi o'zgarishlar hujjat oxiridagi
**2026-11-12** bo'limida.

## 2026-10-31 yangilanishi

**Commit:** `176b6d3` — *feat: gamifikatsiya, sevimlilar, zaxira va test UX yaxshilandi*

## Qisqa mazmun

| Yo'nalish | Natija |
| --- | --- |
| Gamifikatsiya | XP, 6 daraja, 12 yutuq, haftalik TOP-10 reyting |
| Sevimlilar | Darslarni yulduzcha bilan saqlash va «Sevimlilarim» ekrani |
| Fan progressi | Har bir fan tugmasida tugatilgan/jami dars soni va umumiy progress |
| Test UX | Fan bo'yicha eng yaxshi natija, rekord xabari, XP mukofoti |
| AI UX | Javob ostida mavzuga mos 2 tagacha dars havolasi |
| Zaxira | Admin uchun `/backup` va `/export` (CSV) |
| Baza | 3 ta yangi jadval, `users.xp` ustuni, idempotent migratsiya |

## 1. Gamifikatsiya

XP har bir foydalanuvchi uchun `users.xp` da saqlanadi, har bir harakat esa
`xp_log` jurnaliga yoziladi. Bir martalik mukofotlar `once_key` bilan himoyalangan,
shuning uchun sahifani qayta ochish XP ni ikki marta qo'shmaydi.

| Hodisa | XP |
| --- | --- |
| Dars tugatish | +20 |
| Test yakuni | 5 + 2 × to'g'ri javob |
| 100% natija bonusi | +10 |
| Kunlik maqsad bajarildi | +15 |
| Yangi yutuq | +15 |
| AI Ustozga savol | +1 |

### Darajalar

| Emoji | Daraja | Minimal XP |
| --- | --- | --- |
| 🌱 | Yangi boshlovchi | 0 |
| 📗 | O'quvchi | 100 |
| 📘 | Bilimdon | 300 |
| 🎓 | Tajribali | 700 |
| 🏅 | Ustoz | 1500 |
| 👑 | Afsona | 3000 |

### Yutuqlar (12 ta)

Birinchi qadam, Izlanuvchi (5 dars), Bilimdon (15 dars), Marafon (35 dars),
Birinchi sinov, Test ustasi (10 test), Mukammal natija (100%), Uch kun (streak 3),
Bir hafta (streak 7), Kolleksioner (5 sevimli), AI hamkor (10 savol), Maqsadli
(5 kunlik maqsad).

Yangi yutuq ochilganda bot darhol tabriklaydi va `+15 XP` beradi.

### Haftalik reyting

So'nggi 7 kunda to'plangan XP bo'yicha TOP-10 ko'rsatiladi. Ishlatilgan ismlar
maxfiylik uchun qisqartiriladi, joriy foydalanuvchining o'rni alohida chiqadi.

**Qayerda ko'rinadi:** «📊 Mening natijalarim» → daraja va XP yuqorida,
«🏆 Yutuqlarim» va «📈 Haftalik reyting» tugmalari ostida.

## 2. Sevimlilar va fan progressi

- Fanlar ro'yxatida umumiy progress va har bir fan tugmasida `tugatilgan/jami`
  ko'rsatiladi (masalan `2/5`).
- Dars kartochkasidagi **⭐ Sevimlilarga qo'shish** tugmasi darsni saqlaydi yoki
  olib tashlaydi. Holat kartochka qayta chizilganda ko'rinadi.
- «📊 Mening natijalarim → ⭐ Sevimlilarim» saqlangan darslarni ro'yxat qiladi;
  tugma bosilsa, dars darhol ochiladi.

## 3. Test va AI UX

- Test yakunida fan bo'yicha oldingi eng yaxshi natija bilan solishtiriladi;
  rekord yangilansa, alohida nishonlanadi.
- Natija ekranida olingan XP ko'rsatiladi.
- AI Ustoz javobi ostida mavzuga mos 2 tagacha dars tugmasi chiqadi va darsni
  darhol ochish mumkin.
- AI javoblari HTML sifatida xavfsiz ekranlanadi; uzun javob qisqartiriladi.

## 4. Zaxira va CSV eksport

### `/backup`

Admin uchun. Bot SQLite `backup()` API orqali izchil nusxa yaratadi (WAL rejimida
ham), `.db` fayl sifatida Telegram'ga yuboradi. So'nggi 5 ta nusxa `BACKUP_DIR`
papkasida qoladi, eskilari o'chiriladi.

### `/export`

Admin uchun. Foydalanuvchilar jadvalini `utf-8-sig` CSV qilib yuboradi: ism, XP,
tugatilgan darslar, testlar, o'rtacha va eng yaxshi natija. Fayl Excel yoki Google
Sheets'da ochiladi va yuborilgach serverdan o'chiriladi.

### Tiklash

1. Botni to'xtating.
2. Zaxira `.db` faylini `.env` dagi `DATABASE_PATH` manziliga qo'ying.
3. Botni qayta ishga tushiring.

Zaxira faylida shaxsiy ma'lumot bor — uni ochiq joyda saqlamang.

### Render bepul tarifi

Bepul tarifda doimiy disk yo'q. Variantlar:

- muntazam `/backup` olib, faylni kompyuterda saqlash;
- Render persistent disk ulash: `DATABASE_PATH=/var/data/ustoz_ai.db`,
  `BACKUP_DIR=/var/data/backups`;
- Oracle Cloud Always Free + `docker compose` ga o'tish.

Batafsil: [SERVERGA_JOYLASH.md](SERVERGA_JOYLASH.md), 1.4.1-bo'lim.

## 5. Ma'lumotlar bazasi

Yangi jadvallar:

| Jadval | Vazifasi |
| --- | --- |
| `xp_log` | XP jurnali; `once_key` qismiy unikal indeks bilan |
| `achievements` | Ochilgan yutuqlar (PK: user_id, code) |
| `favorites` | Sevimli darslar (PK: user_id, lesson_id) |

`users` jadvaliga `xp` ustuni qo'shildi. Sxema idempotent: `CREATE TABLE IF NOT
EXISTS`, eski bazaga ustun `ALTER TABLE` bilan qo'shiladi. Foydalanuvchi
o'chirilsa, XP, yutuqlar va sevimlilar ham kaskad bilan o'chadi.

## 6. Tekshiruv natijalari

| Tekshiruv | Natija |
| --- | --- |
| `ruff check .` | All checks passed |
| `tests/test_offline.py` | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | `HANDLER_FLOW_OK` |

Testlar vaqtinchalik bazadan foydalanadi; zaxira fayllari ham vaqtinchalik
papkaga yoziladi va testdan keyin o'chiriladi.

## 7. Ishga tushirish holati

- Kod GitHub `main` branch'ga yuklangan: `176b6d3`.
- Render avtomatik deploy qiladi; `/health` manzili yangi commit bilan
  `{"status": "ok"}` qaytaradi.
- Telegramda bot: `@ustoz_ai_2026_bot`.
- **Lokal `python bot.py` ni Render ishlab turganda ishga tushirmang** — Telegram
  polling rejimida bitta nusxa ishlashi kerak, aks holda
  `Conflict: terminated by other getUpdates request` xatosi chiqadi.

### Yangi environment o'zgaruvchisi

| Kalit | Ma'nosi | Standart |
| --- | --- | --- |
| `BACKUP_DIR` | Zaxira va CSV fayllari papkasi | `backups/` |

## 8. Keyingi qadamlar

- Doimiy baza (Render persistent disk yoki PostgreSQL) ga o'tish.
- Yutuqlar va reyting uchun qo'shimcha filtrlash.
- Test natijalari bo'yicha mavzular kesimida tahlil.
- Qidiruvni FTS bilan tezlashtirish.

---

## 2026-11-01 — Kunlik sovg'a, savol va missiyalar

Bu yangilanish foydalanuvchini har kuni botga qaytib kelishga undaydigan uchta
bo'limni qo'shadi. Barcha mukofotlar mavjud XP, daraja va yutuq tizimiga ulanadi.

### Qisqa mazmun

| Yo'nalish | Natija |
| --- | --- |
| 🎁 Kunlik sovg'a | Kuniga bir marta 5–25 XP va sovg'a seriyasi |
| ❓ Kunlik savol | Har kuni bitta savol, izoh, dars havolasi, +10/+2 XP |
| 🎯 Missiyalar | Haftalik 3 dars / 2 test / 3 AI savoli, +30/+25/+20 XP |
| Menyu | Uchta yangi reply tugma |
| Baza | Yangi `daily_answers` jadvali (jami 12 ta jadval) |

### 🎁 Kunlik sovg'a

- **🎁 Sovg'a** tugmasi bosilganda `secrets.randbelow` bilan 5–25 XP orasida
  tasodifiy miqdor tanlanadi.
- Mukofot `xp_log` ga `reason='gift'`, `once_key='gift:<sana>'` bilan yoziladi;
  qayta bosilsa XP qo'shilmaydi.
- Xabarda sovg'a seriyasi ko'rsatiladi. Seriya 3 kunga yetsa, qo'shimcha rag'bat
  matni chiqadi.

### ❓ Kunlik savol

- Savol `zlib.crc32(sana) % savollar_soni` orqali tanlanadi, shuning uchun kun
  davomida barcha foydalanuvchilar bir xil savolni ko'radi.
- Javob `daily_answers` jadvaliga yoziladi; `PRIMARY KEY (user_id, answer_date)`
  va `ON CONFLICT DO NOTHING` takroriy javobni to'sadi.
- To'g'ri javob `+10 XP`, xato javob `+2 XP` beradi. Natijada tanlangan va to'g'ri
  variant, izoh, kunlik seriya va **📖 Darsni ochish** tugmasi chiqadi.
- Savol ID'si `question_id` sifatida saqlanadi, lekin tashqi kalit qo'yilmagan:
  bot har ishga tushganda savollarni qayta yozadi va cascade tarixni o'chirardi.

### 🎯 Haftalik missiyalar

| Kod | Missiya | Maqsad | Mukofot |
| --- | --- | --- | --- |
| `lessons_3` | 📚 3 ta darsni tugatish | 3 | +30 XP |
| `quizzes_2` | 📝 2 ta test yechish | 2 | +25 XP |
| `ai_3` | 🤖 3 ta AI savol berish | 3 | +20 XP |

- Faollik dushanba (UTC+5) boshidan `study_progress`, `quiz_results` va
  `chat_history` bo'yicha hisoblanadi.
- Progress `min(faollik, maqsad)` ko'rinishida bar bilan chiqadi.
- Bajarilgan missiya uchun **🎁 … XP olish** tugmasi paydo bo'ladi; mukofot
  `once_key='mission:<kod>:<hafta>'` bilan haftada bir marta olinadi.
- Har dushanba missiyalar avtomatik yangilanadi, alohida sozlash kerak emas.

### Menyu va fayllar

- Bosh menyuga **🎁 Sovg'a**, **❓ Kunlik savol** va **🎯 Missiyalar** tugmalari
  qo'shildi.
- Yangi fayllar: `database/daily.py`, `services/daily.py`, `handlers/daily.py`.
- `handlers/__init__.py` va `bot.py` routerlar ro'yxatiga `daily` qo'shildi
  (`gamification → daily → daily_plan`).
- `tests/test_offline.py` va `tests/test_handlers_offline.py` yangi oqimlarni
  qamrab oladi.

### Environment

Yangi environment o'zgaruvchisi kerak emas. Barcha hisoblar UTC+5 bo'yicha
`time_utils` orqali amalga oshiriladi.

### Tekshiruv natijalari

| Tekshiruv | Natija |
| --- | --- |
| `ruff check .` | All checks passed |
| `tests/test_offline.py` | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | `HANDLER_FLOW_OK` |

### Deploy holati

- O'zgarishlar GitHub `main` branch'iga yuklanadi va Render avtomatik deploy qiladi.
- Deploydan keyin `/health` manzili `{"status": "ok"}` qaytarishi kerak.
- **Lokal `python bot.py` ni Render ishlab turganda ishga tushirmang** — polling
  rejimida bitta nusxa ishlashi kerak.

## 2026-11-12 — Barqarorlik va kod sifati

Funksiya qo'shilmadi: mavjud oqimlardagi real xatolar tuzatildi va testlar
kengaytirildi.

### Tuzatilgan xatolar

| Muammo | Yechim |
| --- | --- |
| O'zgarmagan xabar tahrirlanganda Telegram `message is not modified` qaytarib, bot dublikat xabar yuborardi | `is_not_modified_error()` qo'shildi; `safe_edit()` va foto caption yo'li jim qaytadi |
| Admin panelida **💾 Baza zaxirasi** va **📤 CSV eksport** alohida qatorlarga sochilib ketardi | `get_admin_keyboard()` da `adjust()` `row()` dan oldin chaqiriladi |
| Bir vaqtda bosilgan «Darsni tugatdim» kunlik reja va XP ni ikki marta sanashi mumkin edi | `complete_lesson()` shartli upsert bilan atomar qilindi |
| Sovg'a yoki missiya ikki marta bosilganda XP yozilmasa ham handler muvaffaqiyat ko'rsatardi | `RewardResult.awarded` qo'shildi, handlerlar «allaqachon oldingiz» xabarini beradi |
| Har AI so'rovida yangi `aiohttp` sessiyasi ochilib, TLS handshake takrorlanardi | Sessiya modul darajasida qayta ishlatiladi, `bot.py` yopilishda tozalaydi |
| AI provayderi ishlamasa har savolda qayta urinish davom etardi | `ProviderGuard`: 3 xatodan keyin 120 soniya cooldown |
| Kunlik reja ekrani maqsadni ikki marta o'qirdi | `_build_plan_text(user, goal)` tayyor qatorni qabul qiladi |

### Baza

`get_connection()` har ulanishda `synchronous=NORMAL` va `cache_size=-8000`
o'rnatadi. WAL rejimida bu xavfsiz va yozishni tezlashtiradi.

### Testlar

`tests/test_offline.py` ga qo'shildi:

- `is_not_modified_error()` ijobiy va salbiy holati;
- `ProviderGuard` bloklash/ochish o'tishlari;
- admin va dars klaviaturalari qatorlarining saqlanishi;
- takroriy mukofotda `awarded=False`, `xp_gained=0`;
- `asyncio.gather` bilan bir vaqtda tugatilgan darsdan faqat bittasi `True`.

### Tekshiruv natijalari

| Tekshiruv | Natija |
| --- | --- |
| `ruff check .` | All checks passed |
| `tests/test_offline.py` | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | `HANDLER_FLOW_OK` |

### Deploy holati

O'zgarishlar lokal commit qilindi. GitHub'ga push qilish va Render deploy alohida
tasdiq bilan bajariladi. **Lokal `python bot.py` ni Render ishlab turganda ishga
tushirmang** — polling rejimida bitta nusxa ishlashi kerak.

## 2026-11-12 — Anatomiya vaqtli testlari

**Nima qo'shildi:** **📚 Darslar → Biologiya** ichida `🫀 Anatomiya testlari · ⏱ vaqtli`
bo'limi. `ANATOMIYA_549_test.html` faylidagi testlar 546 ta takrorlanmagan savolga
keltirildi va uch vaqtli rejimda ishlaydi.

| Rejim | Savollar | Vaqt |
| --- | --- | --- |
| ⚡ Tezkor | 10 | 5 daqiqa |
| 🎯 Standart | 20 | 10 daqiqa |
| 🏆 Marafon | 50 | 25 daqiqa |

### Dizayn

- Menyu `assets/anatomy_banner.png` rasmli kartochka bilan ochiladi.
- Savol ekranida `⏳ 04:46 qoldi` hisoblagichi va `▓▓▓░░░░░░░` progress bar.
- Variantlar matnda **A)–D)** qatorlari sifatida, tugmalarda faqat harflar — uzun
  variantlar ham tugma limitiga sig'adi.
- Javobda `✅`/`❌` reaksiyasi, yakunda natijaga mos `🏆`/`👏`/`👍`/`💪`.
- Natija ekranida foiz, progress bar, sarflangan vaqt, rekord va XP.

### Vaqt chegarasi

- Har bir test uchun fon vazifasi deadline'gacha kutadi va testni yakunlaydi.
- Foydalanuvchi lock'i tufayli kechikkan javob va taymer bir vaqtda yakunlay olmaydi.
- Vaqt tugasa faqat javob berilgan savollar baholanadi; birorta javob bo'lmasa,
  natija saqlanmaydi.
- Eski savol tugmasi bosilsa, "Bu test yakunlangan" ogohlantirishi qaytadi.

### Baza va natijalar

- Yangi `anatomy_questions` jadvali (546 savol, 4 variant, 0–3 indeks).
- Natijalar `quiz_results.subject_id = 900` yashirin `Anatomiya` faniga yoziladi;
  fanlar ro'yxatida ko'rinmaydi, lekin **📊 Mening natijalarim**da chiqadi.
- XP: `5 + 2 × to'g'ri javob`; to'liq 100% natija uchun `+10`; kunlik rejaga +1 test.

### Tekshiruv natijalari

| Tekshiruv | Natija |
| --- | --- |
| `ruff check .` | All checks passed |
| `tests/test_offline.py` | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | `HANDLER_FLOW_OK` |

### Deploy holati

O'zgarishlar faqat lokal commit qilinadi. Push va Render deploy alohida tasdiq bilan
bajariladi; Render xizmati va tokenlar o'zgartirilmaydi.

### Tuzatish — faol testda javob qabul qilinmasligi

**Muammo:** savol ekranida (masalan, `4/20`, taymer `09:55`) A–D tugmasi bosilganda
«Bu test yakunlangan. Yangi rejim tanlang: /start → 📚 Darslar.» ogohlantirishi chiqardi.

**Sabab:** faol test faqat `FSMContext` (`MemoryStorage`) da saqlanardi, javob handleri esa
`AnatomyStates.answering` holatiga bog'langan edi. Foydalanuvchi test paytida boshqa
bo'limga o'tsa (`/menu`, `🏠 Bosh menyu`, darslar, testlar — barchasi `state.clear()`
chaqiradi) yoki bot qayta ishga tushsa, holat yo'qolib, savol tugmalari ishlamay qolardi.

**Yechim:**

- faol test endi xotiradagi `_sessions` va `anatomy_sessions` jadvalida saqlanadi;
- `anatomy:answer:` FSM holatiga bog'lanmagan — sessiyani xotiradan, bo'lmasa bazadan oladi;
- taymer yo'qolgan bo'lsa, javob kelganda qayta ishga tushadi;
- sessiya chindan yo'q bo'lsagina «test yakunlangan yoki bekor qilingan» ogohlantirishi
  qaytadi;
- `anatomy:menu` yangi menyuni ochganda joriy sessiya ongli ravishda bekor qilinadi.

**Testlar:** `test_offline.py` — sessiyani saqlash/tiklash/o'chirish; `test_handlers_offline.py`
— `menu:home` bilan FSM tozalangach va xotiradagi sessiya bo'shatilgach ham javob qabul
qilinishi, bekor qilingan test natija sifatida saqlanmasligi.
