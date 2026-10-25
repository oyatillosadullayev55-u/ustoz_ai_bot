# `services` paketi — umumiy ko'rinish

**Yo'l:** [`services/`](../../../services)
**Vazifasi:** handlerlardan mustaqil biznes servislari: AI bilan aloqa, dars rasmlari va
kunlik eslatmalar.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| [`ai_service.py`](ai_service.md) | AI provayderi, fallback va prompt |
| [`lesson_media.py`](lesson_media.md) | Dars rasmlari, fayl nomlari va `file_id` kesh |
| [`reminders.py`](reminders.md) | Kunlik eslatma yuborish va scheduler |

## Qatlam chegarasi

- Handlerlar Telegram API va foydalanuvchi bilan ishlaydi.
- Servislar tashqi API (AI), statik fayllar (dars rasmlari) yoki fon vazifalari
  (eslatma) bilan ishlaydi.
- Ma'lumotlar bazasi bilan aloqa `database/` paketi orqali bo'ladi.

`services/__init__.py` faqat paket docstring'idan iborat.
