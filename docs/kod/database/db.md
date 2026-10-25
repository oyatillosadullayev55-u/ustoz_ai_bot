# `database/db.py` — ulanish va sxema

**Yo'l:** [`database/db.py`](../../../database/db.py)
**Vazifasi:** SQLite ulanishini boshqarish, 8 ta jadvalni va indekslarni yaratish,
eski bazaga yangi dars ustunlarini migratsiya qilish.

## Tarkib

- `SCHEMA_SQL` — barcha `CREATE TABLE IF NOT EXISTS` va `CREATE INDEX IF NOT EXISTS` buyruqlari.
- `get_connection()` — `@asynccontextmanager`; har bir so'rov uchun ulanish ochadi.
- `_ensure_lesson_columns(db)` — eski bazaga `summary`, `key_points`, `level`,
  `duration_min` ustunlarini qo'shadi.
- `init_db()` — WAL rejimini yoqadi, sxemani qo'llaydi, migratsiyani bajaradi va
  `seed_content()` ni chaqiradi.

## `lessons` jadvali ustunlari

| Ustun | Ma'nosi |
|---|---|
| `content` | To'liq dars matni (batafsil ekranda ko'rsatiladi) |
| `summary` | Qisqa mazmun; kartochkada ko'rsatiladi |
| `key_points` | Asosiy fikrlar, JSON ro'yxat sifatida saqlanadi |
| `level` | `beginner`, `intermediate` yoki `advanced` |
| `duration_min` | Taxminiy o'qish vaqti, 1–120 daqiqa |

## `get_connection()` xatti-harakati

1. `settings.database_path.parent.mkdir(parents=True, exist_ok=True)` — papka bo'lmasa yaratadi.
2. `aiosqlite.connect(...)` — baza faylini ochadi.
3. `row_factory = aiosqlite.Row` — natijalarni ustun nomi bo'yicha o'qish imkonini beradi.
4. `PRAGMA foreign_keys = ON` — tashqi kalitlar majburiy.
5. `PRAGMA busy_timeout = 5000` — band bo'lsa 5 soniya kutadi.
6. `yield` dan keyin `commit`; istisno bo'lsa `rollback` va xatoni qayta ko'tarish.

## Jadval cheklovlari

- `users.level` faqat `beginner`, `intermediate`, `advanced`.
- `lessons.level` faqat `beginner`, `intermediate`, `advanced`.
- `lessons.duration_min` 1–120 oralig'ida.
- `questions.correct_option` 0–3 oralig'ida.
- `study_progress` asosiy kaliti `(user_id, lesson_id)` — takroriy yozuv oldini oladi.
- `daily_goals` uchun `UNIQUE (user_id, goal_date)`.
- `quiz_results.score_percent` 0–100.

## Migratsiya

`CREATE TABLE IF NOT EXISTS` mavjud jadvalni o'zgartirmaydi, shuning uchun yangi
ustunlar `PRAGMA table_info(lessons)` bilan tekshiriladi va faqat yetishmayotganlari
`ALTER TABLE lessons ADD COLUMN ...` orqali qo'shiladi. Har bir qo'shilgan ustun logga
yoziladi. Foydalanuvchi natijalari, progress va maqsadlar saqlanadi.

## Indekslar

`lessons(subject_id, order_index)`, `questions(lesson_id, order_index)`,
`quiz_results(user_id, created_at DESC)`, `study_progress(user_id, status)`,
`chat_history(user_id, created_at)`, `daily_goals(user_id, goal_date)`.

## Eslatma

`init_db()` idempotent: qayta ishga tushirilganda mavjud jadvallar va foydalanuvchi ma'lumotlari saqlanadi. Kontent yangilanishi `database/seed.py` tomonidan boshqariladi.

