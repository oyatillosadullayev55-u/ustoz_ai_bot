# `tests/test_offline.py` — ma'lumotlar qatlami testi

**Yo'l:** [`tests/test_offline.py`](../../../tests/test_offline.py)
**Vazifasi:** Telegramga ulanmasdan baza sxemasi, kontent, foydalanuvchilar, maqsadlar, test natijalari, AI zaxirasi va admin statistikasini tekshirish.

## Ishga tushirish

```bash
.venv\Scripts\python.exe tests\test_offline.py
```

Muvaffaqiyatli yakun: `OFFLINE_TESTS_OK`.

## Izolyatsiya

Fayl import qilinishidan oldin:

- `DATABASE_PATH` vaqtinchalik papkadagi test bazasiga o'rnatiladi;
- `BOT_TOKEN` soxta qiymat bilan beriladi;
- `ADMIN_IDS=999000001`;
- `AI_ENABLED=false`, `AI_API_KEY=""`;
- `get_settings.cache_clear()` chaqiriladi.

Test oxirida `TemporaryDirectory.cleanup()` baza faylini o'chiradi. Haqiqiy `.env`, token yoki foydalanuvchi bazasiga tegmaydi.

## Qamrov

| Bo'lim | Tekshiruvlar |
|---|---|
| Sxema | `init_db()` ikki marta chaqirilganda idempotentligi |
| Kontent | 10 fan, 60 savol, har bir savolda 4 variant, `correct_option` 0–3 |
| Savollar | `get_questions_by_ids` va bo'sh ro'yxat |
| Vaqt | `seconds_until_local_time` bugun/ertaga hisobi |
| Qidiruv | `search_lessons("fotosintez nima")` natijasi |
| Foydalanuvchi | Ro'yxatdan o'tish, dublikat yaratmaslik |
| Maqsad | Standart 1/1, yangilash, pending reminders |
| Dars | Tugatish idempotentligi va kunlik hisob |
| Test | 80% natija, statistika, so'nggi natija |
| Faollik | Streak va faol kunlar |
| Chat | Tarix tartibi, kunlik limit |
| AI | AI o'chirilganda dars bazasidan javob |
| Sozlamalar | Bildirishnoma `0/1` va eslatma ro'yxati |
| Admin | Jami foydalanuvchi, testlar, savollar, o'rtacha foiz |

## Nima uchun skript ko'rinishida

Loyiha uchun qo'shimcha test freymvorki talab qilinmaydi. Har bir tekshiruv `check(shart, xabar)` orqali bajariladi va birinchi xatoda `AssertionError` bilan to'xtaydi. Bu CI'da ham, lokal PyCharm'da ham bir xil ishlaydi.
