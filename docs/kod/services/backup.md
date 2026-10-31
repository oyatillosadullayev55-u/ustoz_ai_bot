# `services/backup.py` — baza zaxirasi va CSV eksport

**Yo'l:** [`services/backup.py`](../../../services/backup.py)
**Vazifasi:** ishlab turgan SQLite bazadan izchil nusxa olish va foydalanuvchilar
jadvalini CSV qilib berish. Admin panelning `💾 Baza zaxirasi` va `📤 CSV eksport`
tugmalari shu servisdan foydalanadi.

## `create_backup_copy()`

- `sqlite3.Connection.backup()` API'si ishlatiladi — bu WAL rejimida ham izchil
  nusxa beradi (faylni `copy` qilish WAL yozuvlarini o'tkazib yuborishi mumkin).
- Nusxa alohida oqimda (`asyncio.to_thread`) bajariladi, event loop bloklanmaydi.
- Fayl nomi: `ustoz_ai_YYYYMMDD_HHMMSS.db`.
- Papka: `BACKUP_DIR` muhit o'zgaruvchisi yoki loyihadagi `backups/`.

## `create_export_csv()`

1. `database.admin.get_export_rows()` orqali foydalanuvchilar yig'masi olinadi.
2. Quyidagi ustunlar yoziladi:

```text
telegram_id, full_name, username, level, xp, notifications_enabled,
created_at, last_seen_at, lessons_completed, quizzes, average_score, best_score
```

3. `utf-8-sig` kodlash ishlatiladi — Excel'da o'zbek harflari to'g'ri ochiladi.
4. `(fayl yo'li, qatorlar soni)` qaytariladi; handler faylni yuborgach o'chiradi.

## `cleanup_old_backups(keep=5)`

Har yangi zaxira yaratilgandan keyin chaqiriladi: eng eski `.db` nusxalar
o'chiriladi, oxirgi 5 tasi qoladi. Shu bilan doimiy disk to'lib ketmaydi.

## Xatolar

Fayl tizimi xatolari (`OSError`) va `sqlite3.Error` handlerda ushlanadi; foydalanuvchiga
qisqa "❌ ... yaratib bo'lmadi" xabari yuboriladi, batafsil sabab logga yoziladi.
