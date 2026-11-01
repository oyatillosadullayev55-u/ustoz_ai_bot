# `database/daily.py` — kunlik sovg'a, savol va missiyalar

**Yo'l:** [`database/daily.py`](../../../database/daily.py)
**Vazifasi:** kunlik sovg'a, kunlik savol javoblari va haftalik missiya faolligi bo'yicha SQL so'rovlar.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `get_daily_question(day)` | Kun uchun bitta savolni barqaror tanlaydi |
| `get_daily_answer(user_id, day)` | Foydalanuvchining shu kungi javobini qaytaradi |
| `save_daily_answer(...)` | Javobni yozadi; takroriy javobda `False` qaytaradi |
| `get_daily_answer_days(user_id)` | Javob berilgan sanalar to'plami (seriya uchun) |
| `has_daily_gift(user_id, day)` | Shu kungi sovg'a olinganmi |
| `get_gift_days(user_id)` | Sovg'a olingan sanalar to'plami |
| `week_start_date()` | Joriy haftaning dushanbasi (UTC+5) |
| `current_week_key()` | `YYYY-Www` ko'rinishidagi hafta kaliti |
| `get_weekly_activity(user_id)` | Shu haftadagi dars, test va AI savollari soni |
| `get_claimed_missions(user_id)` | Shu haftada olingan missiya kodlari |

## Kunlik savol tanlovi

```sql
offset = zlib.crc32(day.encode("utf-8")) % total
SELECT ... ORDER BY q.id LIMIT 1 OFFSET ?
```

`total` — faol fan va darslarga tegishli savollar soni. Sana o'zgarmasa, offset
ham o'zgarmaydi, shuning uchun kun davomida barcha foydalanuvchilar bir xil
savolni ko'radi. Savol faol bo'lmagan darsdan tanlanmaydi.

## Idempotentlik

- `daily_answers` jadvalida `PRIMARY KEY (user_id, answer_date)` bor.
- `save_daily_answer` `INSERT ... ON CONFLICT(user_id, answer_date) DO NOTHING`
  ishlatadi va `cursor.rowcount > 0` qaytaradi. Shu sababli bir kunda ikkinchi
  javob yozilmaydi.
- Sovg'a va missiya mukofotlari `xp_log.once_key` orqali tekshiriladi:
  `gift:<sana>` va `mission:<kod>:<hafta>`.
- `question_id` ataylab tashqi kalit emas: seed savollarni qayta yozganda
  `ON DELETE CASCADE` kunlik javoblar tarixini o'chirib yuborardi.

## Hafta chegarasi

`week_start_date()` mahalliy (UTC+5) dushanbani qaytaradi. `_week_start_utc()`
shu sanani UTC ISO vaqtiga o'giradi va `get_weekly_activity` SQL'ida cutoff
sifatida ishlatiladi. Natijada bazada UTC saqlansa ham, haftalik missiyalar
O'zbekiston vaqti bo'yicha to'g'ri hisoblanadi.
