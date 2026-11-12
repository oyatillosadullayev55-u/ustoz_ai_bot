# `database/anatomy.py` — Anatomiya savollar banki

**Yo'l:** [`database/anatomy.py`](../../../database/anatomy.py)
**Vazifasi:** `content/anatomy_questions.json` faylini `anatomy_questions` jadvaliga
yuklash va savollarni tanlash.

## Manba fayl

```json
[
  {
    "text": "Mezensefalonda joylashgan vegetativ o'zak qaysi?",
    "options": ["nucleus dorsalis", "nucleus accessorius", "nucleus ambiguus", "nucleus ruber"],
    "correct": 0
  }
]
```

- Har bir yozuvda bo'sh bo'lmagan `text`, aynan 4 ta `options` va `0–3` oralig'idagi
  `correct` bo'lishi shart.
- Manba: `ANATOMIYA_549_test.html`; takroriy savollar olib tashlangandan keyin **546**
  ta yozuv qolgan.
- Variantlar tartibi savol matni bo'yicha `sha256` bilan barqaror aralashtiriladi, shuning
  uchun to'g'ri javob pozitsiyasi tasodifiy, lekin har safar bir xil.

## Doimiylar

| Doimiylik | Qiymat |
|---|---|
| `ANATOMY_SUBJECT_ID` | `900` — yashirin fan ID'si |
| `ANATOMY_DATA_PATH` | `content/anatomy_questions.json` |
| `QUESTION_FIELDS` | `SELECT` uchun ustunlar ro'yxati |

## `seed_anatomy()` ish tartibi

1. JSON faylni UTF-8 da o'qiydi; fayl yo'q yoki buzuq bo'lsa `RuntimeError`.
2. `_validate()` har bir yozuvni tekshiradi va `(id, text, a, b, c, d, correct, order_index)`
   qatorlarini tayyorlaydi.
3. `subjects` jadvaliga `id=900, code='anatomy', is_active=0` bilan upsert qiladi.
   Yashirin fan `quiz_results.subject_id` tashqi kaliti uchun kerak, lekin fanlar
   ro'yxatiga chiqmaydi.
4. `DELETE FROM anatomy_questions` → `executemany` bilan qayta yozadi. Seed idempotent.
5. Yakunda savollar soni logga yoziladi.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `seed_anatomy()` | Bank va yashirin fanni bazaga yuklaydi |
| `count_anatomy_questions()` | Jami savollar soni (menyuda ko'rsatiladi) |
| `get_anatomy_questions(limit)` | `ORDER BY RANDOM() LIMIT ?` bilan tasodifiy savollar |
| `get_anatomy_question(id)` | Bitta savol |
| `get_anatomy_questions_by_ids(ids)` | Xatolar tahlili uchun `{id: row}` lug'ati |
| `save_anatomy_session(user_id, data)` | Faol testni `anatomy_sessions` ga upsert qiladi |
| `load_anatomy_session(user_id)` | Faol testni lug'at sifatida qaytaradi (yo'q bo'lsa `None`) |
| `delete_anatomy_session(user_id)` | Yakunlangan/bekor qilingan testni o'chiradi |

## `anatomy_sessions` jadvali

Faol test FSM o'rniga shu jadvalda saqlanadi — bot qayta ishga tushsa yoki boshqa bo'lim
FSM holatini tozalasa ham javoblar qabul qilinaveradi. `question_ids` va `answers` JSON
satr sifatida yoziladi; `deadline`/`started_at` — `time.time()` qiymatlari.

| Ustun | Ma'nosi |
|---|---|
| `user_id` | Egasi (birlamchi kalit, `users` ga FK) |
| `mode` | 10 / 20 / 50 savollik rejim |
| `question_ids` | Savol ID'lari JSON ro'yxati |
| `answered_index` | Joriy savol indeksi |
| `correct` | To'g'ri javoblar soni |
| `answers` | `[{"question_id": ..., "selected": ...}]` JSON |
| `current_id` | Joriy savol ID'si (eski tugmalarni rad etish uchun) |
| `deadline`, `started_at` | Vaqt chegarasi va boshlanish vaqti |
| `chat_id`, `message_id` | Tahrirlanadigan savol xabari |

## Jadval

```sql
CREATE TABLE IF NOT EXISTS anatomy_questions (
    id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option INTEGER NOT NULL CHECK (correct_option BETWEEN 0 AND 3),
    order_index INTEGER NOT NULL DEFAULT 0
);
```

`order_index` bo'yicha indeks `database/db.py` da yaratiladi.

## Bog'liq fayllar

- [`database/db.py`](db.md) — jadval sxemasi va `init_db()` chaqiruvi
- [`handlers/anatomy.py`](../handlers/anatomy.md) — test oqimi
