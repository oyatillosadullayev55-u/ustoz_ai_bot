# `services/reminders.py` — kunlik eslatmalar

**Yo'l:** [`services/reminders.py`](../../../services/reminders.py)
**Vazifasi:** har kuni belgilangan vaqtda rejasi bajarilmagan foydalanuvchilarga eslatma yuborish.

## Funksiyalar

| Funksiya | Vazifasi |
|---|---|
| `format_reminder(...)` | Ism, maqsad va bajarilgan sonlardan HTML matn yasaydi |
| `_send_reminder(bot, chat_id, text)` | Xabar yuboradi; `TelegramRetryAfter` bo'lsa bir marta qayta urinadi |
| `send_due_reminders(bot, goal_date=None)` | Bugungi ro'yxat bo'yicha yuboradi, `(sent, failed)` qaytaradi |
| `run_daily_reminders(bot)` | Cheksiz tsikl: keyingi vaqtgacha uxlaydi, keyin yuboradi |

## Scheduler mantiqi

1. `get_settings()` dan `DAILY_REMINDER_HOUR` olinadi (UTC+5).
2. `seconds_until_local_time(hour)` keyingi belgilangan vaqtgacha soniyalarni hisoblaydi.
3. Logga keyingi eslatma vaqti yoziladi.
4. `asyncio.sleep(delay)` dan keyin `send_due_reminders()` chaqiriladi.
5. `CancelledError` qayta ko'tariladi (bot to'xtaganda vazifa to'g'ri bekor bo'ladi); boshqa xatolar logga yoziladi va tsikl davom etadi.

## Kim eslatma oladi

`get_pending_reminders()` sharti:

- bugun `daily_goals` yozuvi bor;
- `notifications_enabled = 1`;
- dars yoki test maqsadi bajarilmagan.

Bu spamni kamaytiradi va bildirishnoma sozlamasini hurmat qiladi.

## Matn tarkibi

```text
Kunlik eslatma
Salom, <ism>!
Bugungi maqsadingiz hali bajarilmagan:
Darslar: 1/2
Testlar: 0/1
Qoldi: 1 dars, 1 test.
Davom etish uchun «Kunlik reja» bo'limini oching.
```

Nolga teng maqsad qatorlari ko'rsatilmaydi. Ism `html.escape` qilinadi.

## Yuk va xavfsizlik

- Har bir xabar orasida `SEND_DELAY_SECONDS = 0.05` tanaffus.
- `TelegramAPIError` bo'lsa `failed` oshadi; logda faqat foydalanuvchi ID'si bor.
- Xabar matni yoki shaxsiy ma'lumot logga yozilmaydi.
- Scheduler faqat `DAILY_REMINDERS_ENABLED=true` bo'lganda `bot.py` tomonidan ishga tushiriladi.
