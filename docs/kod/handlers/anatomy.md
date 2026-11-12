# `handlers/anatomy.py` — vaqtli Anatomiya testlari

**Yo'l:** [`handlers/anatomy.py`](../../../handlers/anatomy.py)
**Vazifasi:** Biologiya bo'limi ichida 546 savollik Anatomiya bankidan vaqt cheklangan
testlar o'tkazish, natijani saqlash va xatolarni tahlil qilish.

## Rejimlar

| Rejim | Savollar | Vaqt | Callback |
|---|---|---|---|
| ⚡ Tezkor | 10 | 5 daqiqa | `anatomy:start:10` |
| 🎯 Standart | 20 | 10 daqiqa | `anatomy:start:20` |
| 🏆 Marafon | 50 | 25 daqiqa | `anatomy:start:50` |

Doimiylar `keyboards/inline_buttons.py` da: `ANATOMY_MODES = {10: 300, 20: 600, 50: 1500}`
va `ANATOMY_MODE_LABELS`.

## Oqim

1. **📚 Darslar → Biologiya** ro'yxatida `anatomy:menu` tugmasi chiqadi.
2. `anatomy:menu` joriy xabarni o'chirib, `assets/anatomy_banner.png` rasmini caption va
   rejim tugmalari bilan yuboradi. Banner yuborilmasa, oddiy matnli xabar bilan zaxiralanadi.
3. `anatomy:start:<rejim>` `get_anatomy_questions(mode)` bilan tasodifiy savollarni oladi va
   FSM'ga yozadi: `question_ids`, `index`, `correct`, `answers`, `current_id`, `deadline`,
   `started_at`, `mode`, `chat_id`, `message_id`.
4. Savol ekranida vaqt hisoblagichi (`⏳ 04:46 qoldi`), progress bar, savol va A–D variantlari
   matnda ko'rsatiladi. Tugmalar faqat harf (A/B/C/D) va savol ID'sini yuboradi.
5. `anatomy:answer:<question_id>:<0-3>`:
   - `current_id` mosligi tekshiriladi — eski tugma ikkinchi marta ishlamaydi;
   - `deadline` o'tgan bo'lsa, test darhol `timed_out=True` bilan yakunlanadi;
   - javob `answers` ro'yxatiga yoziladi, `✅` yoki `❌` reaksiyasi qo'yiladi.
6. Oxirgi savoldan keyin `_finish()` chaqiriladi.

## Vaqt tugashi

`anatomy:start` har bir foydalanuvchi uchun `asyncio.create_task(_timeout_task(...))`
yaratadi. Vazifa deadline'gacha kutadi, keyin foydalanuvchi lock'ini olib, holat hali
o'sha ekanini tekshiradi va testni yakunlaydi.

- `_locks` — har bir foydalanuvchi uchun `asyncio.Lock`; kechikkan javob va taymer bir
  vaqtda yakunlay olmaydi.
- `_timers` — joriy taymer vazifasi; yangi test boshlanganda eskisi bekor qilinadi.
- `_cancel_timer()` joriy vazifani o'zini bekor qilmaydi (`asyncio.current_task()` tekshiruvi).
- Vaqt tugaganda faqat javob berilgan savollar baholanadi. Birorta javob bo'lmasa, natija
  saqlanmaydi va "Vaqt tugadi" xabari chiqadi.

## Natija

`_finish()`:

1. `state.clear()` — holat darhol bo'shatiladi.
2. `get_subject_best_score()` bilan oldingi rekord olinadi.
3. `save_quiz_result()` natijani yashirin `ANATOMY_SUBJECT_ID = 900` faniga yozadi.
4. XP: `XP_QUIZ_BASE + to'g'ri × XP_QUIZ_PER_CORRECT`; to'liq yakunlangan va 100% natijada
   qo'shimcha `XP_PERFECT_BONUS`.
5. `increment_goal(quizzes=1)` kunlik rejani oshiradi; maqsad bajarilsa `XP_GOAL_BONUS`.
6. Natija ekrani tahrirlanadi: foiz, progress bar, sarflangan vaqt, rekord va XP.
7. Yangi daraja/yutuq bo'lsa `reward_notice()` alohida xabar yuboriladi.
8. Xato javoblar bo'lsa `_review_text()` birinchi 8 tasini ko'rsatadi (qolganlari soni bilan).

## Dizayn qarorlari

- Vaqt chegarasi `time.time()` bilan hisoblanadi, shuning uchun bot qayta ishga tushsa ham
  qolgan vaqt to'g'ri ko'rinadi (FSM `MemoryStorage` da saqlanadi).
- Callback ma'lumotida to'g'ri javob yo'q — faqat savol ID'si va variant indeksi.
- Savol/izoh matnlari `html.escape()` qilinadi; uzun matnlar `_short()` bilan qisqartiriladi.
- `anatomy:answer:` uchun zaxira handler eski tugma bosilganda "Bu test yakunlangan"
  ogohlantirishini qaytaradi.

## Bog'liq fayllar

- [`database/anatomy.py`](../database/anatomy.md) — savollar banki
- [`keyboards/inline_buttons.py`](../keyboards/inline_buttons.md) — rejim va variant tugmalari
- [`handlers/lessons.py`](lessons.md) — Biologiya ro'yxatidagi kirish tugmasi
