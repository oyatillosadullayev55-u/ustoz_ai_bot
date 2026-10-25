# `keyboards/inline_buttons.py` — inline klaviaturalar

**Yo'l:** [`keyboards/inline_buttons.py`](../../../keyboards/inline_buttons.py)
**Vazifasi:** barcha inline tugmalarni va ularning callback formatlarini yasash.

## Doimiylar

- `LEVELS` — daraja kodi → o'qiladigan nom (`beginner` → `Boshlang'ich` va h.k.).
- `OPTION_LETTERS` — `("A", "B", "C", "D")`, test variantlari uchun.

## Klaviaturalar

| Funksiya | Callback formati |
|---|---|
| `get_levels_keyboard()` | `level:<code>` |
| `get_subjects_keyboard(subjects, prefix)` | `<prefix>:subject:<id>` |
| `get_lessons_keyboard(lessons, completed_ids, subject_id)` | `lesson:view:<id>` |
| `get_lesson_keyboard(...)` | `lesson:complete:<id>`, `quiz:subject:<id>`, `lesson:subject:<id>` |
| `get_quiz_options_keyboard(question_id, options)` | `quiz:answer:<question_id>:<0-3>` |
| `get_quiz_result_keyboard(subject_id)` | `quiz:subject:<id>`, `quiz:subjects` |
| `get_search_results_keyboard(lessons)` | `lesson:view:<id>` |
| `get_progress_keyboard()` | `stats:refresh`, `quiz:subjects`, `menu:home` |
| `get_goal_keyboard(...)` | `goal:set:<lessons>:<quizzes>`, `goal:refresh` |
| `get_settings_keyboard(...)` | `settings:level:<code>`, `settings:notify` |
| `get_admin_keyboard()` | `admin:stats`, `admin:broadcast` |
| `get_broadcast_confirm_keyboard()` | `admin:broadcast_confirm`, `admin:broadcast_cancel` |
| `get_broadcast_cancel_keyboard()` | `admin:broadcast_cancel` |

## Xavfsizlik va limitlar

- Test tugmalarida to'g'ri javob yo'q — faqat savol ID'si va variant indeksi.
- Variant matni 60 belgidan uzun bo'lsa qisqartiriladi (Telegram tugma limiti).
- Qidiruv natijalari tugma matni ham 60 belgi bilan cheklanadi.
- Barcha callback'lar qisqa va barqaror; matn o'zgarishi callback'ni buzmaydi.

## Yangilanishlar

`get_search_results_keyboard()` yangi `/qidiruv` buyrug'i uchun qo'shilgan. U natijalarni `lesson:view:<id>` tugmalari bilan ko'rsatadi va "Darslar"/"Menyu" tugmalarini beradi.
