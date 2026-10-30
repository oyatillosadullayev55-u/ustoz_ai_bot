# `handlers/ai_tutor.py` — AI Ustoz rejimi

**Yo'l:** [`handlers/ai_tutor.py`](../../../handlers/ai_tutor.py)
**Vazifasi:** foydalanuvchi savollariga AI yoki mahalliy dars bazasi orqali javob berish,
shu jumladan dars kontekstida tushuntirish.

## FSM

`AITutorStates.chatting` — AI rejimi faol. Chiqish uchun `⬅️ Chiqish` tugmasi yoki asosiy menyu tugmasi bosiladi.

Darsdan `lesson:ask:<id>` orqali kirilganda FSM ma'lumotiga qo'shimcha `lesson_context`
lug'ati yoziladi:

```python
{
    "lesson_id": 501,
    "subject": "🧬 Biologiya",
    "title": "Hujayra tuzilishi",
    "summary": "...",
    "content": "...",
}
```

`lesson_context` faqat joriy suhbat uchun xotirada turadi va bazaga yozilmaydi.

## Cheklovlar

| Doimiylik | Qiymat | Ma'nosi |
|---|---|---|
| `MAX_QUESTION_LENGTH` | 1000 | Bitta savolning maksimal uzunligi |
| `MAX_REPLY_LENGTH` | 3900 | Telegram xabar limitidan xavfsiz chegara |
| `AI_DAILY_LIMIT` | `.env` | Kunlik savollar soni |
| `AI_MIN_INTERVAL` | `.env` | Savollar orasidagi minimal tanaffus |
| `AI_HISTORY_LIMIT` | `.env` | Kontekstga qo'shiladigan oxirgi xabarlar |

## Oqim

1. `🧠 AI Ustoz` bosilganda rejim holati yoqiladi va AI holati, limit va tanaffus
   haqida ma'lumot beriladi.
2. Kartochka yoki batafsil ekrandagi `🧠 AI Ustozga so'rash` bosilganda
   `ask_about_lesson()`:
   - darsni bazadan oladi;
   - FSM'ni tozalab, `chatting` holatini o'rnatadi;
   - `lesson_context` ni saqlaydi;
   - misol savollar bilan ko'rsatma yuboradi.
3. Savol kelganda:
   - uzunlik 2–1000 belgi orasida tekshiriladi;
   - `get_ai_usage()` orqali kunlik limit va oxirgi savol vaqti tekshiriladi;
   - `get_history()` bilan kontekst olinadi;
   - FSM'dan `lesson_context` olinadi;
   - foydalanuvchi xabari bazaga yoziladi.
4. `send_chat_action(TYPING)` yuboriladi (xatolik bo'lsa faqat debug log).
5. `ask_tutor(..., lesson_context)` chaqiriladi. Natija `(javob, manba)`:
   - `ai` — provayder javobi, `html.escape` qilinadi;
   - `lessons` — dars bazasidan yoki dars kontekstidan tayyor HTML javob;
   - `plain` — kutilmagan xatolik uchun oddiy matn.
6. Javob bazaga 4000 belgigacha saqlanadi va foydalanuvchiga yuboriladi.

## Xatoliklarni boshqarish

- AI provayderi xatosi `services/ai_service.py` ichida ushlanadi va dars bazasiga o'tadi.
- Kutilmagan xatolik bo'lsa, foydalanuvchiga "hozir javob bera olmadim" xabari yuboriladi, to'liq traceback logga yoziladi.
- AI kaliti yoki tokeni logga chiqarilmaydi.

## Muhim jihatlar

- AI javobi HTML sifatida escape qilinadi, shuning uchun model yuborgan teglar bajarilmaydi.
- Javob uzunligi `_truncate()` bilan cheklanadi; so'z o'rtasidan kesilmaslikka harakat qilinadi.
- Dars matni provayderga faqat birinchi 2500 belgi bilan uzatiladi.
- Dars mavzusi tashqarisidagi savol ham qabul qilinadi; model dars kontekstini faqat
  yordamchi ma'lumot sifatida oladi.
- Rejimdan chiqishda `state.clear()` chaqiriladi, shu bilan `lesson_context` ham
  tozalanadi.
- Eski `lesson_context` yangi dars tanlanganda yoki AI rejimidan chiqilganda qolib
  ketmaydi.

## Harakat effekti

`ask_tutor()` chaqiruvi `ChatActionSender.typing(...)` kontekstida bajariladi: AI javob
tayyorlayotganda foydalanuvchi doimiy «yozmoqda» indikatorini ko'radi. AI o'chirilgan
(rejim `plain`) holatda ham effekt ishlaydi; `message.bot` yo'q bo'lsa oddiy chaqiruv.

