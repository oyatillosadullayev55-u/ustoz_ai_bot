# `database/users.py` — foydalanuvchilar

**Yo'l:** [`database/users.py`](../../../database/users.py)
**Vazifasi:** ro'yxatdan o'tgan foydalanuvchilar va ularning sozlamalari bilan ishlash.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `get_user(telegram_id)` | Foydalanuvchi qatorini qaytaradi yoki `None` |
| `create_user(...)` | Yangi foydalanuvchi qo'shadi; takroriy chaqiruvda hech narsa qilmaydi |
| `update_level(telegram_id, level)` | Darajani yangilaydi; qator topilsa `True` |
| `update_last_seen(telegram_id)` | `last_seen_at` ni joriy UTC vaqtga o'zgartiradi |
| `update_notifications(telegram_id, enabled)` | Bildirishnoma sozlamasini `0/1` qilib yozadi |

## Qoidalar

- `LEVELS = ("beginner", "intermediate", "advanced")`; boshqa qiymat `ValueError` beradi.
- `create_user` `ON CONFLICT(telegram_id) DO NOTHING` ishlatadi — `/start` bir necha marta bosilsa ham dublikat yaratilmaydi.
- `full_name` sxema darajasida 1–100 belgi bilan cheklangan; `handlers/start.py` esa 2–50 belgi qabul qiladi.
- `notifications_enabled` SQLite'da butun son (`0`/`1`) sifatida saqlanadi, Python'da `bool(...)` bilan o'qiladi.
- Barcha vaqtlar `utc_now()` orqali UTC ISO matn ko'rinishida yoziladi.
