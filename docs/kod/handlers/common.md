# `handlers/common.py` — umumiy yordamchilar

**Yo'l:** [`handlers/common.py`](../../../handlers/common.py)
**Vazifasi:** barcha handlerlar ishlatadigan tekshiruv va xabar tahrirlash yordamchilari.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `require_user(message)` | `from_user` va bazadagi foydalanuvchini tekshiradi; yo'q bo'lsa `/start` ga yo'naltiradi |
| `require_user_callback(callback)` | Callback uchun xuddi shu tekshiruv, `show_alert` bilan |
| `safe_edit(callback, text, markup)` | Xabarni tahrirlaydi; foto yoki eskirgan xabarda yangisini yuboradi |
| `progress_bar(done, target, width=8)` | `▓` va `░` belgilaridan progress bar yasaydi |
| `react(message, emoji)` | Xabarga emoji reaksiya qo'yadi (👋, 📖, 🎉, ✅/❌) — `TelegramAPIError` yutiladi |
| `send_action(message, action)` | «yozmoqda»/«rasm yuklanmoqda» holatini ko'rsatadi; xatolar logga yozilib yutiladi |

## `require_user` mantiqi

- `message.from_user is None` bo'lsa `None`.
- `get_user(telegram_id)` `None` qaytarsa, foydalanuvchiga ro'yxatdan o'tish eslatmasi va bosh menyu yuboriladi.
- Aks holda foydalanuvchi qatori qaytariladi.

## `safe_edit` nima uchun kerak

Telegram eski inline xabarni tahrirlashga ruxsat bermasligi mumkin (xabar o'chirilgan, juda eski yoki matn o'zgarmagan). Bunday holatda `TelegramBadRequest` tutiladi va foydalanuvchiga yangi xabar yuboriladi — handler ishdan chiqmaydi.

Darslar endi foto kartochka bilan ochiladi. Foto xabarda `edit_text()` ishlamaydi, shuning
uchun `safe_edit()` avval `message.photo` ni tekshiradi: foto bo'lsa eski xabarni o'chiradi
va yangi matnli xabar yuboradi. Shu bilan `Darslar`, `Test yechish` yoki boshqa bo'limga
o'tishda eski rasm va uning tugmalari chatda qolib ketmaydi.

## `progress_bar`

```text
progress_bar(1, 2) → "▓▓▓▓░░░░"
```

`target <= 0` bo'lsa bo'sh bar qaytariladi. Qiymat 1.0 dan oshmaydi.
