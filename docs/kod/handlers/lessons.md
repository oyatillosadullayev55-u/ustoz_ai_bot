# `handlers/lessons.py` — darslar va qidiruv

**Yo'l:** [`handlers/lessons.py`](../../../handlers/lessons.py)
**Vazifasi:** fanlar → darslar → dars matni → tugatish oqimi va `/qidiruv` buyrug'i.

## Asosiy oqim

1. `📚 Darslar` tugmasi fanlar ro'yxatini ochadi (`lesson:subjects`).
2. `lesson:subject:<id>` fan darslarini ko'rsatadi; tugatilganlar `✅` bilan belgilanadi.
3. `lesson:view:<id>` dars matnini ochadi va `mark_lesson_started()` chaqiradi.
4. `lesson:complete:<id>` darsni tugatadi:
   - `complete_lesson()` `True` qaytarsa, `increment_goal(lessons=1)`;
   - allaqachon tugatilgan bo'lsa, ogohlantirish beriladi.
5. Dars ekranida `📝 Test yechish` tugmasi shu fan testini boshlaydi.

## `/qidiruv` buyrug'i

```text
/qidiruv fotosintez
/search fotosintez
```

- So'rov 2–100 belgi orasida bo'lishi kerak.
- `search_lessons(query, limit=5)` sarlavha va matn bo'yicha qidiradi.
- Natija topilmasa, bosh menyu bilan maslahat xabari yuboriladi.
- Natijalar `lesson:view:<id>` tugmalari bilan chiqadi.
- So'rov va dars nomlari HTML uchun `html.escape` qilinadi.

## Doimiylar

| Doimiylik | Qiymat |
|---|---|
| `SEARCH_MIN_LENGTH` | 2 |
| `SEARCH_MAX_LENGTH` | 100 |
| `SEARCH_RESULTS_LIMIT` | 5 |

## Xavfsizlik

Foydalanuvchi kiritgan qidiruv matni to'g'ridan-to'g'ri HTML'ga qo'yilmaydi; avval escape qilinadi. SQL so'rov esa parametrlangan.
