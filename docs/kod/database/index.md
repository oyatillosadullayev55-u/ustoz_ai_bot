# `database` paketi — umumiy ko'rinish

**Yo'l:** [`database/`](../../../database)
**Vazifasi:** SQLite bilan ishlashning butun qatlami. Handlerlar SQL yozmaydi, faqat shu paket funksiyalarini chaqiradi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| [`db.py`](db.md) | Ulanish, sxema va indekslar |
| [`seed.py`](seed.md) | `content/seed_data.json` ni bazaga yuklash |
| [`turkish.py`](turkish.md) | Turk tili darslari, gaplari va savollarini yuklash |
| [`users.py`](users.md) | Foydalanuvchilar va sozlamalar |
| [`content.py`](content.md) | Fanlar, darslar, savollar, qidiruv |
| [`quizzes.py`](quizzes.md) | Test natijalarini saqlash |
| [`anatomy.py`](anatomy.md) | 546 savollik Anatomiya banki va yashirin natija fani |
| [`progress.py`](progress.md) | Dars jarayoni va statistika |
| [`goals.py`](goals.md) | Kunlik maqsad va eslatma ro'yxati |
| [`chat.py`](chat.md) | AI suhbat tarixi va kunlik limit |
| [`admin.py`](admin.md) | Admin statistikasi, qabul qiluvchilar va CSV ma'lumoti |
| [`gamification.py`](gamification.md) | XP, yutuqlar va haftalik reyting |
| [`favorites.py`](favorites.md) | Sevimli darslar |
| [`daily.py`](daily.md) | Kunlik sovg'a, savol javoblari va haftalik faollik |

## Ma'lumotlar bazasi sxemasi

Loyihada **15 ta jadval** bor:

1. `users`
2. `subjects`
3. `lessons`
4. `questions`
5. `quiz_results`
6. `study_progress`
7. `chat_history`
8. `daily_goals`
9. `xp_log`
10. `achievements`
11. `favorites`
12. `daily_answers`
13. `anatomy_questions`
14. `anatomy_sessions`
15. `turkish_phrases`

## Umumiy qoidalar

- Barcha so'rovlar parametrlangan (`?`), foydalanuvchi matni SQL'ga to'g'ridan-to'g'ri qo'shilmaydi.
- Har bir funksiya `get_connection()` kontekst menejeridan foydalanadi; muvaffaqiyatda `commit`, xatolikda `rollback` avtomatik bajariladi.
- Vaqtlar UTC'da saqlanadi, kunlik hisoblar UTC+5 bo'yicha amalga oshiriladi.
- `database/__init__.py` faqat paket docstring'idan iborat.
