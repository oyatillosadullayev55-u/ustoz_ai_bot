# `handlers/start.py` — ro'yxatdan o'tish

**Yo'l:** [`handlers/start.py`](../../../handlers/start.py)
**Vazifasi:** `/start` buyrug'i va ikki bosqichli ro'yxatdan o'tish (ism → daraja).

## FSM holatlari

```text
RegistrationStates.waiting_name → RegistrationStates.waiting_level
```

## Oqim

1. `/start` kelganda `state.clear()` qilinadi.
2. Foydalanuvchi bazada bo'lsa: `update_last_seen()` va salomlashuv + bosh menyu.
3. Yangi foydalanuvchi bo'lsa: ism so'raladi va `waiting_name` holati yoqiladi.
4. Ism `process_name` da tekshiriladi:
   - 2–50 belgi;
   - `/` bilan boshlanmaydi;
   - asosiy menyu tugma matnlariga teng emas.
5. Ism state'ga saqlanadi va daraja tugmalari yuboriladi.
6. `level:*` callback kelganda daraja tekshiriladi, foydalanuvchi yaratiladi yoki daraja yangilanadi.
7. `state.clear()`, tasdiq xabari va bosh menyu yuboriladi.

## Muhim jihatlar

- `create_user` idempotent; foydalanuvchi allaqachon bo'lsa dublikat yaratilmaydi.
- Daraja `LEVELS` ro'yxatidan tekshiriladi.
- Til `settings.default_language` dan olinadi (standart `uz`).
- `edit_text` eskirgan xabar uchun `TelegramBadRequest` bersa, bu holat xato hisoblanmaydi (foydalanuvchi tugmani tez ikki marta bosgan bo'lishi mumkin).

## Callback ma'lumotlari

`level:beginner`, `level:intermediate`, `level:advanced`.

## Harakat effekti

`start_handler()` boshida `react(message, "👋")` chaqiriladi — foydalanuvchi xabariga
salomlashish reaksiyasi qo'yiladi. Reaksiya yuborilmasa (guruh, eski mijoz) xato
yutiladi va oqim davom etadi.

