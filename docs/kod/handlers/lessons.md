# `handlers/lessons.py` — darslar, rasmli kartochkalar va qidiruv

**Yo'l:** [`handlers/lessons.py`](../../../handlers/lessons.py)
**Vazifasi:** fanlar → darslar → rasmli dars kartochkasi → tugatish oqimi va `/qidiruv`.

## Asosiy oqim

1. `📚 Darslar` tugmasi fanlar ro'yxatini ochadi (`lesson:subjects`).
2. `lesson:subject:<id>` fan darslarini ko'rsatadi:
   - fan nomi katta harflarda;
   - `tugatilgan/jami` hisobi va progress bar;
   - tugatilgan darslar `✅` bilan belgilanadi.
3. `lesson:view:<id>` darsni **rasmli kartochka** sifatida ochadi va
   `mark_lesson_started()` chaqiradi.
4. `lesson:complete:<id>` darsni tugatadi:
   - `complete_lesson()` `True` qaytarsa, `increment_goal(lessons=1)`;
   - foto xabarning caption'i yangilanadi, `Darsni tugatdim` tugmasi olib tashlanadi;
   - allaqachon tugatilgan bo'lsa, ogohlantirish beriladi.
5. Kartochkadagi `📝 Test yechish` shu fan testini boshlaydi.

## Rasmli kartochka

### Matn tuzilishi

`build_lesson_card(lesson, completed=...)` quyidagi matnni yasaydi:

```text
🇬🇧 INGLIZ TILI · 1-DARS
━━━━━━━━━━━━━━
📖 Alifbo va tovushlar

<dars matni>

━━━━━━━━━━━━━━
💡 Maslahat: Matnni o'qib, «Darsni tugatdim» tugmasini bosing.
```

Tugatilganda oxirgi qator `✅ Tugatilgan. Natijangizda saqlandi.` bo'ladi.
Fan nomi, sarlavha va matn `html.escape()` qilinadi.

### Yuborish mantiqi

`_send_lesson_card()`:

1. `build_lesson_card()` bilan matn, `get_lesson_keyboard()` bilan tugmalar tayyorlanadi.
2. `get_lesson_photo(lesson_id)` orqali rasm olinadi (`services/lesson_media.py`).
3. Rasm yo'q **yoki** matn `LESSON_CAPTION_LIMIT` (1024) dan uzun bo'lsa:
   - `safe_edit()` bilan oddiy matnli xabar yuboriladi.
4. Joriy xabar foto bo'lsa:
   - `edit_caption()` bilan caption va tugmalar yangilanadi.
5. Aks holda eski xabar o'chiriladi va `answer_photo()` bilan yangi kartochka yuboriladi.
6. Yuborilgan rasmning `file_id` si keyingi ochishlar uchun keshlanadi.

Telegram xatosi bo'lsa, logga dars ID si yoziladi va matnli zaxira xabar yuboriladi.

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

## Rasmlar

Rasmlar `assets/lesson_images/lesson_<dars_id>.jpg` nomida saqlanadi. To'liq ro'yxat,
dizayn tizimi va rasm almashtirish yo'riqnomasi:
[`docs/DARS_DIZAYNI.md`](../../DARS_DIZAYNI.md).

## Xavfsizlik

Foydalanuvchi kiritgan qidiruv matni to'g'ridan-to'g'ri HTML'ga qo'yilmaydi; avval escape
qilinadi. SQL so'rov parametrlangan. Rasm nomi faqat dars ID siga bog'langan, foydalanuvchi
kiritgan yo'l ishlatilmaydi.
