# `content/seed_data.json` — o'quv kontenti

**Yo'l:** [`content/seed_data.json`](../../../content/seed_data.json)
**Vazifasi:** botning boshlang'ich o'quv kontenti: fanlar, darslar va test savollari.

## Hajm

| Element | Son |
|---|---|
| Fanlar | 10 |
| Darslar | 20 |
| Savollar | 80 |

Har bir darsda 4 tadan savol bor; har bir savolda 4 ta variant va izoh.
Har bir darsda qisqa mazmun, 3 ta asosiy fikr, daraja, davomiylik va kamida 900
belgili batafsil matn bor.

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
          "summary": "Hujayra — barcha tirik organizmlarning eng kichik tuzilish birligi...",
          "key_points": [
            "Hujayra membrana bilan o'ralgan.",
            "Yadro irsiy ma'lumotni saqlaydi.",
            "Mitoxondriya energiya ishlab chiqaradi."
          ],
          "level": "beginner",
          "duration_min": 7,
          "content": "1️⃣ Oddiy tilda: ...\n2️⃣ Hayotiy misol: ...",
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
| `lessons[].title` | Bo'sh bo'lmagan sarlavha |
| `lessons[].summary` | Bo'sh bo'lmagan qisqa mazmun (amalda 80+ belgi) |
| `lessons[].key_points` | 1–5 ta bo'sh bo'lmagan matn; tavsiya — aynan 3 ta |
| `lessons[].level` | `beginner`, `intermediate` yoki `advanced` |
| `lessons[].duration_min` | 1–120 oralig'idagi butun son |
| `lessons[].content` | Bo'sh bo'lmagan batafsil matn (amalda 900+ belgi) |
| `questions[].options` | Aynan 4 ta matn |
| `questions[].correct` | 0–3 oralig'idagi butun son |
| `questions[].explanation` | Ixtiyoriy, xatolar tahlilida ko'rsatiladi |

## Matn uslubi

Dars matni quyidagi tuzilishda yoziladi:

```text
🎯 Maqsad: ...
1️⃣ Oddiy tilda: ...
2️⃣ Hayotiy misol: ...
3️⃣ Asosiy fikrlar: ...
4️⃣ Eslab qolish siri: ...
✍️ Mini mashq: ...
✅ Xulosa: ...
```

Bu tuzilish kartochkadagi qisqa mazmun bilan birga ishlaydi: kartochka tez tanishtiradi,
batafsil ekran esa bosqichma-bosqich o'rgatadi.

## Tahrirlash tartibi

1. JSON'ni tahrirlang.
2. JSON sintaksisini tekshiring.
3. Botni qayta ishga tushiring — `seed_content()` kontentni upsert qiladi.
4. `tests/test_offline.py` ni ishga tushiring: u 11 fan, 35 dars va 140 savolni tekshiradi.

## Muhim jihatlar

- Dars ID'sini o'zgartirsangiz, uning savollari yangi ID oladi; eski test natijalari tarixiy bo'lib qoladi.
- JSON'dan olib tashlangan fan/dars `is_active = 0` bo'ladi, lekin bazadan o'chirilmaydi.
- Foydalanuvchi ma'lumotlari (natijalar, progress, maqsadlar) seed vaqtida saqlanadi.
- Har bir yangi dars uchun `assets/lesson_images/lesson_<id>.jpg` rasmini qo'shishni
  unutmang.
