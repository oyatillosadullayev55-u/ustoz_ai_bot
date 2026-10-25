# `database/content.py` — fanlar, darslar va qidiruv

**Yo'l:** [`database/content.py`](../../../database/content.py)
**Vazifasi:** o'quv kontentini o'qish, test savollarini tanlash va darslar bo'yicha matnli qidiruv.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `get_subjects_with_counts()` | Faol fanlar, darslar soni va savollar soni bilan |
| `get_subject(subject_id)` | Bitta faol fan |
| `get_lessons(subject_id)` | Fanning faol darslari, tartib bilan |
| `get_lesson(lesson_id)` | Dars matni va fan nomi/emoji'si |
| `get_quiz_questions(subject_id, limit)` | Tasodifiy savollar to'plami |
| `get_question(question_id)` | Bitta savol va uning dars/fan ma'lumoti |
| `get_questions_by_ids(ids)` | Savollarni bitta `IN (...)` so'rovda olib, `{id: row}` qaytaradi |
| `extract_tokens(text, limit=5)` | Qidiruv uchun kalit so'zlarni ajratadi |
| `search_lessons(text, limit=2)` | Sarlavha va matn bo'yicha dars qidiradi |

## Qidiruv mantiqi

1. Matn kichik harflarga o'tkaziladi va `[0-9a-zA-Zа-яА-ЯёЁʻ'’]+` regex bilan bo'linadi.
2. 3 belgidan qisqa so'zlar va `STOPWORDS` ro'yxatidagi yordamchi so'zlar tashlanadi.
3. Har bir token uchun `lower(title) LIKE ? OR lower(content) LIKE ?` sharti tuziladi.
4. Natijalar avval sarlavhada mos kelganlar, keyin `order_index` bo'yicha tartiblanadi.
5. `handlers/lessons.py` qidiruvni 5 ta natija bilan cheklaydi.

## Xavfsizlik

- `LIKE` parametrlari `?` orqali uzatiladi — SQL injection yo'q.
- Foydalanuvchi so'rovi javob matniga chiqarishdan oldin handlerda `html.escape` qilinadi.
- `get_quiz_questions` `correct_option` ni qaytaradi, lekin handler uni tugma matniga yoki callback'ga qo'shmaydi. To'g'ri javob faqat foydalanuvchi javob bergandan keyin tekshiriladi.
