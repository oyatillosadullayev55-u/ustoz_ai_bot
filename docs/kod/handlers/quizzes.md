# `handlers/quizzes.py` — testlar oqimi

**Yo'l:** [`handlers/quizzes.py`](../../../handlers/quizzes.py)
**Vazifasi:** 5 savollik test o'tkazish, natijani saqlash va xato javoblarni tahlil qilish.

## Doimiylar va holat

- `QUIZ_SIZE = 5` — har bir testdagi savollar soni.
- `OPTION_FIELDS` — `option_a` … `option_d` ustunlari.
- `QuizStates.answering` — test davom etayotgan holat.
- `_locks` — har bir foydalanuvchi uchun `asyncio.Lock`; tez ikki marta bosishdan himoya.

FSM ma'lumotlari: `subject_id`, `subject_name`, `subject_emoji`, `question_ids`, `index`, `correct`, `answers`, `current_id`.

## Oqim

1. `📝 Testlar` → fanlar ro'yxati.
2. `quiz:subject:<id>` → `get_quiz_questions()` bilan 5 ta tasodifiy savol olinadi.
3. `quiz:answer:<question_id>:<0-3>` → javob qabul qilinadi:
   - `current_id` mosligi tekshiriladi (eski tugma ikki marta ishlamaydi);
   - variant 0–3 oralig'ida bo'lishi tekshiriladi;
   - foydalanuvchi tanlovi `answers` ro'yxatiga yoziladi.
4. Oxirgi savoldan keyin:
   - `save_quiz_result()` natijani saqlaydi;
   - `increment_goal(quizzes=1)` kunlik rejani oshiradi;
   - `state.clear()` holatni tozalaydi;
   - natija ekrani tahrirlanadi;
   - xato javoblar bo'lsa, alohida "Xatolar tahlili" xabari yuboriladi.
5. Barcha javoblar to'g'ri bo'lsa, natija ekranida "Barcha javoblar to'g'ri" yoziladi.

## Xatolar tahlili

`get_questions_by_ids()` barcha savollarni bitta so'rovda oladi. Faqat xato javoblar ko'rsatiladi:

- savol matni (160 belgigacha);
- foydalanuvchi tanlagan variant;
- to'g'ri variant;
- izoh (180 belgigacha).

Matnlar `html.escape` qilinadi, uzun qiymatlar `_short()` bilan qisqartiriladi. Bu Telegram'ning 4096 belgi limitidan oshib ketmaslik uchun kerak.

## Xavfsizlik

- To'g'ri javob callback ma'lumotida yoki tugma matnida yo'q — faqat savol ID'si va variant indeksi.
- `correct_option` faqat javob qabul qilingandan keyin bazadan o'qiladi.
- Foydalanuvchi matni emas, balki bazadagi savol matni chiqariladi; baribir HTML escape qo'llanadi.

## Harakat effektlari

- Test boshlanganda `🚀`, har bir javobda `✅` yoki `❌` reaksiyasi qo'yiladi.
- Yakunda natijaga qarab `🏆` (≥90%), `👏` (≥70%), `👍` (≥50%), `💪` — `_result_reaction()`.

