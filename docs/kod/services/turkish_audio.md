# `services/turkish_audio.py` — talaffuz ovozi fayllari

**Yo'l:** [`services/turkish_audio.py`](../../../services/turkish_audio.py)
**Vazifasi:** turk tili gaplarining oldindan yaratilgan OGG fayllarini topish va
Telegram `file_id` keshini boshqarish.

## Funksiyalar

| Funksiya | Qaytaradi | Vazifasi |
|---|---|---|
| `audio_filename(lesson_id, phrase_index)` | `str` | `lesson_<id>_<n>.ogg` nomi |
| `get_audio_path(lesson_id, phrase_index)` | `Path \| None` | Fayl mavjudligini tekshiradi |
| `get_audio_source(lesson_id, phrase_index)` | `FSInputFile \| str \| None` | Keshdagi `file_id` yoki yuklash uchun fayl |
| `remember_audio_file_id(lesson_id, phrase_index, file_id)` | `None` | `file_id` ni jarayon xotirasida saqlaydi |
| `missing_audio_files(lesson_ids, phrase_count)` | `list[str]` | Testlar uchun yetishmayotgan fayllar |

## Doimiylar

| Doimiylik | Qiymat |
|---|---|
| `TURKISH_AUDIO_DIR` | `BASE_DIR / "assets" / "turkish_audio"` |

## Fayl nomlash

```text
assets/turkish_audio/lesson_1201_1.ogg
assets/turkish_audio/lesson_1208_8.ogg
```

Jami **64** ta fayl (8 dars × 8 gap), taxminan 850 KB. Fayllar
`scripts/generate_turkish_audio.py` bilan oldindan yaratiladi; serverda TTS yoki
ffmpeg talab qilinmaydi.

## Kesh

- `_file_ids` — `dict[tuple[int, int], str]`, faqat jarayon xotirasida.
- Birinchi muvaffaqiyatli `send_voice()` dan keyin handler `sent.voice.file_id` ni
  saqlaydi; keyingi yuborishlarda fayl qayta yuklanmaydi.
- Bot qayta ishga tushganda kesh tozalanadi.

## Xavfsizlik

Funksiyalar faqat `BASE_DIR` ichidagi qat'iy nomlangan fayllarni o'qiydi;
foydalanuvchi kiritgan qiymat yo'lga qo'shilmaydi.

## Bog'liq hujjatlar

- [`handlers/turkish.py`](../handlers/turkish.md)
- [`database/turkish.py`](../database/turkish.md)
- [`scripts/generate_turkish_audio.md`](../scripts/generate_turkish_audio.md)
