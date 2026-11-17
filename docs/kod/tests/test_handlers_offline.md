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
   - 43 ta rasm mavjudligi va caption limiti;
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
8. Admin: panel, statistika (172 savol), broadcast tasdiqlash va yuborilgan xabar.
9. Kunlik eslatma: `send_due_reminders()` bitta foydalanuvchiga "Kunlik eslatma" yuborishi.
10. Kunlik bo'limlar:
    - menyuda `🎁 Sovg'a`, `❓ Kunlik savol`, `🎯 Missiyalar` tugmalari;
    - sovg'a 5–25 XP beradi, ikkinchi urganda XP qo'shilmaydi va seriya 1 kun;
    - kunlik savol 4 variant bilan chiqadi, to'g'ri javob `+10 XP`, takroriy javob
      qabul qilinmaydi va baza o'zgarmaydi;
    - haftalik faollik to'ldirilgach missiyalar `3/3`, `2/2` ko'rsatadi, mukofot
      `+30 XP` beradi va takroriy olish XP qo'shmaydi.
11. Anatomiya:
    - Biologiya ro'yxatida `anatomy:menu` tugmasi;
    - menyu banner rasmi va uch vaqtli rejim (`anatomy:start:10/20/50`);
    - savolda `1/10`, vaqt hisoblagichi, A–D matni va 4 ta javob tugmasi;
    - 10 savoldan keyin `9/10` va `90%`, XP va xatolar tahlili;
    - natija `subject_id=900` yashirin faniga saqlanadi va kunlik reja oshadi;
    - eski javob tugmasi "yakunlangan" ogohlantirishini qaytaradi;
    - `ANATOMY_MODES[10]` vaqtincha qisqartirilib, taymer javob berilgan 1 savolni
      baholashi tekshiriladi.
12. Turk tili va ovoz:
    - fanlar ro'yxatida `turkish` fani va 8 ta dars ko'rinadi;
    - `lesson:view:1201` kartochkasida `🎧 Ovozli talaffuz` tugmasi bor;
    - `turk:audio:1201` ekranda 8 ta gap tugmasi va «Hammasini tinglash» chiqadi;
    - `turk:say:1201:1` `RECORD_VOICE` harakati va `SendVoice` yuboradi, izohda
      turkcha gap bo'ladi, `file_id` keshlanadi;
    - `turk:all:1201` ketma-ket 8 ta ovoz yuboradi (`PLAYBACK_GAP_SECONDS = 0`).

## Izolyatsiya

Test vaqtinchalik baza va soxta token bilan ishlaydi. Haqiqiy bot tokeni, `.env` yoki tarmoq ishlatilmaydi. Shuning uchun testni bot ishlab turgan paytda ham xavfsiz ishga tushirish mumkin.
