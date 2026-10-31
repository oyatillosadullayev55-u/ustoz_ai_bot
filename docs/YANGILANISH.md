# UstozAI — 2026-10-31 yangilanishi

Bu hujjat loyihaga qo'shilgan yangi imkoniyatlar, ularni qanday ishlatish va
tekshiruv natijalarini jamlaydi.

**Commit:** `176b6d3` — *feat: gamifikatsiya, sevimlilar, zaxira va test UX yaxshilandi*

## Qisqa mazmun

| Yo'nalish | Natija |
| --- | --- |
| Gamifikatsiya | XP, 6 daraja, 12 yutuq, haftalik TOP-10 reyting |
| Sevimlilar | Darslarni yulduzcha bilan saqlash va «Sevimlilarim» ekrani |
| Fan progressi | Har bir fan tugmasida tugatilgan/jami dars soni va umumiy progress |
| Test UX | Fan bo'yicha eng yaxshi natija, rekord xabari, XP mukofoti |
| AI UX | Javob ostida mavzuga mos 2 tagacha dars havolasi |
| Zaxira | Admin uchun `/backup` va `/export` (CSV) |
| Baza | 3 ta yangi jadval, `users.xp` ustuni, idempotent migratsiya |

## 1. Gamifikatsiya

XP har bir foydalanuvchi uchun `users.xp` da saqlanadi, har bir harakat esa
`xp_log` jurnaliga yoziladi. Bir martalik mukofotlar `once_key` bilan himoyalangan,
shuning uchun sahifani qayta ochish XP ni ikki marta qo'shmaydi.

| Hodisa | XP |
| --- | --- |
| Dars tugatish | +20 |
| Test yakuni | 5 + 2 × to'g'ri javob |
| 100% natija bonusi | +10 |
| Kunlik maqsad bajarildi | +15 |
| Yangi yutuq | +15 |
| AI Ustozga savol | +1 |

### Darajalar

| Emoji | Daraja | Minimal XP |
| --- | --- | --- |
| 🌱 | Yangi boshlovchi | 0 |
| 📗 | O'quvchi | 100 |
| 📘 | Bilimdon | 300 |
| 🎓 | Tajribali | 700 |
| 🏅 | Ustoz | 1500 |
| 👑 | Afsona | 3000 |

### Yutuqlar (12 ta)

Birinchi qadam, Izlanuvchi (5 dars), Bilimdon (15 dars), Marafon (35 dars),
Birinchi sinov, Test ustasi (10 test), Mukammal natija (100%), Uch kun (streak 3),
Bir hafta (streak 7), Kolleksioner (5 sevimli), AI hamkor (10 savol), Maqsadli
(5 kunlik maqsad).

Yangi yutuq ochilganda bot darhol tabriklaydi va `+15 XP` beradi.

### Haftalik reyting

So'nggi 7 kunda to'plangan XP bo'yicha TOP-10 ko'rsatiladi. Ishlatilgan ismlar
maxfiylik uchun qisqartiriladi, joriy foydalanuvchining o'rni alohida chiqadi.

**Qayerda ko'rinadi:** «📊 Mening natijalarim» → daraja va XP yuqorida,
«🏆 Yutuqlarim» va «📈 Haftalik reyting» tugmalari ostida.

## 2. Sevimlilar va fan progressi

- Fanlar ro'yxatida umumiy progress va har bir fan tugmasida `tugatilgan/jami`
  ko'rsatiladi (masalan `2/5`).
- Dars kartochkasidagi **⭐ Sevimlilarga qo'shish** tugmasi darsni saqlaydi yoki
  olib tashlaydi. Holat kartochka qayta chizilganda ko'rinadi.
- «📊 Mening natijalarim → ⭐ Sevimlilarim» saqlangan darslarni ro'yxat qiladi;
  tugma bosilsa, dars darhol ochiladi.

## 3. Test va AI UX

- Test yakunida fan bo'yicha oldingi eng yaxshi natija bilan solishtiriladi;
  rekord yangilansa, alohida nishonlanadi.
- Natija ekranida olingan XP ko'rsatiladi.
- AI Ustoz javobi ostida mavzuga mos 2 tagacha dars tugmasi chiqadi va darsni
  darhol ochish mumkin.
- AI javoblari HTML sifatida xavfsiz ekranlanadi; uzun javob qisqartiriladi.

## 4. Zaxira va CSV eksport

### `/backup`

Admin uchun. Bot SQLite `backup()` API orqali izchil nusxa yaratadi (WAL rejimida
ham), `.db` fayl sifatida Telegram'ga yuboradi. So'nggi 5 ta nusxa `BACKUP_DIR`
papkasida qoladi, eskilari o'chiriladi.

### `/export`

Admin uchun. Foydalanuvchilar jadvalini `utf-8-sig` CSV qilib yuboradi: ism, XP,
tugatilgan darslar, testlar, o'rtacha va eng yaxshi natija. Fayl Excel yoki Google
Sheets'da ochiladi va yuborilgach serverdan o'chiriladi.

### Tiklash

1. Botni to'xtating.
2. Zaxira `.db` faylini `.env` dagi `DATABASE_PATH` manziliga qo'ying.
3. Botni qayta ishga tushiring.

Zaxira faylida shaxsiy ma'lumot bor — uni ochiq joyda saqlamang.

### Render bepul tarifi

Bepul tarifda doimiy disk yo'q. Variantlar:

- muntazam `/backup` olib, faylni kompyuterda saqlash;
- Render persistent disk ulash: `DATABASE_PATH=/var/data/ustoz_ai.db`,
  `BACKUP_DIR=/var/data/backups`;
- Oracle Cloud Always Free + `docker compose` ga o'tish.

Batafsil: [SERVERGA_JOYLASH.md](SERVERGA_JOYLASH.md), 1.4.1-bo'lim.

## 5. Ma'lumotlar bazasi

Yangi jadvallar:

| Jadval | Vazifasi |
| --- | --- |
| `xp_log` | XP jurnali; `once_key` qismiy unikal indeks bilan |
| `achievements` | Ochilgan yutuqlar (PK: user_id, code) |
| `favorites` | Sevimli darslar (PK: user_id, lesson_id) |

`users` jadvaliga `xp` ustuni qo'shildi. Sxema idempotent: `CREATE TABLE IF NOT
EXISTS`, eski bazaga ustun `ALTER TABLE` bilan qo'shiladi. Foydalanuvchi
o'chirilsa, XP, yutuqlar va sevimlilar ham kaskad bilan o'chadi.

## 6. Tekshiruv natijalari

| Tekshiruv | Natija |
| --- | --- |
| `ruff check .` | All checks passed |
| `tests/test_offline.py` | `OFFLINE_TESTS_OK` |
| `tests/test_handlers_offline.py` | `HANDLER_FLOW_OK` |

Testlar vaqtinchalik bazadan foydalanadi; zaxira fayllari ham vaqtinchalik
papkaga yoziladi va testdan keyin o'chiriladi.

## 7. Ishga tushirish holati

- Kod GitHub `main` branch'ga yuklangan: `176b6d3`.
- Render avtomatik deploy qiladi; `/health` manzili yangi commit bilan
  `{"status": "ok"}` qaytaradi.
- Telegramda bot: `@ustoz_ai_2026_bot`.
- **Lokal `python bot.py` ni Render ishlab turganda ishga tushirmang** — Telegram
  polling rejimida bitta nusxa ishlashi kerak, aks holda
  `Conflict: terminated by other getUpdates request` xatosi chiqadi.

### Yangi environment o'zgaruvchisi

| Kalit | Ma'nosi | Standart |
| --- | --- | --- |
| `BACKUP_DIR` | Zaxira va CSV fayllari papkasi | `backups/` |

## 8. Keyingi qadamlar

- Doimiy baza (Render persistent disk yoki PostgreSQL) ga o'tish.
- Yutuqlar va reyting uchun qo'shimcha filtrlash.
- Test natijalari bo'yicha mavzular kesimida tahlil.
- Qidiruvni FTS bilan tezlashtirish.
