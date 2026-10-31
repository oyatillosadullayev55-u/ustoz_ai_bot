# `database/gamification.py` — XP, yutuq va reyting so'rovlari

**Yo'l:** [`database/gamification.py`](../../../database/gamification.py)
**Vazifasi:** `xp_log`, `achievements` va `users.xp` bilan ishlash.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `award_xp(user_id, amount, reason, once_key=None)` | XP jurnaliga yozadi va `users.xp` ni oshiradi; takroriy `once_key` uchun `None` qaytaradi |
| `get_total_xp(user_id)` | Foydalanuvchining umumiy XP balansi |
| `get_weekly_xp(user_id)` | So'nggi 7 kundagi XP yig'indisi |
| `get_achievement_codes(user_id)` | Ochilgan yutuq kodlari to'plami |
| `unlock_achievements(user_id, codes)` | Yangi yutuqlarni yozadi, faqat haqiqatan qo'shilganlarini qaytaradi |
| `get_achievement_stats(user_id)` | Yutuq shartlari uchun 7 ta yig'ma ko'rsatkich |
| `get_weekly_leaderboard(user_id, limit=10)` | TOP-10, foydalanuvchining o'rni va haftalik XP'si |

## Bir marta beriladigan XP

`xp_log.once_key` ustunida qismiy unikal indeks bor:

```sql
CREATE UNIQUE INDEX idx_xp_log_once
    ON xp_log (user_id, once_key) WHERE once_key IS NOT NULL;
```

Shu sababli bir dars (`lesson:<id>`) yoki bir kunlik maqsad (`goal:<sana>`) uchun
XP faqat bir marta beriladi. Takroriy `INSERT` `sqlite3.IntegrityError` beradi va
funksiya `None` qaytaradi — handler buni oddiy holat deb qabul qiladi.

## Reyting mantiqi

1. `_week_cutoff()` — hozirdan 7 kun oldingi ISO vaqt.
2. Foydalanuvchilar `SUM(amount)` bo'yicha guruhlanadi, `week_xp > 0` sharti bilan.
3. Teng XP'da `telegram_id` bo'yicha tartib barqaror bo'ladi.
4. Foydalanuvchi o'rni: undan ko'proq XP to'plagan ishtirokchilar soni + 1.
5. Haftalik XP 0 bo'lsa o'rin `None` — ekranda "hali XP to'plamadingiz" chiqadi.

## Bog'liq hujjatlar

- [services/gamification.md](../services/gamification.md) — darajalar va yutuqlar ro'yxati
- [db.md](db.md) — jadval sxemalari
