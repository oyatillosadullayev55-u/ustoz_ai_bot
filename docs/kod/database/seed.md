# `database/seed.py` — kontentni yuklash

**Yo'l:** [`database/seed.py`](../../../database/seed.py)
**Vazifasi:** `content/seed_data.json` faylidagi fan, dars va savollarni bazaga sinxronlash.

## Manba fayl tuzilmasi

```json
{
  "subjects": [
    {
      "id": 1,
      "code": "math",
      "name": "Matematika",
      "emoji": "...",
      "description": "...",
      "lessons": [
        {
          "id": 101,
          "title": "...",
          "content": "...",
          "questions": [
            {
              "text": "...",
              "options": ["A", "B", "C", "D"],
              "correct": 0,
              "explanation": "..."
            }
          ]
        }
      ]
    }
  ]
}
```

## `seed_content()` ish tartibi

1. JSON faylni UTF-8 da o'qib, `json.loads` qiladi. Fayl yo'q yoki JSON buzuq bo'lsa `RuntimeError`.
2. Barcha mavjud fan va darslarni `is_active = 0` qiladi (JSON'dan tushib qolganlar yashiriladi, lekin o'chirilmaydi).
3. Har bir fan uchun `INSERT ... ON CONFLICT(id) DO UPDATE` bajaradi.
4. Har bir dars uchun upsert qiladi va `created_at` ni faqat yangi yozuvda yozadi.
5. Dars savollarini `DELETE` qilib, JSON'dan qayta qo'shadi. Bu savollar tartibini va matnini to'liq yangilaydi.
6. Savol ID'si `lesson_id * 10 + question_order` formula bilan barqaror hisoblanadi.
7. Har bir savolda 4 ta variant va 0–3 oralig'idagi `correct` bo'lmasa `RuntimeError` beradi.
8. Yakunda fan, dars va savollar soni logga yoziladi.

## Xavfsizlik va ma'lumot yaxlitligi

- Seed faqat kontent jadvallariga tegadi: `users`, `quiz_results`, `study_progress`, `chat_history`, `daily_goals` saqlanadi.
- Savol ID'lari barqaror bo'lgani uchun eski natijalar va havolalar buzilmaydi.
- JSON'da faqat admin tomonidan tasdiqlangan matn bo'lishi kerak; foydalanuvchi kiritgan matn seed'ga tushmaydi.
