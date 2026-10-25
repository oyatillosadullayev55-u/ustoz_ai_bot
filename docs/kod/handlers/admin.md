# `handlers/admin.py` — admin panel

**Yo'l:** [`handlers/admin.py`](../../../handlers/admin.py)
**Vazifasi:** faqat adminlar uchun statistika va foydalanuvchilarga ommaviy xabar yuborish.

## Admin tekshiruvi

`IsAdmin` filtri `get_settings().is_admin(event.from_user.id)` ni tekshiradi. `/admin` admin bo'lmagan foydalanuvchi uchun o'z ID'sini va `ADMIN_IDS` sozlamasini ko'rsatuvchi rad javobini beradi.

## Statistika

`admin:stats` callback `get_admin_stats()` natijasini ko'rsatadi: foydalanuvchilar, bugungi yangilar/faollar, testlar, darslar, AI savollar va kontent soni.

## Broadcast oqimi

```text
/admin → admin:broadcast → waiting_broadcast
→ matn kiritish → confirm_broadcast
→ admin:broadcast_confirm → yuborish
```

- Matn 1–3000 belgi bo'lishi kerak.
- Yuborishdan oldin qabul qiluvchilar soni ko'rsatiladi.
- `admin:broadcast_cancel` yoki `/cancel` bekor qiladi.

## Yuborish tafsilotlari

- Faqat `notifications_enabled = 1` foydalanuvchilar oladi.
- Xabar `parse_mode=None` bilan yuboriladi — admin matni HTML sifatida talqin qilinmaydi.
- `TelegramRetryAfter` bo'lsa, `retry_after` soniya kutib bir marta qayta uriniladi.
- Har bir xabar orasida 0,05 soniya tanaffus — Telegram limitini yumshatish uchun.
- Bloklagan foydalanuvchilar `failed` sifatida sanaladi.
- Xabar matni va qabul qiluvchilar ro'yxati logga yozilmaydi; faqat yuborilgan/xato soni.

## Admin statistikasi manbasi

`database/admin.py`: `get_admin_stats`, `get_all_user_ids`.
