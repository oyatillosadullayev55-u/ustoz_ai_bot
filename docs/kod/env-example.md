# `.env.example` — sozlamalar namunasi

**Yo'l:** [`.env.example`](../../.env.example)
**Vazifasi:** yangi o'rnatishda `.env` faylini yaratish uchun xavfsiz namuna.

## Guruhlar

| Guruh | O'zgaruvchilar | Izoh |
|---|---|---|
| Bot | `BOT_TOKEN` | BotFather bergan token; namunada faqat test qiymati |
| Admin | `ADMIN_IDS` | Vergul bilan ajratilgan Telegram ID'lar |
| Baza | `DATABASE_PATH` | Standart `ustoz_ai.db` |
| Logging | `LOG_LEVEL` | `INFO` tavsiya etiladi |
| Til | `DEFAULT_LANGUAGE` | `uz`, `ru`, `en` |
| AI | `AI_ENABLED`, `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `AI_TIMEOUT`, `AI_DAILY_LIMIT`, `AI_MIN_INTERVAL`, `AI_MAX_TOKENS`, `AI_HISTORY_LIMIT` | Kalit bo'lmasa bot dars bazasidan javob beradi |
| Eslatma | `DAILY_REMINDERS_ENABLED`, `DAILY_REMINDER_HOUR` | Vaqt UTC+5 bo'yicha, standart 19:00 |
| Hosting | `PORT` | Ixtiyoriy; Render o'zi beradi, Docker Compose 8080 qiladi. Lokal ishda bo'sh |

## Foydalanish

```bash
cp .env.example .env
# .env ichida BOT_TOKEN va kerak bo'lsa AI_API_KEY ni to'ldiring
```

## Xavfsizlik

- `.env.example` ichida haqiqiy token yoki kalit bo'lmasligi kerak.
- `.env` fayli `.gitignore` orqali istisno qilingan.
- `ADMIN_IDS` bo'sh bo'lsa `/admin` faqat ID ko'rsatuvchi rad javobini beradi.
