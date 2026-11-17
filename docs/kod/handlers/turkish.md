# `handlers/turkish.py` — ovozli talaffuz mashqlari

**Yo'l:** [`handlers/turkish.py`](../../../handlers/turkish.py)
**Vazifasi:** turk tili darslaridagi gaplarni ovozli xabar qilib yuborish va
talaffuz ekranini boshqarish.

## Callback formatlari

| Callback | Vazifasi |
|---|---|
| `turk:audio:<lesson_id>` | Talaffuz ekranini ochadi: 8 ta gap + tugmalar |
| `turk:say:<lesson_id>:<index>` | Bitta gapni ovozli xabar qilib yuboradi |
| `turk:all:<lesson_id>` | Darsning barcha gaplarini ketma-ket yuboradi |

## Oqim

1. `turk:audio` — `get_lesson()` orqali darsni tekshiradi:
   - dars mavjud bo'lmasa yoki `subject_code != "turkish"` bo'lsa ogohlantirish;
   - `get_turkish_phrases()` gaplarni oladi;
   - `safe_edit()` bilan matnli ekran va `get_turkish_audio_keyboard()` chiqaradi;
   - xabarga 🎧 reaksiya qo'yiladi.
2. `turk:say` — gap indeksini tekshiradi, `ChatAction.RECORD_VOICE` yuboradi va
   `bot.send_voice()` orqali OGG faylni yuboradi. Caption'da gap, tarjima va
   talaffuz maslahati bo'ladi.
3. `turk:all` — foydalanuvchi uchun `asyncio.Lock` oladi (ikki marta bosilsa
   «Avvalgi tinglash tugashini kuting»), barcha gaplarni 0.5 soniya tanaffus bilan
   yuboradi. Bu Telegram flood limitidan himoya qiladi.

## Ovoz manbasi

`services/turkish_audio.py::get_audio_source()` avval keshlangan Telegram
`file_id` ni, keyin `assets/turkish_audio/lesson_<id>_<n>.ogg` faylini qaytaradi.
Fayl topilmasa handler ogohlantirish beradi va logga dars/gap ID sini yozadi.

## Xavfsizlik va limitlar

- Har bir handler `require_user_callback()` bilan ro'yxatdan o'tishni tekshiradi.
- Callback'dan kelgan ID'lar `int` ga aylantiriladi va bazadan qayta tekshiriladi.
- Matn va tarjima `html.escape()` qilinadi.
- Ovoz caption'i Telegram limitidan ancha kichik (3 qator).
- `_locks` faqat jarayon xotirasida; foydalanuvchi ma'lumoti saqlanmaydi.

## Bog'liq hujjatlar

- [`database/turkish.py`](../database/turkish.md)
- [`services/turkish_audio.py`](../services/turkish_audio.md)
- [`keyboards/inline_buttons.py`](../keyboards/inline_buttons.md)
- [`handlers/lessons.py`](lessons.md)
