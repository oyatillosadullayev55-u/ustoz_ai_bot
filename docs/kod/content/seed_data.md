# `content/seed_data.json` — o'quv kontenti

**Yo'l:** [`content/seed_data.json`](../../../content/seed_data.json)
**Vazifasi:** botning boshlang'ich o'quv kontenti: fanlar, darslar va test savollari.

## Hajm

| Element | Son |
|---|---|
| Fanlar | 10 |
| Darslar | 20 |
| Savollar | 60 |

Har bir darsda 3 tadan savol bor; har bir savolda 4 ta variant.

## Tuzilma

```json
{
  "subjects": [
    {
      "id": 5,
      "code": "biology",
      "name": "Biologiya",
      "emoji": "🧬",
      "description": "Tirik organizmlar haqidagi fan",
      "lessons": [
        {
          "id": 501,
          "title": "Hujayra tuzilishi",
          "content": "Dars matni...",
          "questions": [
            {
              "text": "Savol matni?",
              "options": ["A", "B", "C", "D"],
              "correct": 0,
              "explanation": "Nima uchun bu javob to'g'ri"
            }
          ]
        }
      ]
    }
  ]
}
```

## Maydon qoidalari

| Maydon | Qoida |
|---|---|
| `subjects[].id` | Butun son, unikal |
| `subjects[].code` | Unikal kod (bazada `UNIQUE`) |
| `subjects[].emoji` | Ixtiyoriy, standart `📚` |
| `lessons[].id` | Butun son, unikal; savol ID'lari shundan hosil bo'ladi |
| `lessons[].content` | Bo'sh bo'lmagan matn |
| `questions[].options` | Aynan 4 ta matn |
| `questions[].correct` | 0–3 oralig'idagi butun son |
| `questions[].explanation` | Ixtiyoriy, xatolar tahlilida ko'rsatiladi |

## Tahrirlash tartibi

1. JSON'ni tahrirlang.
2. JSON sintaksisini tekshiring.
3. Botni qayta ishga tushiring — `seed_content()` kontentni upsert qiladi.
4. `tests/test_offline.py` ni ishga tushiring: u 10 fan va 60 savolni tekshiradi.

## Muhim jihatlar

- Dars ID'sini o'zgartirsangiz, uning savollari yangi ID oladi; eski test natijalari tarixiy bo'lib qoladi.
- JSON'dan olib tashlangan fan/dars `is_active = 0` bo'ladi, lekin bazadan o'chirilmaydi.
- Foydalanuvchi ma'lumotlari (natijalar, progress, maqsadlar) seed vaqtida saqlanadi.
