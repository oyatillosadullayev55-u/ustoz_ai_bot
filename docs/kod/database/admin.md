# `database/admin.py` — admin statistikasi

**Yo'l:** [`database/admin.py`](../../../database/admin.py)
**Vazifasi:** admin panel uchun umumiy ko'rsatkichlar va xabar qabul qiluvchilar ro'yxatini tayyorlash.

## Funksiyalar

### `get_admin_stats()`

Qaytaradi:

| Kalit | Ma'nosi |
|---|---|
| `total_users` | Barcha foydalanuvchilar |
| `new_today` | Bugun ro'yxatdan o'tganlar (UTC+5) |
| `active_today` | Bugun oxirgi marta ko'ringanlar |
| `quizzes` | Jami yechilgan testlar |
| `average_score` | Testlarning o'rtacha foizi |
| `lessons_completed` | Jami tugatilgan darslar |
| `ai_today` | Bugungi AI savollar soni |
| `subjects` | Faol fanlar |
| `lessons` | Faol darslar |
| `questions` | Jami savollar |

### `get_all_user_ids(notifications_only=False)`

- `False` — barcha foydalanuvchilar.
- `True` — faqat bildirishnomalarni yoqqanlar (`notifications_enabled = 1`).
- Natija `telegram_id` bo'yicha o'sish tartibida.

## Muhim jihatlar

- Bugungi sanalar SQL'da `date(..., '+5 hours')` bilan hisoblanadi.
- Broadcast faqat ro'yxatdagi ID'larga yuboriladi; bloklagan foydalanuvchilar xato sifatida sanaladi.
- Statistik so'rovlar faqat o'qish (SELECT) amallarini bajaradi.
