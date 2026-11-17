# `content/turkish_courses.json` — Turk tili kursi

**Yo'l:** [`content/turkish_courses.json`](../../../content/turkish_courses.json)
**Vazifasi:** Turk tili fani, 8 dars, har bir darsda 8 ta tayyor gap va 4 ta test
savolini saqlaydi.

## Tuzilma

```json
{
  "subjects": [
    {
      "id": 9,
      "code": "turkish",
      "name": "Turk tili",
      "emoji": "🇹🇷",
      "description": "...",
      "lessons": [
        {
          "id": 1201,
          "title": "Salomlashish va tanishuv",
          "summary": "...",
          "key_points": ["...", "...", "..."],
          "level": "beginner",
          "duration_min": 8,
          "content": "...",
          "phrases": [{"tr": "Merhaba!", "uz": "Salom!", "hint": "mer-ha-BA"}],
          "questions": [{"text": "...", "options": ["..."], "correct": 0}]
        }
      ]
    }
  ]
}
```

## Darslar

| ID | Mavzu | Gaplar | Savollar |
|---|---|---|---|
| 1201 | Salomlashish va tanishuv | 8 | 4 |
| 1202 | Raqamlar va yosh | 8 | 4 |
| 1203 | Oila a'zolari | 8 | 4 |
| 1204 | Ovqat va ichimlik | 8 | 4 |
| 1205 | Shahar va yo'l so'rash | 8 | 4 |
| 1206 | Vaqt va kunlar | 8 | 4 |
| 1207 | Xarid qilish | 8 | 4 |
| 1208 | Mehmonxona va sayohat | 8 | 4 |

Jami: **64 ta gap**, **32 ta savol**.

## Qoidalar

- Har bir darsda bo'sh bo'lmagan `summary`, 1–5 ta `key_points`, `content` (900+
  belgi), `level`, `duration_min` bo'lishi kerak.
- `phrases` — kamida bitta gap; `tr` va `uz` majburiy, `hint` ixtiyoriy.
- `questions` — har birida aynan 4 ta variant va `0–3` oralig'idagi `correct`.
- Dars ID'lari `1201–1208`; savol ID'lari avtomatik `lesson_id * 10 + tartib`.

## Ovoz fayllari

Har bir gap uchun `assets/turkish_audio/lesson_<dars_id>_<tartib>.ogg` fayli
`scripts/generate_turkish_audio.py` bilan yaratiladi. Matn o'zgarsa, ovozni
qayta yaratish uchun skriptni `--force` bilan ishga tushiring.

## Bog'liq hujjatlar

- [`database/turkish.py`](../kod/database/turkish.md)
- [`scripts/generate_turkish_audio.py`](../kod/scripts/generate_turkish_audio.md)
- [`services/turkish_audio.py`](../kod/services/turkish_audio.md)
