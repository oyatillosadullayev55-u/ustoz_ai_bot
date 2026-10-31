# `services` paketi — umumiy ko'rinish

**Yo'l:** [`services/`](../../../services)
**Vazifasi:** handlerlardan mustaqil biznes servislari: AI bilan aloqa, dars rasmlari,
kunlik eslatmalar va health-check serveri.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| [`ai_service.py`](ai_service.md) | AI provayderi, dars konteksti, fallback va prompt |
| [`lesson_media.py`](lesson_media.md) | Dars rasmlari, fayl nomlari va `file_id` kesh |
| [`reminders.py`](reminders.md) | Kunlik eslatma yuborish va scheduler |
| [`gamification.py`](gamification.md) | XP qiymatlari, darajalar, yutuqlar va reyting |
| [`backup.py`](backup.md) | Baza zaxirasi va CSV eksport |
| [`health_server.py`](health_server.md) | Render uchun HTTP health-check serveri |

## Qatlam chegarasi

- Handlerlar Telegram API va foydalanuvchi bilan ishlaydi.
- Servislar tashqi API (AI), statik fayllar (dars rasmlari), fon vazifalari
  (eslatma) yoki hosting uchun HTTP endpoint (health) bilan ishlaydi.
- Ma'lumotlar bazasi bilan aloqa `database/` paketi orqali bo'ladi.

`services/__init__.py` faqat paket docstring'idan iborat.

