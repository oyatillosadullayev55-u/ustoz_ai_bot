# `handlers/daily.py` — sovg'a, kunlik savol va missiyalar

**Yo'l:** [`handlers/daily.py`](../../../handlers/daily.py)
**Router:** `daily`
**Vazifasi:** `🎁 Sovg'a`, `❓ Kunlik savol` va `🎯 Missiyalar` bo'limlari, kunlik javob va missiya mukofotini olish.

## Handlerlar

| Handler | Trigger | Vazifasi |
|---|---|---|
| `gift_entry` | `🎁 Sovg'a` matni | Kunlik sovg'ani ochadi yoki allaqachon olinganini aytadi |
| `daily_question_entry` | `❓ Kunlik savol` matni | Kunlik savol yoki bugungi natijani ko'rsatadi |
| `daily_question_callback` | `daily:question` | Sovg'a/missiya ekranidan savolni ochadi |
| `answer_daily_question` | `daily:answer:<qid>:<0-3>` | Javobni tekshiradi, saqlaydi va XP beradi |
| `missions_entry` | `🎯 Missiyalar` matni | Haftalik missiyalar ekranini ochadi |
| `missions_callback` | `missions:show` | Missiyalar ekranini qayta chizadi |
| `claim_mission` | `mission:claim:<kod>` | Bajarilgan missiya mukofotini beradi |

## Sovg'a oqimi

1. `has_daily_gift` tekshiriladi; olingan bo'lsa seriya bilan eslatma yuboriladi.
2. Aks holda `gift_amount()` miqdori `reward(..., once_key=f"gift:{day}")` orqali
   beriladi. `once_key` takroriy XP ni to'sadi.
3. Bugungi sana sovg'a kunlari to'plamiga qo'shilib, seriya hisoblanadi.
4. Xabar `🎁` reaksiyasi va yutuq bildirishnomalari bilan yuboriladi.

## Kunlik savol oqimi

1. `get_daily_question(local_today())` savolni tanlaydi.
2. Javob bo'lsa, natija (tanlangan va to'g'ri variant, izoh, seriya) qayta
   ko'rsatiladi.
3. Javob bo'lmasa, 4 variantli inline klaviatura yuboriladi.
4. `answer_daily_question` callback'ni 4 qismga ajratadi, variant indeksini
   0–3 oralig'ida tekshiradi va savol ID'si bugungi savolga mos kelishini
   tasdiqlaydi.
5. `save_daily_answer` takroriy javobni to'sadi. Muvaffaqiyatli javob uchun
   `DAILY_CORRECT_XP` (10) yoki `DAILY_WRONG_XP` (2) beriladi.
6. Natija `safe_edit` bilan yangilanadi, `✅`/`❌` reaksiyasi qo'yiladi va
   **📖 Darsni ochish** / **🎯 Missiyalar** / **🏠 Bosh menyu** tugmalari chiqadi.

## Missiyalar oqimi

- `get_mission_states` har bir missiya progressi va holatini beradi.
- Ekranda hafta oralig'i, `YYYY-Www` kaliti va progress barlar ko'rsatiladi:
  ⏳ bajarilmagan, 🎁 mukofotga tayyor, ✅ olingan.
- `claim_mission` missiya kodini `MISSION_MAP` dan topadi, `done` va `claimed`
  holatini tekshiradi, so'ng `reward(..., once_key=mission_once_key(code))`
  chaqiradi.
- Mukofot olingach ekran qayta chiziladi va tugma yo'qoladi.

## Xavfsizlik

- Har bir handler `require_user` yoki `require_user_callback` bilan boshlanadi.
- Savol matni, variantlar va izoh `html.escape` qilinadi.
- Callback ma'lumotlari `int` ga aylantirishda `try/except ValueError` bilan
  tekshiriladi; noto'g'ri yoki eskirgan savol rad etiladi.
- Barcha XP mukofotlari `once_key` bilan idempotent.
