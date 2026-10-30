# `handlers/lessons.py` — darslar, rasmli kartochkalar, batafsil ekran va qidiruv

**Yo'l:** [`handlers/lessons.py`](../../../handlers/lessons.py)
**Vazifasi:** fanlar → darslar → qisqa kartochka → batafsil matn → tugatish oqimi va
`/qidiruv`.

## Asosiy oqim

1. `📚 Darslar` tugmasi fanlar ro'yxatini ochadi (`lesson:subjects`).
2. `lesson:subject:<id>` fan darslarini ko'rsatadi:
   - fan nomi katta harflarda;
   - `tugatilgan/jami` hisobi va progress bar;
   - darslarning davomiylik oralig'i;
   - tugatilgan darslar `✅` bilan belgilanadi.
3. `lesson:view:<id>` darsni **qisqa rasmli kartochka** sifatida ochadi va
   `mark_lesson_started()` chaqiradi.
4. `lesson:read:<id>` **batafsil ekran**ni ochadi: to'liq matn, maqsad, misol, mini
   mashq va xulosa.
5. `lesson:complete:<id>` darsni tugatadi:
   - `complete_lesson()` `True` qaytarsa, `increment_goal(lessons=1)`;
   - joriy ekran (kartochka yoki batafsil matn) yangilanadi va `Darsni tugatdim`
     tugmasi olib tashlanadi;
   - allaqachon tugatilgan bo'lsa, ogohlantirish beriladi.
6. Kartochkadagi `📝 Test yechish` shu fan testini boshlaydi.
7. `🧠 AI Ustozga so'rash` (`lesson:ask:<id>`) darsni AI rejimiga kontekst sifatida
   uzatadi — handler `handlers/ai_tutor.py` da.

## Kartochka va batafsil ekran

### `build_lesson_card()`

```text
🇬🇧 INGLIZ TILI · 1-DARS
━━━━━━━━━━━━━━
📖 Alifbo va tovushlar

🎯 <summary>

🔑 Asosiy fikrlar
• ...
• ...
• ...

⏱️ 7 daqiqa · 🟢 Boshlang'ich
━━━━━━━━━━━━━━
💡 Maslahat: «Batafsil o'qish» bilan mavzuni chuqurroq o'rganing.
```

- `summary` bo'sh bo'lsa, `content` ning birinchi 220 belgisi olinadi.
- `key_points` — JSON ro'yxat; ko'pi bilan 4 tasi ko'rsatiladi.
- Tugatilganda holat qatori `✅ Tugatilgan. Natijangizda saqlandi.` bo'ladi.
- Fan nomi, sarlavha, mazmun va fikrlar `html.escape()` qilinadi.

### `build_lesson_details()`

Sarlavha, fan, davomiylik va daraja bilan boshlanadi, keyin to'liq `content`,
so'ngra holat va maslahat. Matn `LESSON_TEXT_LIMIT = 4000` belgiga sig'masa, oxiri
`…` bilan qisqartiriladi. Barcha matn escape qilinadi.

### Yuborish mantiqi

`_send_lesson_card()`:

1. Matn, `get_lesson_keyboard()` va oldingi/keyingi dars ID'lari tayyorlanadi.
2. `get_lesson_photo(lesson_id)` orqali rasm olinadi (`services/lesson_media.py`).
3. Rasm yo'q **yoki** matn `LESSON_CAPTION_LIMIT` (1024) dan uzun bo'lsa:
   - `safe_edit()` bilan oddiy matnli xabar yuboriladi.
4. Joriy xabar foto bo'lsa:
   - `edit_caption()` bilan caption va tugmalar yangilanadi.
5. Aks holda eski xabar o'chiriladi va `answer_photo()` bilan yangi kartochka yuboriladi.
6. Yuborilgan rasmning `file_id` si keyingi ochishlar uchun keshlanadi.

Telegram xatosi bo'lsa, logga dars ID si yoziladi va matnli zaxira xabar yuboriladi.

`_send_lesson_details()` xuddi shu rasmni saqlamaydi: `safe_edit()` orqali joriy
xabarni matnga almashtiradi yoki foto xabarni o'chirib, yangi matn yuboradi.

### Navigatsiya va ekran holati

- `_adjacent_lesson_ids(lesson)` shu fan ichidagi qo'shnilarni topadi.
- `_lesson_nav_row()` faqat mavjud qo'shnilar uchun tugma chiqaradi.
- `_is_details_view(message)` tugma matni `🖼️ Kartochkaga qaytish` bo'lsa, joriy ekran
  batafsil hisoblanadi. Shu sababli tugatishdan keyin foydalanuvchi o'qiyotgan ekran
  saqlanadi.

## `/qidiruv` buyrug'i

```text
/qidiruv fotosintez
/search fotosintez
```

- So'rov 2–100 belgi orasida bo'lishi kerak.
- `search_lessons(query, limit=5)` sarlavha va matn bo'yicha qidiradi.
- Natija topilmasa, bosh menyu bilan maslahat xabari yuboriladi.
- Natijalar `lesson:view:<id>` tugmalari bilan chiqadi; dars ochilganda rasmli kartochka
  ko'rsatiladi.
- So'rov va dars nomlari HTML uchun `html.escape` qilinadi.

## Doimiylar

| Doimiylik | Qiymat |
|---|---|
| `SEARCH_MIN_LENGTH` | 2 |
| `SEARCH_MAX_LENGTH` | 100 |
| `SEARCH_RESULTS_LIMIT` | 5 |
| `LESSON_CAPTION_LIMIT` | 1024 |
| `LESSON_TEXT_LIMIT` | 4000 |
| `LESSON_LEVEL_LABELS` | `beginner`, `intermediate`, `advanced` → o'zbekcha yorliq |

## Rasmlar

Rasmlar `assets/lesson_images/lesson_<dars_id>.jpg` nomida saqlanadi. To'liq ro'yxat,
dizayn tizimi va rasm almashtirish yo'riqnomasi:
[`docs/DARS_DIZAYNI.md`](../../DARS_DIZAYNI.md).

## Xavfsizlik

Foydalanuvchi kiritgan qidiruv matni to'g'ridan-to'g'ri HTML'ga qo'yilmaydi; avval escape
qilinadi. SQL so'rov parametrlangan. Rasm nomi faqat dars ID siga bog'langan, foydalanuvchi
kiritgan yo'l ishlatilmaydi. Callback'dan kelgan dars ID si butun songa aylantiriladi va
bazadan qayta tekshiriladi.

## Harakat effektlari

- `Darslar` tugmasi bosilganda `send_action(TYPING)` yuboriladi.
- Rasmli kartochka yuborilishidan oldin `send_action(UPLOAD_PHOTO)` — «rasm yuklanmoqda».
- Dars ochilganda `📖`, batafsil matnda `📘`, dars tugatilganda `🎉` reaksiyalari
  `handlers.common.react()` orqali qo'yiladi.
- Kartochka va batafsil ekranda tashqi havola tugmasi yo'q: barcha material bot ichida.

