# `tests/test_offline.py` — ma'lumotlar qatlami testi

**Yo'l:** [`tests/test_offline.py`](../../../tests/test_offline.py)
**Vazifasi:** Telegramga ulanmasdan baza sxemasi, migratsiya, kontent, foydalanuvchilar,
maqsadlar, test natijalari, AI zaxirasi, health server va admin statistikasini tekshirish.

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
- `AI_ENABLED=false`, `AI_API_KEY=""`, `AI_MIN_INTERVAL=0`;
- `get_settings.cache_clear()` chaqiriladi.

`check_config_cleaning()` test boshida tokenni vaqtincha qo'shtirnoq ichida va
`BOT_TOKEN=` prefiksi bilan beradi, noto'g'ri formatni tekshiradi, so'ng haqiqiy
test qiymatlarini qaytaradi.

Test oxirida `TemporaryDirectory.cleanup()` baza faylini o'chiradi. Haqiqiy `.env`, token yoki foydalanuvchi bazasiga tegmaydi.

## Qamrov

| Bo'lim | Tekshiruvlar |
|---|---|
| Konfiguratsiya | `BOT_TOKEN` va `ADMIN_IDS` qo'shtirnoqlardan tozalanadi; `BOT_TOKEN=` prefiksi olib tashlanadi; noto'g'ri token rad etiladi |
| Sxema | `init_db()` ikki marta chaqirilganda idempotentligi |
| Migratsiya | Eski `lessons` jadvaliga `summary`, `key_points`, `level`, `duration_min` qo'shilishi |
| Kontent | 8 fan, 35 dars, 140 savol; har bir darsda 4 savol |
| Dars sifati | Har bir darsda 80+ belgili `summary`, aynan 3 ta `key_points`, to'g'ri `level`, 1–120 `duration_min`, 900+ belgili `content` |
| Savollar | `get_questions_by_ids` va bo'sh ro'yxat |
| Health server | `PORT` bo'lmasa server ochilmaydi; `PORT` berilganda `/health` 200 va `status=ok` qaytaradi |
| Vaqt | `seconds_until_local_time` bugun/ertaga hisobi |
| Qidiruv | `search_lessons("fotosintez nima")` natijasi |
| Foydalanuvchi | Ro'yxatdan o'tish, dublikat yaratmaslik |
| Maqsad | Standart 1/1, yangilash, pending reminders |
| Dars | Tugatish idempotentligi va kunlik hisob |
| Test | 80% natija, statistika, so'nggi natija |
| Faollik | Streak va faol kunlar |
| Chat | Tarix tartibi, kunlik limit |
| AI | AI o'chirilganda dars bazasidan javob; dars konteksti bilan `Shu darsdan tushuntirish` javobi |
| Sozlamalar | Bildirishnoma `0/1` va eslatma ro'yxati |
| Admin | Jami foydalanuvchi, testlar, 140 savol, o'rtacha foiz |

## Nima uchun skript ko'rinishida

Loyiha uchun qo'shimcha test freymvorki talab qilinmaydi. Har bir tekshiruv `check(shart, xabar)` orqali bajariladi va birinchi xatoda `AssertionError` bilan to'xtaydi. Bu CI'da ham, lokal PyCharm'da ham bir xil ishlaydi.
