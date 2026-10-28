# `tests/test_handlers_offline.py` — handler oqimlari testi

**Yo'l:** [`tests/test_handlers_offline.py`](../../../tests/test_handlers_offline.py)
**Vazifasi:** aiogram routerlari, FSM va callback oqimlarini Telegram tarmog'iga chiqmasdan tekshirish.

## Ishga tushirish

```bash
.venv\Scripts\python.exe tests\test_handlers_offline.py
```

Muvaffaqiyatli yakun: `HANDLER_FLOW_OK`.

## Qanday ishlaydi

- `FakeSession` — `Bot` sessiyasining o'rnini bosadi; yuborilgan `SendMessage`, `SendPhoto`, `EditMessageText`, `EditMessageCaption` kabi metodlarni ro'yxatga yozadi va `True` qaytaradi.
- `Message(...).as_(bot)` va `CallbackQuery(...).as_(bot)` bilan sintetik yangilanishlar yaratiladi.
- `Dispatcher.feed_update()` orqali handlerlar haqiqiy aiogram mantiqi bo'yicha ishlaydi.
- `dispatcher.errors.register(record_error)` barcha handler xatolarini yig'adi; test oxirida ro'yxat bo'sh bo'lishi shart.
- `last_inline_markup()` yordamchisi yuborilgan oxirgi inline klaviaturani qaytaradi, shu
  bilan tugatilgan darsning batafsil ekrani qayta yaratilishi mumkin.

## Qamrov

1. Ro'yxatdan o'tish: `/start` → ism → daraja callback → baza va menyu.
2. Rasmli darslar:
   - 35 ta rasm mavjudligi va caption limiti;
   - `SendPhoto` va kartochkadagi `Asosiy fikrlar`;
   - `lesson:read` va `lesson:ask` tugmalari;
   - `lesson:view:502` orqali keyingi darsga o'tish va `lesson:view:501` bilan qaytish;
   - batafsil ekranda maqsad va mini mashq matni, `Kartochkaga qaytish` tugmasi;
   - batafsil ekrandan darsni tugatish: holat yangilanadi, `Darsni tugatdim` tugmasi
     olib tashlanadi va kunlik reja oshadi;
   - kartochkaga qaytganda ham tugatilgan holat saqlanadi;
   - foto kartochkadan orqaga qaytish.
3. Qidiruv: `/qidiruv fotosintez`, natijadan dars ochish, bo'sh va natijasiz so'rov.
4. Test: 5 savol, birinchi javob ataylab xato, qolganlari to'g'ri:
   - natija `4/5` va `80%`;
   - xatolar tahlili alohida xabarda;
   - tanlangan va to'g'ri variant ko'rsatilgan.
5. Statistika, kunlik reja, maqsadni 2/2 ga o'zgartirish.
6. Sozlamalar: bildirishnoma va daraja.
7. AI Ustoz: AI o'chirilganda dars bazasidan javob, tarix bazaga yozilishi; `lesson:ask:501`
   orqali dars kontekstida `Shu darsdan tushuntirish` javobi.
8. Admin: panel, statistika (140 savol), broadcast tasdiqlash va yuborilgan xabar.
9. Kunlik eslatma: `send_due_reminders()` bitta foydalanuvchiga "Kunlik eslatma" yuborishi.

## Izolyatsiya

Test vaqtinchalik baza va soxta token bilan ishlaydi. Haqiqiy bot tokeni, `.env` yoki tarmoq ishlatilmaydi. Shuning uchun testni bot ishlab turgan paytda ham xavfsiz ishga tushirish mumkin.
