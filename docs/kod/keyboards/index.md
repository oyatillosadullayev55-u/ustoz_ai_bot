# `keyboards` paketi — umumiy ko'rinish

**Yo'l:** [`keyboards/`](../../../keyboards)
**Vazifasi:** Telegram klaviaturalarini markazlashtirish. Handlerlar `ReplyKeyboardMarkup` yoki `InlineKeyboardMarkup` ni to'g'ridan-to'g'ri yasamaydi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| [`main_menu.py`](main_menu.md) | Bosh menyu va AI rejimi reply klaviaturalari |
| [`inline_buttons.py`](inline_buttons.md) | Barcha inline klaviaturalar |

## Nima uchun alohida paket

- Tugma matnlari va callback formatlari bir joyda saqlanadi.
- Handlerlar faqat biznes mantiqqa e'tibor beradi.
- Tugma matni o'zgarsa, bir nechta fayl emas, bitta fayl tahrirlanadi.

`keyboards/__init__.py` faqat paket docstring'idan iborat.
