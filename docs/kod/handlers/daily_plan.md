# `handlers/daily_plan.py` — kunlik reja

**Yo'l:** [`handlers/daily_plan.py`](../../../handlers/daily_plan.py)
**Vazifasi:** bugungi maqsadni ko'rsatish, progress barni chizish va maqsadni o'zgartirish.

## Ekran tarkibi

- Bugungi sana (UTC+5);
- foydalanuvchi ismi;
- darslar va testlar progressi (`▓`/`░` bar);
- ketma-ket faol kunlar;
- qolgan ishlar yoki "maqsad bajarildi" xabari.

## Callback'lar

| Callback | Vazifasi |
|---|---|
| `goal:set:<lessons>:<quizzes>` | Maqsadni o'zgartiradi |
| `goal:refresh` | Ekranni yangilaydi |

## Tekshiruvlar

- `goal:set` callback'i 4 qismdan iborat bo'lishi kerak.
- Qiymatlar 0–20 oralig'ida va yig'indisi 0 dan katta bo'lishi kerak.
- Noto'g'ri qiymatda `show_alert` bilan xabar beriladi.

## Klaviatura

`get_goal_keyboard()` uchta tayyor variantni beradi:

- `1 dars + 1 test` — oson;
- `2 dars + 2 test` — o'rta;
- `3 dars + 3 test` — intensiv.

Joriy tanlov `✅` bilan belgilanadi.

## Bog'liq eslatma

Kunlik maqsad `daily_goals` jadvalida saqlanadi. `services/reminders.py` shu jadval asosida rejasi bajarilmagan foydalanuvchilarga eslatma yuboradi.
