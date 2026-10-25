# `database/goals.py` — kunlik maqsadlar

**Yo'l:** [`database/goals.py`](../../../database/goals.py)
**Vazifasi:** har bir foydalanuvchi uchun kunlik dars/test maqsadini yaratish, yangilash va eslatma uchun ro'yxat tayyorlash.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `get_today_goal(user_id)` | Bugungi maqsadni qaytaradi; bo'lmasa `1 dars + 1 test` bilan yaratadi |
| `set_goal_targets(user_id, lessons, quizzes)` | Maqsadni 0–20 oralig'ida o'zgartiradi; bajarilganlar saqlanadi |
| `increment_goal(user_id, lessons=0, quizzes=0)` | Bajarilgan dars/test hisobini oshiradi |
| `get_pending_reminders(goal_date)` | Rejasi bajarilmagan va bildirishnomasi yoqilgan foydalanuvchilar |

## Kunlik kalit

- Barcha funksiyalar `local_today()` dan foydalanadi (UTC+5).
- `daily_goals` jadvalida `UNIQUE (user_id, goal_date)` bor, shuning uchun bir kunda bitta qator bo'ladi.
- Yangi kunda birinchi chaqiruv standart `1/1` maqsad yaratadi.

## Eslatma ro'yxati

`get_pending_reminders` shartlari:

```sql
dg.goal_date = ?
AND u.notifications_enabled = 1
AND (completed_lessons < target_lessons OR completed_quizzes < target_quizzes)
```

Shu sababli:

- bildirishnomalarni o'chirgan foydalanuvchi eslatma olmaydi;
- bugun reja ochmagan foydalanuvchi eslatma olmaydi (spam oldini oladi);
- maqsad bajarilgan bo'lsa eslatma yuborilmaydi.

## O'sish mantiqi

`increment_goal` qator bo'lmasa `1/1` nishon bilan yaratadi, keyin bajarilgan sonlarni qo'shadi. Manfiy qiymatlar `ValueError` beradi.
