# `services/lesson_media.py` — dars rasmlari

**Yo'l:** [`services/lesson_media.py`](../../../services/lesson_media.py)
**Vazifasi:** dars kartochkalari uchun rasm fayllarini topish va Telegram `file_id`
keshini boshqarish.

## Funksiyalar

| Funksiya | Qaytaradi | Vazifasi |
|---|---|---|
| `get_lesson_image_path(lesson_id)` | `Path \| None` | `assets/lesson_images/lesson_<id>.jpg` (yoki `.jpeg`, `.png`) faylini qidiradi |
| `get_lesson_photo(lesson_id)` | `FSInputFile \| str \| None` | Keshlangan `file_id` yoki yuklash uchun `FSInputFile` qaytaradi |
| `remember_lesson_file_id(lesson_id, file_id)` | `None` | Birinchi yuborilgandan keyin `file_id` ni jarayon xotirasida saqlaydi |

## Doimiylar

| Doimiylik | Qiymat |
|---|---|
| `LESSON_IMAGES_DIR` | `BASE_DIR / "assets" / "lesson_images"` |
| `IMAGE_SUFFIXES` | `(".jpg", ".jpeg", ".png")` |

## Fayl nomlash

```text
assets/lesson_images/lesson_101.jpg
assets/lesson_images/lesson_502.jpg
assets/lesson_images/lesson_1002.jpg
```

Nom darsning `lessons.id` qiymatiga bog'langan. Bu kontent JSON'idagi ID bilan bir xil.
Rasm topilmasa, handler matnli kartochkaga avtomatik qaytadi.

## Kesh

- `_file_ids` — `dict[int, str]`, faqat jarayon xotirasida.
- Birinchi `answer_photo()` dan keyin handler `sent.photo[-1].file_id` ni saqlaydi.
- Keyingi ochishlarda fayl qayta yuklanmaydi.
- Bot qayta ishga tushganda kesh tozalanadi; birinchi foydalanuvchi rasmni yana bir
  marta yuklaydi.
- Keshda foydalanuvchi ma'lumoti yo'q — faqat dars ID si va Telegram `file_id` si.

## Xavfsizlik

Funksiyalar faqat `BASE_DIR` ichidagi qat'iy nomlangan fayllarni o'qiydi; foydalanuvchi
kiritgan qiymat yo'lga qo'shilmaydi. Fayl mavjudligi `Path.is_file()` bilan tekshiriladi.
Telegram API xatosi handlerda tutiladi va logga faqat dars ID si yoziladi.

## Bog'liq hujjatlar

- [Dars kartochkalari dizayni](../../DARS_DIZAYNI.md)
- [`handlers/lessons.py`](../handlers/lessons.md)
- [`handlers/common.py`](../handlers/common.md)
