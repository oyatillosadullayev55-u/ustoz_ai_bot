# `time_utils.py` — vaqt va sana yordamchilari

**Yo'l:** [`time_utils.py`](../../time_utils.py)
**Vazifasi:** butun loyiha uchun yagona vaqt zonasi va sana hisoblash qoidalarini berish.

## Vaqt zonasi

- `LOCAL_TZ = UTC+5` — O'zbekiston vaqti.
- Bazada vaqtlar **UTC** ko'rinishida saqlanadi (`utc_now()`).
- Kunlik maqsad, streak va eslatmalar **mahalliy** sana bo'yicha hisoblanadi.

## Funksiyalar

| Funksiya | Qaytaradi | Izoh |
|---|---|---|
| `utc_now()` | ISO matn | `2026-10-25T07:00:00+00:00` ko'rinishida, sekundgacha |
| `local_now()` | `datetime` | UTC+5 zonasi bilan joriy vaqt |
| `local_today()` | `YYYY-MM-DD` | Mahalliy bugungi sana |
| `local_date_of(value)` | `date \| None` | ISO matnni mahalliy sanaga aylantiradi; noto'g'ri qiymatda `None` |
| `format_local_date(value, fmt)` | matn | Standart `%d.%m.%Y`; bo'sh qiymatda `—` |
| `calculate_streak(days)` | `int` | Bugundan yoki kechadan boshlab ketma-ket faol kunlar |
| `seconds_until_local_time(hour, minute=0)` | `float` | Keyingi belgilangan mahalliy vaqtgacha soniyalar |

## Muhim qoidalar

- `calculate_streak` bugun hali faol bo'lmasa, kechadan boshlab sanaydi — foydalanuvchi kunni hali boshlamagan bo'lsa ham streak saqlanadi.
- `seconds_until_local_time` o'tib ketgan vaqtni ertangi kunga suradi; noto'g'ri soat/daqiqada `ValueError` beradi.
- SQL so'rovlarida UTC matn sanani mahalliy kunga aylantirish uchun `date(created_at, '+5 hours')` ishlatiladi.
