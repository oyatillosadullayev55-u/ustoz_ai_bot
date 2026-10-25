# `handlers/menu.py` — menyu va zaxira handlerlar

**Yo'l:** [`handlers/menu.py`](../../../handlers/menu.py)
**Vazifasi:** `/menu`, `/help`, `/id`, bosh menyuga qaytish va tanilmagan yangilanishlarga javob berish.

## Buyruqlar

| Buyruq | Vazifasi |
|---|---|
| `/menu` | Holatni tozalaydi va bosh menyuni ochadi |
| `/help` | Bot imkoniyatlari va buyruqlar ro'yxati |
| `/id` | Foydalanuvchining Telegram ID raqamini ko'rsatadi |

`/help` matnida `/qidiruv` buyrug'i ham ko'rsatilgan. `/id` natijasidagi ID'ni admin `.env` faylidagi `ADMIN_IDS` ga qo'shishi mumkin.

## Callback'lar

- `menu:home` — inline xabar tugmalarini olib tashlaydi va bosh menyuni yuboradi.
- `level:*` — ro'yxatdan o'tgan foydalanuvchi eski daraja tugmasini bossa, "allaqachon ro'yxatdan o'tgansiz" ogohlantirishi.
- Boshqa barcha callback'lar — "amal eskirgan" javobi.

## Zaxira handlerlar

- `handle_unknown_text` — ro'yxatdan o'tgan foydalanuvchi tushunarsiz matn yozsa, AI Ustoz yoki menyuni taklif qiladi.
- `handle_unsupported_content` — rasm, video, sticker kabi matn bo'lmagan xabarlarga javob beradi.

## Router tartibi

Bu router `bot.py` da eng oxirida ulanadi. Shu sababli uning keng filtrlari (`F.text`, umumiy callback) faqat boshqa routerlar mos handler topmagan holatda ishlaydi.
