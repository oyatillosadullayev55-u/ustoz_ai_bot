# `database/chat.py` — AI suhbat tarixi va limit

**Yo'l:** [`database/chat.py`](../../../database/chat.py)
**Vazifasi:** AI Ustoz suhbatini saqlash, tarixni olish va kunlik foydalanishni sanash.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `add_message(user_id, role, message)` | `user` yoki `assistant` xabarini saqlaydi |
| `get_history(user_id, limit)` | Oxirgi `limit` xabarni vaqt tartibida qaytaradi |
| `get_ai_usage(user_id)` | Bugungi savollar soni va oxirgi savol vaqti |

## Tafsilotlar

- `role` faqat `user` yoki `assistant`; boshqa qiymat `ValueError`.
- `get_history` `ORDER BY id DESC LIMIT ?` bilan oxirgi xabarlarni oladi, keyin ro'yxatni teskari aylantiradi — natija xronologik tartibda bo'ladi.
- `get_ai_usage` faqat `role = 'user'` xabarlarini sanaydi va `date(created_at, '+5 hours') = local_today()` shartini qo'llaydi.
- `limit <= 0` bo'lsa tarix so'ralmaydi.
- AI javobi bazaga 4000 belgigacha saqlanadi (`handlers/ai_tutor.py` cheklovi).

## Nima uchun kerak

- Handler kunlik limit va minimal intervalni shu ma'lumotlar asosida tekshiradi.
- Tarix AI provayderiga kontekst sifatida yuboriladi (`AI_HISTORY_LIMIT`).
- Faollik statistikasi AI savol yozilgan kunlarni ham hisobga oladi.
