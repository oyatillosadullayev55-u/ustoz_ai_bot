# `database/quizzes.py` — test natijalari

**Yo'l:** [`database/quizzes.py`](../../../database/quizzes.py)
**Vazifasi:** tugallangan test natijasini `quiz_results` jadvaliga yozish.

## `save_quiz_result(...)`

```python
async def save_quiz_result(
    *, user_id: int, subject_id: int,
    total_questions: int, correct_answers: int
) -> int
```

1. `total_questions > 0` tekshiriladi.
2. `0 <= correct_answers <= total_questions` tekshiriladi.
3. Foiz `round(correct_answers / total_questions * 100)` bilan hisoblanadi.
4. Yozuv UTC vaqt bilan `INSERT` qilinadi.
5. Hisoblangan foiz qaytariladi — handler shu qiymatni natija ekranida ko'rsatadi.

## Nima uchun foiz bazada saqlanadi

- Statistika (`get_user_stats`, `get_recent_results`, admin panel) qayta hisoblashsiz tez ishlaydi.
- Tarixiy natijalar savollar soni o'zgarsa ham o'z foizini saqlab qoladi.

## Cheklovlar

- `subject_id` mavjud fanga tashqi kalit bilan bog'langan.
- Noto'g'ri qiymatlar `ValueError` bilan rad etiladi; handlerlar faqat tekshirilgan sonlarni uzatadi.
