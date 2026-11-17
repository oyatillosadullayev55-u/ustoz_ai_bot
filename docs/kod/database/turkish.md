# `database/turkish.py` — Turk tili kursi

**Yo'l:** [`database/turkish.py`](../../../database/turkish.py)
**Vazifasi:** `content/turkish_courses.json` faylini fan, dars, savol va gaplar
sifatida bazaga yuklash hamda dars gaplarini o'qish.

## Manba fayl

```json
{
  "subjects": [
    {
      "id": 9,
      "code": "turkish",
      "name": "Turk tili",
      "emoji": "🇹🇷",
      "lessons": [
        {
          "id": 1201,
          "title": "Salomlashish va tanishuv",
          "phrases": [{"tr": "Merhaba!", "uz": "Salom!", "hint": "mer-ha-BA"}],
          "questions": [{"text": "...", "options": ["..."], "correct": 0}]
        }
      ]
    }
  ]
}
```

## `seed_turkish()` ish tartibi

1. JSON faylni o'qiydi; fayl yo'q yoki buzuq bo'lsa `RuntimeError`.
2. Har bir darsni `_validate_lesson()` bilan tekshiradi: bo'sh bo'lmagan `summary`,
   1–5 ta `key_points`, to'g'ri `level`, 1–120 daqiqa `duration_min`, kamida bitta
   gap (`tr`, `uz`, ixtiyoriy `hint`) va 4 variantli savollar.
3. `subjects` jadvaliga fan ID'si bilan upsert qiladi va `is_active = 1` qiladi.
4. Darslarni upsert qiladi, `questions` jadvalida eski savollarni o'chirib qayta yozadi
   (`id = lesson_id * 10 + tartib`).
5. `turkish_phrases` jadvalida dars gaplarini qayta yozadi.
6. Yakunda dars, gap va savollar soni logga yoziladi.

`seed_content()` barcha fanlarni nofaol qiladi, shuning uchun `seed_turkish()` undan
**keyin** chaqiriladi (`database/db.py::init_db`).

## Doimiylar

| Doimiylik | Qiymat |
|---|---|
| `TURKISH_SUBJECT_ID` | `9` |
| `TURKISH_DATA_PATH` | `content/turkish_courses.json` |
| `VALID_LEVELS` | `beginner`, `intermediate`, `advanced` |

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `seed_turkish()` | Fan, 8 dars, 8 tadan gap va 32 savolni bazaga yuklaydi |
| `get_turkish_phrases(lesson_id)` | Dars gaplarini `phrase_index` tartibida qaytaradi |

## `turkish_phrases` jadvali

| Ustun | Ma'nosi |
|---|---|
| `lesson_id`, `phrase_index` | Birgalikdagi asosiy kalit |
| `phrase_tr` | Turkcha gap |
| `phrase_uz` | O'zbekcha tarjima |
| `hint` | Talaffuz maslahati (bo'sh bo'lishi mumkin) |

Jadval `lessons` ga `ON DELETE CASCADE` bilan bog'langan.

## Bog'liq hujjatlar

- [`content/turkish_courses.md`](../content/turkish_courses.md)
- [`services/turkish_audio.py`](../services/turkish_audio.md)
- [`handlers/turkish.py`](../handlers/turkish.md)
- [`database/db.md`](db.md)
