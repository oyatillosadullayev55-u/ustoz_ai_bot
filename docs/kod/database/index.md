# `database` paketi — umumiy ko'rinish

**Yo'l:** [`database/`](../../../database)
**Vazifasi:** SQLite bilan ishlashning butun qatlami. Handlerlar SQL yozmaydi, faqat shu paket funksiyalarini chaqiradi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| [`db.py`](db.md) | Ulanish, sxema va indekslar |
| [`seed.py`](seed.md) | `content/seed_data.json` ni bazaga yuklash |
| [`users.py`](users.md) | Foydalanuvchilar va sozlamalar |
| [`content.py`](content.md) | Fanlar, darslar, savollar, qidiruv |
| [`quizzes.py`](quizzes.md) | Test natijalarini saqlash |
| [`progress.py`](progress.md) | Dars jarayoni va statistika |
| [`goals.py`](goals.md) | Kunlik maqsad va eslatma ro'yxati |
| [`chat.py`](chat.md) | AI suhbat tarixi va kunlik limit |
| [`admin.py`](admin.md) | Admin statistikasi va qabul qiluvchilar |

## Ma'lumotlar bazasi sxemasi

Loyihada **aynan 8 ta jadval** bor:

1. `users`
2. `subjects`
3. `lessons`
4. `questions`
5. `quiz_results`
6. `study_progress`
7. `chat_history`
8. `daily_goals`

## Umumiy qoidalar

- Barcha so'rovlar parametrlangan (`?`), foydalanuvchi matni SQL'ga to'g'ridan-to'g'ri qo'shilmaydi.
- Har bir funksiya `get_connection()` kontekst menejeridan foydalanadi; muvaffaqiyatda `commit`, xatolikda `rollback` avtomatik bajariladi.
- Vaqtlar UTC'da saqlanadi, kunlik hisoblar UTC+5 bo'yicha amalga oshiriladi.
- `database/__init__.py` faqat paket docstring'idan iborat.
