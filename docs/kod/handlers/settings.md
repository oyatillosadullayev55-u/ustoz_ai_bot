# `handlers/settings.py` — foydalanuvchi sozlamalari

**Yo'l:** [`handlers/settings.py`](../../../handlers/settings.py)
**Vazifasi:** bilim darajasini va bildirishnomalarni boshqarish.

## Ekran

- Ism;
- joriy daraja;
- bildirishnoma holati;
- til (hozircha faqat o'zbekcha);
- AI Ustoz holati (ulangan model yoki mahalliy dars bazasi).

## Callback'lar

| Callback | Vazifasi |
|---|---|
| `settings:level:<code>` | Darajani `beginner` / `intermediate` / `advanced` ga o'zgartiradi |
| `settings:notify` | Bildirishnomalarni yoqadi yoki o'chiradi |

## Oqim

1. `⚙️ Sozlamalar` tugmasi joriy holatni ko'rsatadi.
2. Daraja o'zgarsa `update_level()` chaqiriladi, so'ng foydalanuvchi bazadan qayta o'qiladi.
3. Bildirishnoma tugmasi `update_notifications()` bilan `0/1` qiymatni almashtiradi.
4. Ekran `safe_edit` bilan yangilanadi va `callback.answer` orqali tasdiq beriladi.

## Ta'sir doirasi

- Daraja AI javoblarining uslubiga ta'sir qiladi (`LEVEL_NAMES`).
- Bildirishnoma o'chirilganda:
  - admin broadcast'lari yuborilmaydi;
  - kunlik eslatmalar yuborilmaydi.

## Xavfsizlik

Daraja qiymati `LEVELS` ro'yxatidan tekshiriladi. Foydalanuvchi faqat o'z yozuvini o'zgartiradi.
