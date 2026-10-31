# `handlers/gamification.py` — yutuqlar, reyting va sevimlilar ekranlari

**Yo'l:** [`handlers/gamification.py`](../../../handlers/gamification.py)
**Router:** `gamification`

## Callbacklar

| Callback | Ekran |
|---|---|
| `stats:achievements` | 12 ta yutuq: ✅ ochilgan, 🔒 yopiq |
| `stats:leaderboard` | So'nggi 7 kunlik TOP-10 va foydalanuvchi o'rni |
| `stats:favorites` | Sevimli darslar ro'yxati va ochish tugmalari |

## Mantiq

- Har bir handler avval `require_user_callback()` bilan ro'yxatdan o'tishni tekshiradi.
- Ekranlar `safe_edit()` orqali yangilanadi — foto xabar bo'lsa yangi xabar yuboriladi.
- Haftalik reytingda TOP-3 uchun 🥇🥈🥉, qolganlar uchun tartib raqami.
- Ismlar `html.escape` qilinadi va 24 belgida qisqartiriladi.
- Reyting bo'sh bo'lsa "Birinchi darsni tugatib, ro'yxatga kiring! 🚀" ko'rsatiladi.
- Sevimlilar bo'sh bo'lsa dars kartochkasidagi ⭐ tugmasiga yo'naltiruvchi matn chiqadi.

## Klaviaturalar

- `get_stats_back_keyboard()` — «⬅️ Natijalar» va «🏠 Bosh menyu».
- `get_favorite_lessons_keyboard(lessons)` — har dars uchun `lesson:view:<id>`.

## Bog'liq

- [services/gamification.md](../services/gamification.md)
- [database/favorites.md](../database/favorites.md)
