# `database/progress.py` — o'quv jarayoni va statistika

**Yo'l:** [`database/progress.py`](../../../database/progress.py)
**Vazifasi:** darslarni boshlash/tugatish, foydalanuvchi statistikasi va faollik kunlarini hisoblash.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `mark_lesson_started(user_id, lesson_id)` | Darsni `started` deb belgilaydi; mavjud bo'lsa faqat `updated_at` yangilanadi |
| `complete_lesson(user_id, lesson_id)` | `completed` qiladi; birinchi marta bo'lsa `True`, takroran bo'lsa `False` |
| `get_completed_lesson_ids(user_id, subject_id)` | Fan bo'yicha tugatilgan darslar to'plami |
| `get_user_stats(user_id)` | Testlar soni, o'rtacha/best foiz, darslar, AI savollar soni |
| `get_recent_results(user_id, limit=5)` | So'nggi test natijalari fan nomi bilan |
| `get_activity_stats(user_id)` | `streak` va `active_days` |

## Faollik kunlari

`get_activity_stats` uchta manbani `UNION` qiladi:

1. `quiz_results.created_at` — test topshirilgan kunlar.
2. `study_progress.completed_at` — dars tugatilgan kunlar.
3. `chat_history.created_at` — foydalanuvchi AI'ga savol yozgan kunlar.

Barcha sanalar `date(..., '+5 hours')` bilan UTC+5 ga o'tkaziladi, takrorlar `UNION` orqali olib tashlanadi. `calculate_streak` bugundan yoki kechadan boshlab ketma-ket kunlarni sanaydi.

## Muhim jihatlar

- `complete_lesson` idempotent: kunlik maqsad faqat birinchi tugatishda oshiriladi (handler `True` qiymatiga qarab).
- Statistika `quiz_results` va `study_progress` bo'yicha indekslardan foydalanadi.
- Foydalanuvchi matni statistika javobiga chiqarishdan oldin handlerda `html.escape` qilinadi.
