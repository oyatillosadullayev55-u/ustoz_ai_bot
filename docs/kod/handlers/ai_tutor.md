# `handlers/ai_tutor.py` — AI Ustoz rejimi

**Yo'l:** [`handlers/ai_tutor.py`](../../../handlers/ai_tutor.py)
**Vazifasi:** foydalanuvchi savollariga AI yoki mahalliy dars bazasi orqali javob berish.

## FSM

`AITutorStates.chatting` — AI rejimi faol. Chiqish uchun `⬅️ Chiqish` tugmasi yoki asosiy menyu tugmasi bosiladi.

## Cheklovlar

| Doimiylik | Qiymat | Ma'nosi |
|---|---|---|
| `MAX_QUESTION_LENGTH` | 1000 | Bitta savolning maksimal uzunligi |
| `MAX_REPLY_LENGTH` | 3900 | Telegram xabar limitidan xavfsiz chegara |
| `AI_DAILY_LIMIT` | `.env` | Kunlik savollar soni |
| `AI_MIN_INTERVAL` | `.env` | Savollar orasidagi minimal tanaffus |
| `AI_HISTORY_LIMIT` | `.env` | Kontekstga qo'shiladigan oxirgi xabarlar |

## Oqim

1. `🧠 AI Ustoz` bosilganda rejim holati yoqiladi va AI holati haqida ma'lumot beriladi.
2. Savol kelganda:
   - uzunlik 2–1000 belgi orasida tekshiriladi;
   - `get_ai_usage()` orqali kunlik limit va oxirgi savol vaqti tekshiriladi;
   - `get_history()` bilan kontekst olinadi;
   - foydalanuvchi xabari bazaga yoziladi.
3. `send_chat_action(TYPING)` yuboriladi (xatolik bo'lsa faqat debug log).
4. `ask_tutor()` chaqiriladi. Natija `(javob, manba)`:
   - `ai` — provayder javobi, `html.escape` qilinadi;
   - `lessons` — dars bazasidan tayyor HTML javob;
   - `plain` — kutilmagan xatolik uchun oddiy matn.
5. Javob bazaga 4000 belgigacha saqlanadi va foydalanuvchiga yuboriladi.

## Xatoliklarni boshqarish

- AI provayderi xatosi `services/ai_service.py` ichida ushlanadi va dars bazasiga o'tadi.
- Kutilmagan xatolik bo'lsa, foydalanuvchiga "hozir javob bera olmadim" xabari yuboriladi, to'liq traceback logga yoziladi.
- AI kaliti yoki tokeni logga chiqarilmaydi.

## Muhim jihatlar

- AI javobi HTML sifatida escape qilinadi, shuning uchun model yuborgan teglar bajarilmaydi.
- Javob uzunligi `_truncate()` bilan cheklanadi; so'z o'rtasidan kesilmaslikka harakat qilinadi.
- Rejimdan chiqishda `state.clear()` chaqiriladi.
