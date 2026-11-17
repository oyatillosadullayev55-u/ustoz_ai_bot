# `scripts/generate_turkish_audio.py` — talaffuz ovozlarini yaratish

**Yo'l:** [`scripts/generate_turkish_audio.py`](../../../scripts/generate_turkish_audio.py)
**Vazifasi:** `content/turkish_courses.json` dagi 64 ta gapni Microsoft Edge TTS
orqali MP3 qilib, keyin OGG/Opus formatiga aylantirib `assets/turkish_audio/`
papkasiga yozadi.

Bu **faqat ishlab chiqish** skripti. Ishlab chiqarish serverida `edge-tts` va
`ffmpeg` talab qilinmaydi — tayyor OGG fayllar repo bilan tarqatiladi.

## Ishlatish

```powershell
.venv\Scripts\python.exe scripts/generate_turkish_audio.py
.venv\Scripts\python.exe scripts/generate_turkish_audio.py --force
```

- `--force` bo'lmasa, mavjud fayllar o'tkazib yuboriladi.
- Har bir gap uchun skript progressni konsolga yozadi.

## Texnik tafsilotlar

| Parametr | Qiymat |
|---|---|
| Ovoz | `tr-TR-EmelNeural` (Microsoft, ayol ovoz) |
| Tezlik | `-8%` — o'rganuvchilar uchun sekinroq |
| MP3 | `edge-tts` ning standart `audio-24khz-48kbitrate-mono-mp3` formati |
| OGG | `imageio-ffmpeg` ichidagi ffmpeg, `libopus`, 48 kHz, mono, 48 kbps |

Vaqtinchalik MP3 `tempfile.TemporaryDirectory()` da yaratiladi va avtomatik
o'chiriladi. Natija fayl nomi `lesson_<dars_id>_<gap_tartibi>.ogg`.

## Bog'liqliklar (dev)

`requirements-dev.txt` ga qo'shilgan:

```text
edge-tts==7.3.1
imageio-ffmpeg==0.8.1
```

## Bog'liq hujjatlar

- [`database/turkish.py`](../database/turkish.md)
- [`services/turkish_audio.py`](../services/turkish_audio.md)
- [`content/turkish_courses.md`](../content/turkish_courses.md)
