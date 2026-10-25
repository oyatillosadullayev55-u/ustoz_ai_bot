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
| `get_lesson_keyboard(...)` | `lesson:read:<id>`, `lesson:complete:<id>`, `lesson:ask:<id>`, `quiz:subject:<id>`, `lesson:view:<id>` (qo'shnilar), `lesson:subject:<id>` |
| `get_lesson_details_keyboard(...)` | `lesson:view:<id>` (kartochkaga qaytish), `lesson:complete`, `lesson:ask`, `quiz:subject`, qo'shni darslar, `lesson:subject`, `menu:home` |
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

- `get_lesson_keyboard()` qisqa kartochka uchun: batafsil o'qish, tugatish, AI, test va
  oldingi/keyingi dars tugmalari.
- `get_lesson_details_keyboard()` batafsil ekran uchun: kartochkaga qaytish va AI
  tugmasi bilan bir xil navigatsiya.
- `_lesson_nav_row()` faqat mavjud qo'shni darslar uchun tugma qo'shadi.
- `get_search_results_keyboard()` `/qidiruv` natijalarini `lesson:view:<id>` bilan
  ko'rsatadi.
- Qo'shni darslar va qidiruv natijalari doim kartochka orqali ochiladi, shuning uchun
  har bir dars bir xil ko'rinishda boshlanadi.
